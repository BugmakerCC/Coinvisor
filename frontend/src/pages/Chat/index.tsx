import {
  Bubble,
  Conversations,
  Prompts,
  Sender,
  Welcome,
  useXAgent,
  useXChat,
} from "@ant-design/x";
import { Button, Space, Image } from "antd";
import type { BubbleProps } from "@ant-design/x";
import { useEffect, useMemo, useState, useCallback } from "react";
// import { getUserInfo } from "@/services/chat";
import { getToken, autoLogin } from "@/services/request";
import "./index.less";

import { FireOutlined, PlusOutlined, ReadOutlined } from "@ant-design/icons";
import type { GetProp } from "antd";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const defaultConversationsItems = [
  {
    key: "0",
    label: "什么是区块链?",
  },
];

const senderPromptsItems: GetProp<typeof Prompts, "items"> = [
  {
    key: "1",
    description: "共识算法",
    icon: <FireOutlined style={{ color: "#FF4D4F" }} />,
  },
  {
    key: "2",
    description: "零知识证明",
    icon: <ReadOutlined style={{ color: "#1890FF" }} />,
  },
];

const roles: GetProp<typeof Bubble.List, "roles"> = {
  ai: {
    placement: "start",
    typing: { step: 20, interval: 10 },
  },
  local: {
    placement: "end",
    variant: "outlined",
  },
};

