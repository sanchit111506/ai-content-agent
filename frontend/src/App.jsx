import { useState, useRef, useEffect, useCallback } from "react";
import toast from "react-hot-toast";

import API from "./services/api";
import useLocalStorage from "./hooks/useLocalStorage";

import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import MessageBubble from "./components/MessageBubble";
import TypingIndicator from "./components/TypingIndicator";
import ChatInput from "./components/ChatInput";
import WelcomeScreen from "./components/WelcomeScreen";

const createNewChat = () => ({
  id: Date.now(),
  title: "New Chat",
  messages: [],
});

function formatErrorMessage(error) {
  if (error.name === "CanceledError" || error.code === "ERR_CANCELED") return null;
  if (error.code === "ECONNABORTED") {
    return (
      "⏱️ **The model took too long to respond.**\n\n" +
      "Try Auto/Moderate mode, a shorter question, or try again."
    );
  }
  if (!error.response) {
    return (
      "🔌 **Cannot reach the backend.**\n\n" +
      "Please check that your server is running at `http://127.0.0.1:8000`."
    );
  }
  const backendMsg =
    error.response.data?.response ||
    error.response.data?.detail ||
    "Unknown server error.";
  return `⚠️ **Backend error (${error.response.status}):**\n\n${backendMsg}`;
}

