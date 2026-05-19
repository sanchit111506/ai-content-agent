import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { Sparkles, User } from "lucide-react";

import CodeBlock from "./CodeBlock";
import FilePreview from "./FilePreview";
import MessageActions from "./MessageActions";

/**
 * MessageBubble
 * - User: right-aligned dark-gray bubble with user avatar
 * - Assistant: left-aligned, no bubble (ChatGPT-style), markdown rendered
 * - Math: handled by remark-math + rehype-katex (no regex hacks!)
 * - Code: handled by CodeBlock with copy button
 */
export default function MessageBubble({ message, isUser, onReload }) {
  const { content, files } = message;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex gap-4 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {/* AVATAR */}
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center">
            <User size={16} className="text-white" />
          </div>
        ) : (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <Sparkles size={16} className="text-white" />
          </div>
        )}
      </div>

      {/* CONTENT */}
      <div className={`flex flex-col min-w-0 ${isUser ? "items-end" : "items-start"} max-w-[85%]`}>
        {/* File chips (above message text) */}
        {files && files.length > 0 && (
          <FilePreview files={files} />
        )}

        {/* Message body */}
        {isUser ? (
          // USER — dark bubble, plain text (preserve line breaks)
          <div className="bg-[#2a2a2a] border border-zinc-800 rounded-2xl px-4 py-2.5 text-[15px] text-zinc-100 whitespace-pre-wrap break-words">
            {content}
          </div>
        ) : (
          // ASSISTANT — no bubble, full markdown
          <div className="markdown-body w-full">
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[rehypeKatex]}
              components={{
                code({ inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || "");
                  const value = String(children).replace(/\n$/, "");

                  if (!inline && match) {
                    return <CodeBlock language={match[1]} value={value} />;
                  }
                  return (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
                // Open links in new tab
                a({ children, ...props }) {
                  return (
                    <a
                      target="_blank"
                      rel="noopener noreferrer"
                      {...props}
                    >
                      {children}
                    </a>
                  );
                },
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        )}

        {/* ACTIONS — only for assistant messages */}
        {!isUser && content && (
          <MessageActions content={content} onReload={onReload} />
        )}
      </div>
    </motion.div>
  );
}
