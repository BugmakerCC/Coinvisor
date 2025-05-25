import React, { useState } from "react";
import { Form, Input, Button, message, Modal } from "antd";
import { Link, history } from "umi";
import { login } from "@/services/chat";
import { setToken } from "@/services/request";
import styles from "./index.less";

export const layout = false;

const LoginPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [forgotVisible, setForgotVisible] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      const { access_token: token } = await login(values);
      setToken(token);
      message.success("登录成功");
      history.push("/chat");
    } catch (error: any) {
      const code = error?.response?.data?.errorCode;
      const msg = error?.response?.data?.errorMessage || "登录失败";

      if (code === "EMAIL_NOT_FOUND") {
        form.setFields([{ name: "email", errors: [msg] }]);
      } else if (code === "INVALID_CREDENTIALS") {
        form.setFields([{ name: "password", errors: [msg] }]);
      } else {
        message.error(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleForgot = async () => {
    if (!forgotEmail) {
      message.warning("请输入邮箱后再提交");
      return;
    }
    try {
      message.success("如果邮箱存在，重置链接已发送");
      setForgotVisible(false);
    } catch {
      message.error("发送失败，请稍后重试");
    }
  };

  return (
   <div className={styles.pageWrapper}>
        <div className={styles.logo}>
          <img
            className={styles.logoImg}
            src="https://mdn.alipayobjects.com/huamei_iwk9zp/afts/img/A*eco6RrQhxbMAAAAAAAAAAAAADgCCAQ/original"
            alt="链 AI"
            draggable={false}
          />
          <span className={styles.logoText}>链 AI</span>
        </div>

      <div className={styles.contentWrapper}>
        <div className={styles.loginContainer}>
          <Form
            form={form}
            name="login"
            onFinish={onFinish}
            layout="vertical"
          >
            <Form.Item
              name="email"
              label="邮箱"
              rules={[
                { type: "email", message: "请输入有效的邮箱地址" },
                { required: true, message: "请输入邮箱地址" },
              ]}
            >
              <Input placeholder="请输入邮箱地址" />
            </Form.Item>

            <Form.Item
              name="password"
              label="密码"
              rules={[{ required: true, message: "请输入密码" }]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
            <Form.Item className={styles.forgotRow} colon={false} wrapperCol={{ span: 24 }}>
              <a onClick={() => setForgotVisible(true)}>忘记密码？</a>
            </Form.Item>
            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
              >
                登录
              </Button>
            </Form.Item>

            <div className={styles.footer}>
              <Link to="/register">没有账号？立即注册</Link>
            </div>
          </Form>
        </div>
      </div>

      <Modal
        title="重置密码"
        visible={forgotVisible}
        onOk={handleForgot}
        onCancel={() => setForgotVisible(false)}
        okText="发送重置链接"
      >
        <Input
          value={forgotEmail}
          onChange={(e) => setForgotEmail(e.target.value)}
          placeholder="请输入您的注册邮箱"
        />
      </Modal>
    </div>
  );
};

export default LoginPage;