export default function App() {
  const [chatHistory, setChatHistory] = useLocalStorage(
    "universal_ai_chats",
    [createNewChat()]
  );
  const [currentChatId, setCurrentChatId] = useLocalStorage(
    "universal_ai_current_id",
    chatHistory[0]?.id
  );
  const [selectedMode, setSelectedMode] = useLocalStorage(
    "universal_ai_mode",
    "Auto"
  );
  const [sidebarCollapsed, setSidebarCollapsed] = useLocalStorage(
    "universal_ai_sidebar_collapsed",
    false
  );

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);

  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  const currentChat =
    chatHistory.find((c) => c.id === currentChatId) || chatHistory[0];
  const messages = currentChat?.messages || [];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const newChat = useCallback(() => {
    const chat = createNewChat();
    setChatHistory((prev) => [chat, ...prev]);
    setCurrentChatId(chat.id);
    setInput("");
    setSelectedFiles([]);
  }, [setChatHistory, setCurrentChatId]);

  const openChat = useCallback(
    (id) => {
      setCurrentChatId(id);
      setInput("");
      setSelectedFiles([]);
    },
    [setCurrentChatId]
  );

  const deleteChat = useCallback(
    (id) => {
      setChatHistory((prev) => {
        const updated = prev.filter((c) => c.id !== id);
        if (updated.length === 0) {
          const fresh = createNewChat();
          setCurrentChatId(fresh.id);
          return [fresh];
        }
        if (id === currentChatId) setCurrentChatId(updated[0].id);
        return updated;
      });
      toast.success("Chat deleted");
    },
    [currentChatId, setChatHistory, setCurrentChatId]
  );

  // ⭐ NEW: clear ALL chats — used by Settings → Danger Zone
  const clearAllChats = useCallback(() => {
    const fresh = createNewChat();
    setChatHistory([fresh]);
    setCurrentChatId(fresh.id);
    setInput("");
    setSelectedFiles([]);
  }, [setChatHistory, setCurrentChatId]);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles((prev) => [...prev, ...files]);
    e.target.value = "";
  };

  const handleRemoveFile = (index) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleDownload = () => {
    if (messages.length === 0) {
      toast.error("Nothing to download yet");
      return;
    }
    const text = messages
      .map((m) => `${m.role.toUpperCase()}:\n${m.content}`)
      .join("\n\n---\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${currentChat.title || "chat"}-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Chat downloaded");
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setLoading(false);
    toast("Generation stopped", { icon: "⏹️" });
  };

  const sendMessage = async (overrideText) => {
    const text = (overrideText ?? input).trim();
    if (!text && selectedFiles.length === 0) return;

    const userMessage = {
      role: "user",
      content: text || `Uploaded ${selectedFiles.length} file(s)`,
      files: selectedFiles.map((f) => ({ name: f.name, size: f.size })),
      timestamp: Date.now(),
    };

    const newMessages = [...messages, userMessage];

    setChatHistory((prev) =>
      prev.map((c) =>
        c.id === currentChatId
          ? {
              ...c,
              title:
                c.title === "New Chat" && text ? text.slice(0, 40) : c.title,
              messages: newMessages,
            }
          : c
      )
    );

    setInput("");
    setLoading(true);

    const historyForBackend = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    const formData = new FormData();
    formData.append("message", text);
    formData.append("mode", selectedMode);
    formData.append("chat_history", JSON.stringify(historyForBackend));
    formData.append("chat_id", String(currentChatId));
    selectedFiles.forEach((file) => formData.append("files", file));

    abortControllerRef.current = new AbortController();

    try {
      const response = await API.post("/chat", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        signal: abortControllerRef.current.signal,
      });

      const backendData = response.data || {};
      const aiContent =
        backendData.response ?? backendData.message ?? "(empty response)";
      const isBackendError = backendData.success === false;

      const aiMessage = {
        role: "assistant",
        content: aiContent,
        timestamp: Date.now(),
        isError: isBackendError,
      };

      setChatHistory((prev) =>
        prev.map((c) =>
          c.id === currentChatId
            ? { ...c, messages: [...newMessages, aiMessage] }
            : c
        )
      );
      setSelectedFiles([]);
    } catch (error) {
      const friendly = formatErrorMessage(error);
      if (friendly === null) return;
      console.error(error);
      const errorMsg = {
        role: "assistant",
        content: friendly,
        timestamp: Date.now(),
        isError: true,
      };
      setChatHistory((prev) =>
        prev.map((c) =>
          c.id === currentChatId
            ? { ...c, messages: [...newMessages, errorMsg] }
            : c
        )
      );
      toast.error("Failed to get response");
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleReload = () => {
    const lastUserIdx = [...messages]
      .reverse()
      .findIndex((m) => m.role === "user");
    if (lastUserIdx === -1) return;
    const realIdx = messages.length - 1 - lastUserIdx;
    const lastUserMsg = messages[realIdx];

    const trimmed = messages.slice(0, realIdx);
    setChatHistory((prev) =>
      prev.map((c) =>
        c.id === currentChatId ? { ...c, messages: trimmed } : c
      )
    );
    setTimeout(() => sendMessage(lastUserMsg.content), 50);
  };

  return (
    <div
      className="h-screen flex overflow-hidden"
      style={{
        background: "var(--bg-primary)",
        color: "var(--text-primary)",
      }}
    >
      <Sidebar
        newChat={newChat}
        chatHistory={chatHistory}
        deleteChat={deleteChat}
        openChat={openChat}
        currentChatId={currentChatId}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        onClearAllChats={clearAllChats}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <TopBar
          selectedMode={selectedMode}
          setSelectedMode={setSelectedMode}
          onDownload={handleDownload}
          onDelete={() => deleteChat(currentChatId)}
          messages={messages}
        />

        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 && !loading ? (
            <WelcomeScreen onSuggestion={(prompt) => sendMessage(prompt)} />
          ) : (
            <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
              {messages.map((msg, idx) => (
                <MessageBubble
                  key={idx}
                  message={msg}
                  isUser={msg.role === "user"}
                  onReload={
                    idx === messages.length - 1 && msg.role === "assistant"
                      ? handleReload
                      : null
                  }
                />
              ))}
              {loading && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <ChatInput
          input={input}
          setInput={setInput}
          onSend={() => sendMessage()}
          onStop={handleStop}
          loading={loading}
          selectedFiles={selectedFiles}
          onFileChange={handleFileChange}
          onRemoveFile={handleRemoveFile}
        />
      </div>
    </div>
  );
}
