import { request } from "./request";

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
  data?: any,
  options?: { [key: string]: any }
) {
  return request("/api/v1/user/me", {
    method: "GET",
    params: data,
    ...(options || {}),
  });
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
