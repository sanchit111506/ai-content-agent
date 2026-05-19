import { useState, useMemo } from "react";
import {
  Plus,
  Trash2,
  MessageSquare,
  Search,
  PanelLeftClose,
  PanelLeftOpen,
  Settings,
  User,
} from "lucide-react";

import UniversalAILogo from "./UniversalAILogo";
import SettingsModal from "./SettingsModal";
import AccountModal from "./AccountModal";

export default function Sidebar({
  newChat,
  chatHistory = [],
  deleteChat,
  openChat,
  currentChatId,
  collapsed,
  setCollapsed,
  onClearAllChats,
}) {
  const [search, setSearch] = useState("");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);

  const filteredChats = useMemo(() => {
    if (!search.trim()) return chatHistory;
    const q = search.toLowerCase();
    return chatHistory.filter((c) =>
      (c.title || "").toLowerCase().includes(q)
    );
  }, [chatHistory, search]);

  const groupedChats = useMemo(() => {
    const now = Date.now();
    const DAY = 86400000;
    const groups = {
      Today: [],
      Yesterday: [],
      "Previous 7 Days": [],
      Older: [],
    };
    filteredChats.forEach((chat) => {
      const age = now - chat.id;
      if (age < DAY) groups.Today.push(chat);
      else if (age < 2 * DAY) groups.Yesterday.push(chat);
      else if (age < 7 * DAY) groups["Previous 7 Days"].push(chat);
      else groups.Older.push(chat);
    });
    return groups;
  }, [filteredChats]);

  // COLLAPSED VIEW
  if (collapsed) {
    return (
      <>
        <div
          className="w-[60px] flex flex-col items-center py-4 gap-3 border-r"
          style={{
            background: "var(--bg-secondary)",
            borderColor: "var(--border-primary)",
          }}
        >
          <div style={{ color: "var(--text-primary)" }}>
            <UniversalAILogo size={26} />
          </div>

          <CollapsedButton onClick={() => setCollapsed(false)} title="Open sidebar">
            <PanelLeftOpen size={20} />
          </CollapsedButton>
          <CollapsedButton onClick={newChat} title="New chat">
            <Plus size={20} />
          </CollapsedButton>

          <div className="flex-1" />

          <CollapsedButton onClick={() => setSettingsOpen(true)} title="Settings">
            <Settings size={18} />
          </CollapsedButton>
          <CollapsedButton onClick={() => setAccountOpen(true)} title="Account">
            <User size={18} />
          </CollapsedButton>
        </div>

        <SettingsModal
          open={settingsOpen}
          onClose={() => setSettingsOpen(false)}
          onClearAllChats={onClearAllChats}
        />
        <AccountModal
          open={accountOpen}
          onClose={() => setAccountOpen(false)}
          chatHistory={chatHistory}
        />
      </>
    );
  }

  return (
    <>
      <div
        className="w-[260px] flex flex-col h-screen border-r"
        style={{
          background: "var(--bg-secondary)",
          borderColor: "var(--border-primary)",
        }}
      >
        {/* HEADER */}
        <div
          className="flex items-center justify-between px-3 py-3 border-b"
          style={{ borderColor: "var(--border-primary)" }}
        >
          <div className="flex items-center gap-2.5">
            <div style={{ color: "var(--text-primary)" }}>
              <UniversalAILogo size={26} />
            </div>
            <h1
              className="text-base font-semibold tracking-tight"
              style={{ color: "var(--text-primary)" }}
            >
              Universal AI
            </h1>
          </div>
          <button
            onClick={() => setCollapsed(true)}
            className="p-1.5 rounded-md transition"
            style={{ color: "var(--text-tertiary)" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "var(--bg-hover)";
              e.currentTarget.style.color = "var(--text-primary)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.color = "var(--text-tertiary)";
            }}
            title="Collapse sidebar"
          >
            <PanelLeftClose size={18} />
          </button>
        </div>

        {/* NEW CHAT */}
        <div className="p-3">
          <button
            onClick={newChat}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border transition text-sm font-medium"
            style={{
              background: "var(--bg-elevated)",
              borderColor: "var(--border-primary)",
              color: "var(--text-primary)",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-hover)")}
            onMouseLeave={(e) => (e.currentTarget.style.background = "var(--bg-elevated)")}
          >
            <Plus size={16} />
            New chat
          </button>
        </div>

        {/* SEARCH */}
        <div className="px-3 pb-2">
          <div className="relative">
            <Search
              size={14}
              className="absolute left-3 top-1/2 -translate-y-1/2"
              style={{ color: "var(--text-muted)" }}
            />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search chats…"
              className="w-full text-sm pl-9 pr-3 py-2 rounded-lg outline-none transition border"
              style={{
                background: "var(--bg-elevated)",
                borderColor: "var(--border-primary)",
                color: "var(--text-primary)",
              }}
              onFocus={(e) => (e.currentTarget.style.borderColor = "var(--border-focus)")}
              onBlur={(e) => (e.currentTarget.style.borderColor = "var(--border-primary)")}
            />
          </div>
        </div>

        {/* CHAT LIST */}
        <div className="flex-1 overflow-y-auto px-2 pb-2">
          {Object.entries(groupedChats).map(([label, chats]) =>
            chats.length === 0 ? null : (
              <div key={label} className="mb-3">
                <div
                  className="px-2 pt-2 pb-1 text-[11px] uppercase tracking-wider font-medium"
                  style={{ color: "var(--text-muted)" }}
                >
                  {label}
                </div>
                <div className="space-y-0.5">
                  {chats.map((chat) => (
                    <ChatItem
                      key={chat.id}
                      chat={chat}
                      isActive={currentChatId === chat.id}
                      onOpen={() => openChat(chat.id)}
                      onDelete={(e) => {
                        e.stopPropagation();
                        deleteChat(chat.id);
                      }}
                    />
                  ))}
                </div>
              </div>
            )
          )}

          {filteredChats.length === 0 && (
            <div
              className="text-center text-sm py-8 px-2"
              style={{ color: "var(--text-muted)" }}
            >
              {search ? "No chats match your search" : "No chats yet"}
            </div>
          )}
        </div>

        {/* FOOTER */}
        <div
          className="border-t p-2 space-y-0.5"
          style={{ borderColor: "var(--border-primary)" }}
        >
          <FooterButton icon={Settings} onClick={() => setSettingsOpen(true)}>
            Settings
          </FooterButton>
          <FooterButton icon={User} onClick={() => setAccountOpen(true)}>
            Account
          </FooterButton>
        </div>
      </div>

      {/* MODALS */}
      <SettingsModal
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onClearAllChats={onClearAllChats}
      />
      <AccountModal
        open={accountOpen}
        onClose={() => setAccountOpen(false)}
        chatHistory={chatHistory}
      />
    </>
  );
}

