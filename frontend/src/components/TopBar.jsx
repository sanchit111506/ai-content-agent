import { useState, useRef, useEffect } from "react";
import toast from "react-hot-toast";
import {
  Share2,
  MoreHorizontal,
  Download,
  Trash2,
  Copy,
  Link2,
} from "lucide-react";

import AgentSelector from "./AgentSelector";
import ThemeToggle from "./ThemeToggle";

export default function TopBar({
  selectedMode,
  setSelectedMode,
  onDownload,
  onDelete,
  messages,
}) {
  const [shareOpen, setShareOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const shareRef = useRef(null);
  const moreRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (shareRef.current && !shareRef.current.contains(e.target)) setShareOpen(false);
      if (moreRef.current && !moreRef.current.contains(e.target)) setMoreOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const getChatText = () =>
    messages.map((m) => `${m.role.toUpperCase()}:\n${m.content}`).join("\n\n");

  const handleCopyChat = async () => {
    await navigator.clipboard.writeText(getChatText());
    toast.success("Chat copied to clipboard");
    setShareOpen(false);
  };

  const handleCopyLink = async () => {
    await navigator.clipboard.writeText(window.location.href);
    toast.success("Link copied");
    setShareOpen(false);
  };

  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Universal AI Chat",
          text: getChatText(),
        });
      } catch (err) {/* user cancelled */}
    } else {
      toast.error("Native sharing not supported on this device");
    }
    setShareOpen(false);
  };

  return (
    <div
      className="flex items-center justify-between px-4 py-2.5 border-b"
      style={{
        background: "var(--bg-primary)",
        borderColor: "var(--border-primary)",
      }}
    >
      {/* LEFT — Mode pills */}
      <AgentSelector
        selectedMode={selectedMode}
        setSelectedMode={setSelectedMode}
      />

      {/* RIGHT */}
      <div className="flex items-center gap-1">
        {/* 🌙 THEME TOGGLE - this is the missing button */}
        <ThemeToggle />

        {/* SHARE */}
        <div className="relative" ref={shareRef}>
          <button
            onClick={() => setShareOpen((v) => !v)}
            className="p-2 rounded-lg border transition"
            style={{
              borderColor: "var(--border-primary)",
              color: "var(--text-secondary)",
              background: "var(--bg-elevated)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "var(--bg-hover)";
              e.currentTarget.style.color = "var(--text-primary)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "var(--bg-elevated)";
              e.currentTarget.style.color = "var(--text-secondary)";
            }}
            title="Share"
          >
            <Share2 size={16} />
          </button>
          {shareOpen && (
            <Menu>
              <MenuItem icon={Share2} onClick={handleNativeShare}>Native share</MenuItem>
              <MenuItem icon={Link2} onClick={handleCopyLink}>Copy link</MenuItem>
              <MenuItem icon={Copy} onClick={handleCopyChat}>Copy full chat</MenuItem>
            </Menu>
          )}
        </div>

        {/* MORE */}
        <div className="relative" ref={moreRef}>
          <button
            onClick={() => setMoreOpen((v) => !v)}
            className="p-2 rounded-lg border transition"
            style={{
              borderColor: "var(--border-primary)",
              color: "var(--text-secondary)",
              background: "var(--bg-elevated)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "var(--bg-hover)";
              e.currentTarget.style.color = "var(--text-primary)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "var(--bg-elevated)";
              e.currentTarget.style.color = "var(--text-secondary)";
            }}
            title="More options"
          >
            <MoreHorizontal size={16} />
          </button>
          {moreOpen && (
            <Menu>
              <MenuItem icon={Download} onClick={() => { onDownload(); setMoreOpen(false); }}>
                Download chat
              </MenuItem>
              <MenuItem icon={Trash2} danger onClick={() => { onDelete(); setMoreOpen(false); }}>
                Delete chat
              </MenuItem>
            </Menu>
          )}
        </div>
      </div>
    </div>
  );
}

function Menu({ children }) {
  return (
    <div
      className="absolute right-0 top-full mt-1.5 min-w-[180px] border rounded-lg shadow-lg overflow-hidden z-50 py-1 fade-in-up"
      style={{
        background: "var(--bg-elevated)",
        borderColor: "var(--border-primary)",
      }}
    >
      {children}
    </div>
  );
}

function MenuItem({ icon: Icon, children, onClick, danger }) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-3 py-2 text-sm transition"
      style={{ color: danger ? "#ef4444" : "var(--text-primary)" }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = danger
          ? "rgba(239, 68, 68, 0.1)"
          : "var(--bg-hover)";
      }}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
    >
      <Icon size={15} />
      {children}
    </button>
  );
}