const Independent = () => {
  // ==================== State ====================

  const [content, setContent] = useState("");
  const [conversationsItems, setConversationsItems] = useState(
    defaultConversationsItems
  );
  const [activeKey, setActiveKey] = useState(defaultConversationsItems[0].key);

  const [agent] = useXAgent({
    request: async ({ message }, { onUpdate, onSuccess }) => {
      let token = getToken();

      // 如果 token 为空或过期，自动重新登录
      if (!token) {
        try {
          token = await autoLogin();
        } catch (loginError) {
          console.error("自动登录失败:", loginError);
          throw loginError;
        }
      }

      try {
        const response = await fetch("http://116.62.42.206:5000/api/v1/chat", {
          method: "POST",
          // @ts-ignore
          headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
            authorization: token,
          },
          body: JSON.stringify({ message }),
          cache: "no-store",
          credentials: "same-origin",
        });

        if (!response.ok)
          throw new Error(`HTTP error! status: ${response.status}`);
        if (!response.body) throw new Error("No response body");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let accumulatedContent = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            onSuccess(accumulatedContent);
            break;
          }

          buffer += decoder.decode(value, { stream: true });

          // 处理完整事件（以\n\n分隔）
          while (buffer.includes("\n\n")) {
            const splitIndex = buffer.indexOf("\n\n");
            const eventData = buffer.slice(0, splitIndex);
            buffer = buffer.slice(splitIndex + 2);

            // 处理事件数据
            const lines = eventData.split("\n");
            let content = "";
            for (const line of lines) {
              if (line.startsWith("data: ")) {
                content += line.slice(6);
              } else {
                content += "\n" + line;
              }
            }

            if (content) {
              accumulatedContent += content; // 累积内容
              onUpdate(accumulatedContent); // 更新累积内容
            }
          }
        }
      } catch (error) {
        console.error("请求失败:", error);
      }
    },
  });

  const { onRequest, messages, setMessages } = useXChat({
    agent,
  });

  useEffect(() => {
    if (activeKey !== undefined) {
      setMessages([]);
    }
    // 组件初始化时自动调用getUserInfo接口，如果token过期，request.ts中的自动登录机制会处理
    // getUserInfo()
    // .then((res: any) => {
    //   console.log("用户信息获取成功:", res);
    // })
    // .catch((err: any) => {
    //   console.log("获取用户信息失败:", err);
    // });
  }, [activeKey]);

  // ==================== Event ====================
  const onSubmit = (nextContent: string) => {
    if (!nextContent) return;
    onRequest(nextContent);
    setContent("");
  };

  const onPromptsItemClick: GetProp<typeof Prompts, "onItemClick"> = (info) => {
    onRequest(info.data.description as string);
  };

  const onAddConversation = () => {
    setConversationsItems([
      ...conversationsItems,
      {
        key: `${conversationsItems.length}`,
        label: `新对话 ${conversationsItems.length}`,
      },
    ]);
    setActiveKey(`${conversationsItems.length}`);
  };

  const onConversationClick: GetProp<typeof Conversations, "onActiveChange"> = (
    key
  ) => {
    setActiveKey(key);
  };

  // ==================== Nodes ====================
  const placeholderNode = (
    <Space direction="vertical" size={16} className="placeholder">
      <Welcome
        variant="borderless"
        title="👋 我是链智能助手，很高兴见到你！"
        description="这是一段描述……"
      />
    </Space>
  );

  const ImageComponent = useCallback(
    ({ src, alt }: { src?: string; alt?: string }) => {
      const [loaded, setLoaded] = useState(false);

      return (
        <Image
          src={src}
          alt={alt}
          style={{
            opacity: loaded ? 1 : 0,
          }}
          onLoad={() => setLoaded(true)}
        />
      );
    },
    []
  );

  type ParagraphType = "thinking" | "tool" | "analysis" | "response";

  const parseContent = (content: string) => {
    const patterns: {
      regex: RegExp;
      type: ParagraphType;
    }[] = [
      { regex: /^🤔\s*正在思考:\s*/, type: "thinking" },
      { regex: /^🔧\s*正在调用.*?:\s*/, type: "tool" },
      { regex: /^😎\s*正在分析.*?:\s*/, type: "analysis" },
      { regex: /^🤖\s*正在回复:\s*/, type: "response" },
    ];

    const paragraphs: { type: ParagraphType; content: string }[] = [];
    let remaining = content;
    let currentType: ParagraphType | null = null;
    let buffer = "";

    const flushBuffer = () => {
      if (currentType && buffer.trim()) {
        paragraphs.push({ type: currentType, content: buffer });
        buffer = "";
      }
    };

    while (remaining.length > 0) {
      let matched = false;

      for (const { regex, type } of patterns) {
        const match = regex.exec(remaining);
        if (match) {
          flushBuffer();
          currentType = type;

          buffer += match[0] + "\n\n"; // 保留类型标识符

          remaining = remaining.slice(match[0].length);
          matched = true;
          break;
        }
      }

      if (!matched) {
        const nextChar = remaining[0];
        if (currentType === "response") {
          buffer += nextChar;
        } else {
          buffer += nextChar.replace(/\s/g, ""); // 去除空格
        }

        remaining = remaining.slice(1);
      }
    }

    flushBuffer();
    return paragraphs;
  };

  // ==================== 样式渲染逻辑 ====================
  const getParagraphStyle = (type: ParagraphType) => {
    const baseStyle = {
      margin: "8px 0",
      padding: "0px 12px",
    };

    switch (type) {
      case "thinking":
        return {
          ...baseStyle,
          borderLeft: "3px solid #ddd",
          color: "#666",
        };
      case "tool":
        return {
          ...baseStyle,
          borderLeft: "3px solid #1890ff",
          color: "#666",
        };
      case "analysis":
        return {
          ...baseStyle,
          borderLeft: "3px solid #52c41a",
          color: "#666",
        };
      case "response":
        return {
          ...baseStyle,
          color: "#000",
        };
      default:
        return baseStyle;
    }
  };

  // ==================== Markdown渲染 ====================
  const renderMarkdown: BubbleProps["messageRender"] = useCallback(
    (content: string) => {
      const paragraphs = parseContent(content);

      return (
        <div className="message-paragraphs">
          {paragraphs.map((paragraph, index) => (
            <div key={index} style={getParagraphStyle(paragraph.type)}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  img: ImageComponent,
                  code: ({ node, className, children, ...props }) => (
                    <code
                      className={className}
                      style={{
                        background: "#f5f5f5",
                        padding: "2px 4px",
                        borderRadius: 4,
                      }}
                      {...props}
                    >
                      {children}
                    </code>
                  ),
                }}
              >
                {paragraph.content}
              </ReactMarkdown>
            </div>
          ))}
        </div>
      );
    },
    [ImageComponent]
  );

  // ==================== 消息列表优化 ====================
  const memoizedItems = useMemo(() => {
    return messages.map(({ id, message, status }) => ({
      key: id,
      role: status === "local" ? "local" : "ai",
      content: message,
      // typing: status !== "local" ? { step: 10, interval: 10 } : false,
      messageRender:
        status === "local" ? (content: string) => content : renderMarkdown,
    }));
  }, [messages, renderMarkdown]);

  // 对话气泡
  const items: GetProp<typeof Bubble.List, "items"> = memoizedItems;

  const logoNode = (
    <div className="logo">
      <img
        src="https://mdn.alipayobjects.com/huamei_iwk9zp/afts/img/A*eco6RrQhxbMAAAAAAAAAAAAADgCCAQ/original"
        draggable={false}
        alt="logo"
      />
      <span>链 AI</span>
    </div>
  );

  // ==================== Render =================
  return (
    <div className="layout">
      <div className="menu">
        {/* 🌟 Logo */}
        {logoNode}
        {/* 🌟 添加会话 */}
        <Button
          onClick={onAddConversation}
          type="link"
          className="addBtn"
          icon={<PlusOutlined />}
        >
          新对话
        </Button>
        {/* 🌟 会话管理 */}
        <Conversations
          items={conversationsItems}
          className="conversations"
          activeKey={activeKey}
          onActiveChange={onConversationClick}
        />
      </div>
      <div className="chat">
        {/* 🌟 消息列表 */}
        <Bubble.List
          items={
            items.length > 0
              ? items
              : [{ content: placeholderNode, variant: "borderless" }]
          }
          roles={roles}
          className="messages"
        />
        {/* 🌟 提示词 */}
        <Prompts items={senderPromptsItems} onItemClick={onPromptsItemClick} />
        {/* 🌟 输入框 */}
        <Sender
          value={content}
          onSubmit={onSubmit}
          onChange={setContent}
          loading={agent.isRequesting()}
          className="sender"
        />
      </div>
    </div>
  );
};

export default Independent;