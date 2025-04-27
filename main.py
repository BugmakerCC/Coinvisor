from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import json
from pydantic import BaseModel, EmailStr, ValidationError, TypeAdapter
from passlib.hash import bcrypt
from openai import OpenAI, AsyncOpenAI
import json
from rank import get_top_gainers, get_hot_coins
from get_news import get_news
from get_events import get_events
from get_src import get_src
from get_bkg import get_bkg
from get_coin_info_market import get_coin_info_market
from get_chain_info import get_chain_info
from get_k_des import get_k_des
from sqlalchemy.orm import Session
from models import User, ChatHistory, ChatSession
from database import AsyncSessionLocal, SessionLocal
from uuid import UUID
from typing import Optional
from uuid import uuid4
from auth import create_access_token
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
from fastapi.middleware.cors import CORSMiddleware

client = AsyncOpenAI(
    api_key="your-api-key-here",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
# JWT配置
SECRET_KEY = "your-secret-key-here"  # 应使用环境变量存储
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 999999

tools = [
    # 工具1 获取当前加密货币币价涨幅排行榜
    {
        "type": "function",
        "function": {
            "name": "币价涨幅排行模块",
            "description": "当你想知道加密货币币价涨幅排行榜时非常有用，它可以帮助你更好地了解加密货币市场的情况。",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_n": {
                        "type": "int",
                        "description": "需要返回的币价涨幅排行榜上加密货币的数量，默认值为10。"
                    }
                },
                "required": [
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "热门加密货币模块",
            "description": "当你想知道热门加密货币（单日成交额大）的排行榜时非常有用，它可以帮助你更好地了解加密货币市场的情况。",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_n": {
                        "type": "int",
                        "description": "需要返回的排行榜上热门加密货币的数量，默认值为10。"
                    }
                },
                "required": [
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "实时新闻模块",
            "description": "当你想知道加密货币有关新闻时非常有用，一些新闻能够影响加密市场行情。",
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "历史事件模块",
            "description": "当你想知道某种加密货币自发行以来的历史事件时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "需要查询的加密货币的符号，例如：BTC、ETH、BNB等。"
                    }
                },
                "required": [
                    "symbol"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "合约分析模块",
            "description": "当你想获取某种加密货币在以太坊上的合约源代码时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "需要查询的加密货币的符号，例如：BTC、ETH、BNB等。"
                    }
                },
                "required": [
                    "symbol"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "加密货币背景信息模块",
            "description": "当你想知道某种加密货币的来源、背景信息时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "需要查询的加密货币的符号，例如：BTC、ETH、BNB等。"
                    }
                },
                "required": [
                    "symbol"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "实时市场信息模块",
            "description": "当你想知道某种加密货币的市场信息（包括最新价格、24小时涨跌幅等）非常有用，它可以帮助你更好地了解该加密货币的市场表现。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "需要查询的加密货币的符号，例如：BTC、ETH、BNB等。"
                    }
                },
                "required": [
                    "symbol"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "链上信息模块",
            "description": "当你想知道某种加密货币的链上信息时（该代币的合约地址、以及近期大额交易）非常有用，它可以帮助你更好地了解该加密货币近期的异常交易。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "需要查询的加密货币的符号，例如：BTC、ETH、BNB等。"
                    }
                },
                "required": [
                    "symbol"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "K线分析模块",
            "description": "当你想拿到某种加密货币的K线图时非常有用，它可以帮助你更好地了解该加密货币的市场表现。",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "需要查询的加密货币的符号，例如：BTC、ETH、BNB等。"
                    },
                    "days": {
                        "type": "int",
                        "description": "需要查询的加密货币的K线图的天数，默认为90。"
                    },
                    "interval": {
                        "type": "string",
                        "description": "需要查询的加密货币的K线图的时间间隔，默认为'1d'。"
                    }
                },
                "required": [
                    "symbol"
                ]
            }
        }
    },
]

# 配置 logger
logger = logging.getLogger("access_logger")
handler = logging.FileHandler("access.log", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI(debug=True)
app.mount("/charts", StaticFiles(directory="/charts"), name="charts")

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. 获取客户端 IP（优先 X-Forwarded-For）
        xff = request.headers.get("X-Forwarded-For")
        client_ip = xff.split(",")[0].strip() if xff else request.client.host

        # 2. 获取其他信息
        ts = datetime.utcnow().isoformat() + "Z"
        method = request.method
        path = request.url.path
        ua = request.headers.get("User-Agent", "-")

        # 3. 先执行业务，拿到响应
        response = await call_next(request)

        # 4. 记录日志
        logger.info(f"{ts} | {client_ip} | {method} {path} | {response.status_code} | {ua}")
        return response

# 安装中间件
app.add_middleware(AccessLogMiddleware)
# 允许所有源；生产环境可以改成具体域名列表
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],           # 允许所有 HTTP 方法
    allow_headers=["*"],           # 允许所有头部
)


