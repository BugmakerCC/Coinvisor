const { REACT_APP_ENV = "dev" } = process.env;

export default {
  plugins: ["@umijs/plugins/dist/request"],
  request: {
    dataField: "data",
  },
  define: {
    REACT_APP_ENV: REACT_APP_ENV || false,
    SERVER_ADDRESS: "http://116.62.42.206:5000",
  },
  proxy: {
    "/api": {
      target: "http://116.62.42.206:5000/",
      changeOrigin: true,
    },
    "/sse": {
      target: "http://localhost:3000/",
      changeOrigin: true,
    },
  },
  routes: [
    {
      path: "/",
      component: "./Chat",
    },
    {
      path: "/docs",
      component: "./docs.tsx",
    },
  ],
};