// =========================================
// CHAT ITEM
// =========================================
function ChatItem({ chat, isActive, onOpen, onDelete }) {
  return (
    <div
      onClick={onOpen}
      className="group flex items-center gap-2 px-2.5 py-2 rounded-lg cursor-pointer transition"
      style={{
        background: isActive ? "var(--bg-active)" : "transparent",
        color: "var(--text-primary)",
      }}
      onMouseEnter={(e) => {
        if (!isActive) e.currentTarget.style.background = "var(--bg-hover)";
      }}
      onMouseLeave={(e) => {
        if (!isActive) e.currentTarget.style.background = "transparent";
      }}
    >
      <MessageSquare
        size={14}
        className="flex-shrink-0"
        style={{ color: "var(--text-tertiary)" }}
      />
      <span
        className="flex-1 truncate text-sm"
        style={{ color: "var(--text-primary)" }}
      >
        {chat.title || "New Chat"}
      </span>
      <button
        onClick={onDelete}
        className="opacity-0 group-hover:opacity-100 p-1 rounded transition flex-shrink-0"
        style={{ color: "var(--text-muted)" }}
        onMouseEnter={(e) => (e.currentTarget.style.color = "#ef4444")}
        onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-muted)")}
        title="Delete chat"
      >
        <Trash2 size={14} />
      </button>
    </div>
  );
}

// =========================================
// FOOTER BUTTON
// =========================================
function FooterButton({ icon: Icon, children, onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-2.5 py-2 rounded-lg text-sm transition"
      style={{ color: "var(--text-secondary)" }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "var(--bg-hover)";
        e.currentTarget.style.color = "var(--text-primary)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "transparent";
        e.currentTarget.style.color = "var(--text-secondary)";
      }}
    >
      <Icon size={16} />
      {children}
    </button>
  );
}

// =========================================
// COLLAPSED BUTTON
// =========================================
function CollapsedButton({ onClick, title, children }) {
  return (
    <button
      onClick={onClick}
      className="p-2 rounded-lg transition"
      style={{ color: "var(--text-tertiary)" }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "var(--bg-hover)";
        e.currentTarget.style.color = "var(--text-primary)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "transparent";
        e.currentTarget.style.color = "var(--text-tertiary)";
      }}
      title={title}
    >
      {children}
    </button>
  );
}
