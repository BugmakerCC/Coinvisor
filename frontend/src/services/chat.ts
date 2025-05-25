import { request } from 'umi';
import { ApiResponse, UserInfo,getToken, setToken, clearToken, autoLogin, LoginResponse, RegisterResponse, Session, PaginatedSessions, ChatHistoryItem, PaginatedChatHistory} from "./request";


export async function register(payload: {
  username: string;
  email: string;
  password: string;
}): Promise<ApiResponse<RegisterResponse>> {
  try {
    const res = await request<ApiResponse<RegisterResponse>>('/api/v1/register', {
      method: 'POST',
      data: payload,
      adaptor: (responseData: any): any => {
      //console.log('▶ [register · raw responseData]:', responseData);
      return responseData;
    },
      // ...(options || {}),
    });
    //console.log('注册响应:', res);//console.log('▶ [register · after request]:', res);
    if (res.success) {
      return res;
    }
    throw {
      errorCode: res.errorCode,
      errorMessage: res.errorMessage,
    };
  } catch (err: any) {
    if (err.errorCode) throw err;
    throw {
      errorCode: 'UNKNOWN',
      errorMessage: err?.message || '注册失败',
    };
  }
}


export async function login(
  data: { email: string; password: string },
  options?: { [key: string]: any }
): Promise<ApiResponse<LoginResponse>> {
  const res = await request<ApiResponse<LoginResponse>>("/api/v1/login", {
    method: "POST",
    data,
    ...(options || {}),
  });

  if (!res.success) {
    const err = new Error(res.errorMessage || "登录失败");
    (err as any).response = { data: res };
    throw err;
  }

  return res;
}


// 获取当前用户信息
export async function getUserInfo(
  options?: { [key: string]: any }
) : Promise<ApiResponse<UserInfo>> {
  const response = await request<ApiResponse<UserInfo>>("/api/v1/user/me", {
    method: "GET",
  });
  console.log("获取的用户信息响应:", response);
  const apiResponse = response as ApiResponse<UserInfo>;
  return apiResponse;
}

// 会话获取
export async function getUserSessions(
  data?: any,
  options?: { [key: string]: any }
) {
  return request("/api/v1/userSessions", {
    method: "GET",
    params: data,
    ...(options || {}),
  });
}
// 历史会话
export async function getChatHistory(
  sessionId: string,
  pagination?: {
    current?: number;
    pagesize?: number;
  },
  options?: { [key: string]: any }
): Promise<PaginatedChatHistory> {
  const response = await request(`/api/v1/chatHistory/${sessionId}`, {
    method: "GET",
    params: {
      current: pagination?.current || 1,
      pageSize: pagination?.pagesize || 10,
      ...(options?.params || {})
    },
    ...(options || {})
  });

  return response as PaginatedChatHistory;
}
// 实时对话
export async function chat(data?: any, options?: { [key: string]: any }) {
  return request("/api/v1/chat", {
    method: "POST",
    data,
    responseType: "text",
    headers: {
      Accept: "text/event-stream",
    },
    ...(options || {}),
  });
}
