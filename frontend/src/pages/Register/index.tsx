import React, { useState } from "react";
import { Form, Input, Button, message } from "antd";
import { Link, history } from "umi";
import { register ,getUserInfo} from "@/services/chat";
import styles from "./index.less";

const RegisterPage: React.FC = () => {
  const [form] = Form.useForm();
  const [fieldErrors, setFieldErrors] = useState<{
    username?: string;
    email?: string;
  }>({});

  const [loading, setLoading] = useState(false);
  interface RegisterFormValues {
  username: string;
  email: string;
  password: string;
}
  const onFinish = async (values: RegisterFormValues): Promise<void> => {
  setFieldErrors({});
  setLoading(true);
  try {
    const response =await register(values);
    //console.log('注册成功响应:', response);
    const { username, email } = response.data;
    console.log("注册成功，用户ID:", username, "邮箱:", email);
    message.success("注册成功");
    history.push("/login");
  } catch (err: any) {
    // ② 根据后端的 errorCode 分发到 fieldErrors
    if (err.errorCode === 'USERNAME_EXISTS') {
      setFieldErrors({ username: err.errorMessage });
    } else if (err.errorCode === 'EMAIL_EXISTS') {
      setFieldErrors({ email: err.errorMessage });
    } else {
      message.error(err.errorMessage);
    }
  } finally {
    setLoading(false);
  }
};


  return (
      <div className={styles.pageWrapper}>
        <div className={styles.logoWrapper}>
          <img
            className={styles.logoImg}
            src="https://mdn.alipayobjects.com/huamei_iwk9zp/afts/img/A*eco6RrQhxbMAAAAAAAAAAAAADgCCAQ/original"
            alt="链 AI"
            draggable={false}
          />
          <span className={styles.logoText}>链 AI</span>
        </div>

      <div className={styles.contentWrapper}>
    <div className={styles.registerContainer}>
      <Form
        form={form}
        name="register"
        onFinish={onFinish}
        scrollToFirstError
        layout="vertical"
      >
        {/* 用户名 */}
        <Form.Item
          label="用户名"
          name="username"
          validateStatus={fieldErrors.username ? 'error' : undefined}
          help={fieldErrors.username}
          rules={[{ required: true, message: '请输入用户名' }]}
        >
        <Input placeholder="请输入用户名" />
        </Form.Item>

        <Form.Item
        label="邮箱"
        name="email"
        validateStatus={fieldErrors.email ? 'error' : undefined}
        help={fieldErrors.email}
        rules={[{ required: true, message: '请输入邮箱' }, { type: 'email', message: '请输入正确的邮箱' }]}
        >
        <Input placeholder="请输入邮箱地址" />
        </Form.Item>


        {/* 密码 */}
        <Form.Item
          label="密码"
          name="password"
          rules={[{ required: true, message: "请输入密码" }]}
        >
          <Input.Password placeholder="请输入密码" />
        </Form.Item>

        <Form.Item>
          <Button
              type="primary"
              htmlType="submit"
              loading={loading}>
            注册
          </Button>
        </Form.Item>

        <div className={styles.footer}>
          <Link to="/login">已有账号？直接登录</Link>
        </div>
      </Form>
    </div>
      </div>
    </div>
  );
};

export default RegisterPage;
