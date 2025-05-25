import { ApiResponse, UserInfo, ChatHistoryItem, PaginatedChatHistory, request } from "./request";

// 注册
export async function register(data?: any, options?: { [key: string]: any }) {
  return request("/api/v1/register", {
    method: "POST",
    data,
    ...(options || {}),
  });
}

// 登录
export async function login(data?: any, options?: { [key: string]: any }) {
  return request("/api/v1/login", {
    method: "POST",
    data,
    ...(options || {}),
  });
}

// 获取当前用户信息
export async function getUserInfo(
  options?: { [key: string]: any }
) : Promise<ApiResponse<UserInfo>> {
  const response = await request<ApiResponse<UserInfo>>("/api/v1/user/me", {
    method: "GET",
    ...(options || {}),
  });

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
