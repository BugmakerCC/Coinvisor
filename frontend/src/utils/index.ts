/* eslint-disable */

declare const REACT_APP_ENV: any;
declare const SERVER_ADDRESS: string;

/**
 * 判断使用本地 mock 或者是后端服务，local 有设置使用同源接口
 * @param url
 * @returns
 */
export const handleProxy = (url: string) => {
  const targetPrefix = REACT_APP_ENV ? "" : SERVER_ADDRESS;
  return targetPrefix + url;
};