async def get_db_async():
    async with AsyncSessionLocal() as session:
        yield session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 用户注册
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

@app.post("/api/v1/register")
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "data": {},
                "errorCode": "USERNAME_EXISTS",
                "errorMessage": "用户名已存在"
            }
        )
    
    if db.query(User).filter(User.email == data.email).first():
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "data": {},
                "errorCode": "EMAIL_EXISTS",
                "errorMessage": "邮箱已注册"
            }
        )

    # 加密密码
    hashed_password = bcrypt.hash(data.password)

    # 创建新用户
    new_user = User(
        username=data.username,
        email=data.email,
        password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "username": new_user.username,
                "email": new_user.email
            },
            "errorCode": "",
            "errorMessage": ""
        }
    )


# 生成JWT token的函数
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 登录响应
class LoginResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    expiresIn: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60

# 用户登录
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/v1/login")
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "data": {},
                "errorCode": "EMAIL_NOT_FOUND",
                "errorMessage": "邮箱不存在"
            }
        )

    if not bcrypt.verify(data.password, user.password):
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "data": {},
                "errorCode": "INVALID_CREDENTIALS",
                "errorMessage": "密码错误"
            }
        )

    access_token = create_access_token(
        {"sub": str(user.user_id)}  # 关键：将user_id编码到token中
    )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": LoginResponse(
                accessToken=access_token,
                expiresIn=ACCESS_TOKEN_EXPIRE_MINUTES*60
            ).dict(),
            "errorCode": "",
            "errorMessage": ""
        }
    )

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=True)
security = HTTPBearer()
async def get_current_user(
    token: str = Depends(API_KEY_HEADER),
    db: AsyncSession = Depends(get_db_async)  # 必须使用异步会话
) -> User:
    # 统一使用HTTPException抛出错误
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    # 异步查询数据库
    result = await db.execute(select(User).filter(User.user_id == int(user_id)))
    user = result.scalars().first()
    
    if not user:
        raise credentials_exception
    
    return user




# 获取用户信息
@app.get("/api/v1/user/me")
async def read_user(current_user: User = Depends(get_current_user)):
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "userId": current_user.user_id,
                "username": current_user.username,
                "email": current_user.email,
                "createdAt": int(current_user.created_at.timestamp() * 1000)
            },
            "errorCode": "",
            "errorMessage": ""
        }
    )


# 获取某个用户的所有session
@app.get("/api/v1/userSessions")
def get_user_sessions(
    current_user: User = Depends(get_current_user),
    current: int = 1,
    pageSize: int = 10,
    db: ChatSession = Depends(get_db)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.user_id  # 从token获取用户ID
    )
    total = sessions.count()
    sessions = sessions.offset((current-1)*pageSize).limit(pageSize).all()

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "list": [{
                    "sessionId": str(s.session_id),
                    "createdAt": int(s.created_at.timestamp() * 1000)
                } for s in sessions],
                "current": current,
                "pageSize": pageSize,
                "total": total
            },
            "errorCode": "",
            "errorMessage": ""
        }
    )



# 获取用户某个session的所有对话历史
@app.get("/api/v1/chatHistory/{sessionId}")
def get_chat_history_by_session(
    sessionId: UUID,
    current: int = 1,
    pageSize: int = 10,
    db: ChatSession = Depends(get_db)
):
    # 查询总记录数
    total = db.query(ChatHistory).filter(
        ChatHistory.session_id == sessionId
    ).count()

    if total == 0:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "errorCode": "CHAT_HISTORY_NOT_FOUND",
                "errorMessage": "该对话不存在或聊天记录已被删除"
            }
        )

    # 分页查询
    chat_histories = db.query(ChatHistory).filter(
        ChatHistory.session_id == sessionId
    ).order_by(ChatHistory.created_at.asc()) \
        .offset((current - 1) * pageSize) \
        .limit(pageSize) \
        .all()

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "list": [{
                    "historyId": str(history.history_id),
                    "role": history.role,
                    "content": history.content,
                    "toolCalls": history.tool_calls,
                    "createdAt": int(history.created_at.timestamp() * 1000)
                } for history in chat_histories],
                "current": current,
                "pageSize": pageSize,
                "total": total
            },
            "errorCode": "",
            "errorMessage": ""
        }
    )


