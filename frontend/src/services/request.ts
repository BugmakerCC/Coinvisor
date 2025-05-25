// request.ts
import { request as umiRequest } from "umi";
import { handleProxy } from "@/utils";

// token 管理
let cachedToken: string | null = null;
let isAutoLoginInProgress = false;

// 用户接口
export interface UserInfo {
  userId: number;
  username: string;
  email: string;
  createdAt: number;
}

export interface Session {
  sessionId: string;
  createdAt: number;
}

export interface PaginatedSessions {
  list: Session[];
  current: number;
  pageSize: number;
  total: number;
}

export interface ChatHistoryItem {
  historyId: string;
  role: string;
  content: string;
  toolCalls: null | any; // 根据实际工具调用结构定义
  createdAt: number;
}

export interface PaginatedChatHistory {
  list: ChatHistoryItem[];
  current: number;
  pageSize: number;
  total: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  errorCode: string;
  errorMessage: string;
}

/**
 * 获取最新的 token
 * @returns 当前的 token
 */
export function getToken(): string | null {
  if (!cachedToken) {
    cachedToken = localStorage.getItem("token");
  }
  return cachedToken;
}

/**
 * 设置 token 并缓存
 * @param token 新的 token
 */
export function setToken(token: string): void {
  cachedToken = token;
  localStorage.setItem("token", token);
}

/**
 * 清除 token
 */
export function clearToken(): void {
  cachedToken = null;
  localStorage.removeItem("token");
}

/**
 * 自动登录
 * @returns Promise<string> token
 */
export async function autoLogin() {
  if (isAutoLoginInProgress) {
    // 防止重复调用登录接口
    return new Promise((resolve) => {
      const checkToken = () => {
        const token = getToken();
        if (token) {
          resolve(token);
        } else {
          setTimeout(checkToken, 300);
        }
      };
      checkToken();
    });
  }

  isAutoLoginInProgress = true;
  try {
    // 调用登录接口（硬编码登录信息）
    const loginResponse = await umiRequest("/api/v1/login", {
      method: "POST",
      data: {
        email: "test@example.com",
        password: "123456",
      },
    });

    const { accessToken } = loginResponse.data;
    setToken(accessToken);
    isAutoLoginInProgress = false;
    return accessToken;
  } catch (error) {
    isAutoLoginInProgress = false;
    console.error("自动登录失败:", error);
    throw error;
  }
}
export async function request<T>(url: string, options: any){
  let token = getToken();

  // 如果是登录接口则直接请求
  if (url.includes("/api/v1/login")) {
    return umiRequest(url, options);
  }

  try {
    const response = await umiRequest<T>(
      url,
      Object.assign({}, options, {
        headers: {
          ...(options.headers || {}),
          Authorization: token,
        },
        responseType: options.responseType || "json", // 添加 responseType 选项
      })
    );

    return response.data;
  } catch (error: any) {
    // 处理 token 过期情况
    if (error.response && error.response.status === 401) {
      // token 过期，清除缓存
      clearToken();

      // 自动重新登录
      try {
        await autoLogin();
        // 获取新的 token
        token = getToken();

        // 使用新 token 重试原请求
        return umiRequest(
          url,
          Object.assign({}, options, {
            headers: {
              ...(options.headers || {}),
              Authorization: token,
            },
            responseType: options.responseType || "json",
          })
        );
      } catch (loginError) {
        console.error("重新登录失败:", loginError);
        throw loginError;
      }
    }

    throw error;
  }
}
