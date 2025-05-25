const { REACT_APP_ENV = "dev" } = process.env;

export default {
  plugins: ["@umijs/plugins/dist/request"],
  request: {
    dataField: "data",
  },
  define: {
    REACT_APP_ENV: REACT_APP_ENV || false,
    SERVER_ADDRESS: "http://47.111.15.36:5000",
  },
  proxy: {
    "/api": {
      target: "http://47.111.15.36:5000/",
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
      component: "./Login",
    },
    {
      path: "/docs",
      component: "./docs.tsx",
    },
    {
      path: "/chat",
      component: "./Chat",
    },
    {
      path: "/login",
      component: "./Login",
    },
    {
      path: "/register",
      component: "./Register",
    },
  ],
};