# 用户实时对话
class ChatRequest(BaseModel):
    session_id: Optional[UUID] = None  # 允许为空，新对话时为 null
    message: str

@app.post("/api/v1/chat")
async def chat_endpoint(chat_request: ChatRequest, current_user: User = Depends(get_current_user), db: ChatSession = Depends(get_db_async)):
    return StreamingResponse(
        stream_chat_response(current_user.user_id, chat_request.session_id, chat_request.message, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream; charset=utf-8",
            "Connection": "keep-alive",
            # "Access-Control-Allow-Origin": "*",
            # "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            # "Access-Control-Allow-Headers": "*",
            # "Access-Control-Allow-Credentials": "true"
        }
    )

async def stream_chat_response(user_id: int, session_id: UUID, user_input: str, db: ChatSession):

    def execute_with_timeout(func, args, timeout=5):
        """带超时控制的函数执行器"""
        if func == get_bkg:
            timeout = 60  # 对于get_bkg函数，增加超时时间
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, **args)
            try:
                return future.result(timeout=timeout)
            except TimeoutError:
                # 超时后返回默认响应
                return {"error": "服务器繁忙，请求处理超时，请稍后再试"}

    # 0. 先判断用户是新建对话还是加载了历史对话
    if session_id is None:
        new_session = ChatSession(
            session_id=uuid4(),
            user_id=user_id
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        session_id = new_session.session_id

    # 1. 构建历史消息列表
    messages = [{
        "role": "system",
        "content": """
你是一个名叫CC-AI的全能AI助手，尤其擅长加密货币投资领域。你可以访问一系列强大的工具来帮助你获取币价、涨跌幅、K线走势、相关新闻、链上交易等信息。你需要根据用户的问题智能判断是否使用工具，调用工具是被鼓励的。
    """,
    }]

    while True:
        # 1) 拿到当前会话最新的一条消息
        result = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.history_id.desc())
            .limit(1)
        )
        last_msg: ChatHistory = result.scalars().first()
        if not last_msg:
            # 如果空了，就跳出
            break

        # 2) 检查条件：必须是 assistant 且 tool_calls 为空或者 null
        if last_msg.role == "assistant" and not last_msg.tool_calls:
            break

        # 3) 不符合就删掉这条
        await db.execute(
            delete(ChatHistory)
            .where(ChatHistory.history_id == last_msg.history_id)
        )
        await db.commit()

    history_result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at)
    )
    history = history_result.scalars().all()
    for chat in history:
        messages.append({"role": chat.role, "content": chat.content, "tool_calls": chat.tool_calls})

    # 2. 加入当前用户输入
    messages.append({"role": "user", "content": user_input})


    # 3. 保存用户消息到数据库
    user_message = ChatHistory(
        session_id=session_id,
        user_id=user_id,
        role="user",
        content=user_input
    )
    db.add(user_message)
    await db.commit()

    # 4. 生成回复
    while True:
        completion = await client.chat.completions.create(
            model="qwq-plus-latest",
            messages=messages,
            parallel_tool_calls=True,
            stream=True,
            tools=tools
        )

        reasoning_content = ""
        answer_content_without_tools = ""
        tool_info = []
        is_answering = False

        # 处理每个chunk并实时发送到前端
        # yield "="*20+"思考过程"+"="*20+"\n"
        if messages[-1]["role"] == "tool":
            # yield "data: 😎 正在分析工具执行结果: \n\n".encode('utf-8')
            yield "data: 😎 正在分析工具执行结果: \n\n"
            await asyncio.sleep(0)
        else:
            # yield "data: 🤔 正在思考: \n\n".encode('utf-8')
            yield "data: 🤔 正在思考: \n\n"
            await asyncio.sleep(0)
        async for chunk in completion:
            if not chunk.choices:
                continue  # 忽略没有choices的chunk
            delta = chunk.choices[0].delta

            # 处理思考过程
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                # yield "\n思考: \n"
                reasoning_content += delta.reasoning_content
                # yield f"\ndata: {delta.reasoning_content}\n\n".encode('utf-8')
                yield f"\ndata: {delta.reasoning_content}\n\n"
                await asyncio.sleep(0)
            
            # 处理回复内容
            elif delta.content is not None:
                if not is_answering:
                    is_answering = True
                    # yield "\n"+"="*20+"回复内容"+"="*20+"\n"
                    # yield "\ndata: 🤖 正在回复: \n\n".encode('utf-8')
                    yield "\ndata: 🤖 正在回复: \n\n"
                    await asyncio.sleep(0)
                answer_content_without_tools += delta.content
                # yield f"data: {delta.content}\n\n".encode('utf-8')
                yield f"data: {delta.content}\n\n"
                await asyncio.sleep(0)
                # yield delta.content
            
            # 处理工具调用信息（支持并行工具调用）
            if delta.tool_calls is not None:
                for tool_call in delta.tool_calls:
                    index = tool_call.index  # 工具调用索引，用于并行调用
                    
                    # 动态扩展工具信息存储列表
                    while len(tool_info) <= index:
                        tool_info.append({})
                    
                    # 收集工具调用ID（用于后续函数调用）
                    if tool_call.id:
                        tool_info[index]['id'] = tool_info[index].get('id', '') + tool_call.id
                    
                    # 收集函数名称（用于后续路由到具体函数）
                    if tool_call.function and tool_call.function.name:
                        tool_info[index]['name'] = tool_info[index].get('name', '') + tool_call.function.name
                    
                    # 收集函数参数（JSON字符串格式，需要后续解析）
                    if tool_call.function and tool_call.function.arguments:
                        tool_info[index]['arguments'] = tool_info[index].get('arguments', '') + tool_call.function.arguments

        messages.append({
            "role": "assistant",
            "content": answer_content_without_tools,
            "tool_calls": [
                {
                    "id": info["id"],
                    "function": {"name": info["name"], "arguments": info["arguments"]},
                    "type": "function"
                } for info in tool_info
            ] if tool_info else None
        })
        assistant_message_without_tools = ChatHistory(
            session_id=session_id,
            user_id=user_id,
            role="assistant",
            content=answer_content_without_tools,
            tool_calls = [
                {
                    "id": info["id"],
                    "function": {"name": info["name"], "arguments": info["arguments"]},
                    "type": "function"
                } for info in tool_info
            ] if tool_info else None
        )
        db.add(assistant_message_without_tools)
        await db.commit()
        

        # 处理工具调用并发送结果
        if tool_info:
            # yield "\n"+"="*20+"执行工具调用"+"="*20+"\n"
            for info in tool_info:
                # 发送工具调用信息
                # yield f"调用工具: {info['name']}\n\n参数: {info['arguments']}\n\n"
                # yield f"data: 🔧 正在调用{info['name']}...\n\n".encode('utf-8')
                yield f"data: 🔧 正在调用{info['name']}...\n\n"
                await asyncio.sleep(0)
                try:
                    # 执行对应的工具函数
                    args = json.loads(info["arguments"])
                    if info["name"] == "币价涨幅排行模块":
                        result = execute_with_timeout(get_top_gainers, args)
                    elif info["name"] == "热门加密货币模块":
                        result = execute_with_timeout(get_hot_coins, args)
                    elif info["name"] == "实时新闻模块":
                        result = execute_with_timeout(get_news, args)
                    elif info["name"] == "历史事件模块":
                        result = execute_with_timeout(get_events, args)
                    elif info["name"] == "合约分析模块":
                        result = execute_with_timeout(get_src, args)
                    elif info["name"] == "加密货币背景信息模块":
                        result = execute_with_timeout(get_bkg, args)
                    elif info["name"] == "实时市场信息模块":
                        result = execute_with_timeout(get_coin_info_market, args)
                    elif info["name"] == "链上信息模块":
                        result = execute_with_timeout(get_chain_info, args)
                    elif info["name"] == "K线分析模块":
                        result = execute_with_timeout(get_k_des, args)
                    
                    # 发送工具执行结果
                    # yield f"结果: {str(result)[:200]}...\n"  # 截断长文本
                    
                    # 将结果添加到消息历史
                    messages.append({
                        "role": "tool",
                        "content": str(result),
                        "tool_call_id": info["id"]
                    })

                    tool_message = ChatHistory(
                        session_id=session_id,
                        user_id=user_id,
                        role="tool",
                        content=str(result)
                    )
                    db.add(tool_message)
                    await db.commit()
                    
                except Exception as e:
                    error_msg = f"错误: {str(e)}"
                    yield f"{error_msg}\n"
                    messages.append({
                        "role": "tool",
                        "content": error_msg,
                        "tool_call_id": info["id"]
                    })
                    tool_message = ChatHistory(
                        session_id=session_id,
                        user_id=user_id,
                        role="tool",
                        content=error_msg
                    )
                    db.add(tool_message)
                    await db.commit()
        else:
            break
    # yield "data: [DONE]".encode('utf-8')
    yield "data: [DONE]"
    await asyncio.sleep(0)