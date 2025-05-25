import { request } from 'umi';


export interface RegisterResult {
  username: string;
  email: string;
}

export interface LoginResult {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export async function register(payload: {
  username: string;
  email: string;
  password: string;
}): Promise<RegisterResult> {
  try {
    const res = await request('/api/v1/register', {
      method: 'POST',
      data: payload,
      adaptor: (responseData: any): any => {
      //console.log('▶ [register · raw responseData]:', responseData);
      return responseData;
    },
      // ...(options || {}),
    });
    //console.log('▶ [register · after request]:', res);
    if (res.success) {
      return res.data;
    }
    throw {
      errorCode: res.errorCode,
      errorMessage: res.errorMessage,
    };
  } catch (err: any) {
    //console.log('▶ [register · catch]:', err);
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
): Promise<LoginResult> {
  const res: {
    success: boolean;
    data: LoginResult;
    errorCode: string;
    errorMessage: string;
  } = await request("/api/v1/login", {
    method: "POST",
    data,
    ...(options || {}),
  });

  if (!res.success) {
    const err = new Error(res.errorMessage || "登录失败");
    ;(err as any).response = { data: res };
    throw err;
  }

  return res.data;
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
