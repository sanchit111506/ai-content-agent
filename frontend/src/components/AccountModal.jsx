import { useState, useMemo } from "react";
import toast from "react-hot-toast";
import {
  User,
  Mail,
  MessageSquare,
  Clock,
  Database,
  LogOut,
} from "lucide-react";

import Modal from "./Modal";
import useLocalStorage from "../hooks/useLocalStorage";

export default function AccountModal({ open, onClose, chatHistory }) {
  const [profile, setProfile] = useLocalStorage("universal_ai_profile", {
    name: "User",
    email: "",
  });

  const [draftName, setDraftName] = useState(profile.name);
  const [draftEmail, setDraftEmail] = useState(profile.email);

  // Derived stats from local chat history
  const stats = useMemo(() => {
    const totalChats = chatHistory?.length || 0;
    let totalMessages = 0;
    let userMessages = 0;
    let aiMessages = 0;
    let firstChatDate = null;

    chatHistory?.forEach((chat) => {
      totalMessages += chat.messages?.length || 0;
      chat.messages?.forEach((m) => {
        if (m.role === "user") userMessages++;
        else if (m.role === "assistant") aiMessages++;
      });
      if (!firstChatDate || chat.id < firstChatDate) firstChatDate = chat.id;
    });

    return {
      totalChats,
      totalMessages,
      userMessages,
      aiMessages,
      firstChatDate,
    };
  }, [chatHistory]);

  const handleSave = () => {
    setProfile({
      name: draftName.trim() || "User",
      email: draftEmail.trim(),
    });
    toast.success("Profile saved");
  };

  const handleResetProfile = () => {
    setProfile({ name: "User", email: "" });
    setDraftName("User");
    setDraftEmail("");
    toast.success("Profile reset");
  };

  // Get initials for avatar
  const initials = useMemo(() => {
    const name = (profile.name || "U").trim();
    const parts = name.split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  }, [profile.name]);

  const memberSince = stats.firstChatDate
    ? new Date(stats.firstChatDate).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "Today";

  return (
    <Modal open={open} onClose={onClose} title="Account" maxWidth="max-w-lg">
      <div className="space-y-6">
        {/* AVATAR + NAME */}
        <div className="flex items-center gap-4">
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center text-xl font-semibold flex-shrink-0"
            style={{
              background: "linear-gradient(135deg, #6366f1, #a855f7)",
              color: "#ffffff",
            }}
          >
            {initials}
          </div>
          <div className="flex-1 min-w-0">
            <div
              className="text-lg font-semibold truncate"
              style={{ color: "var(--text-primary)" }}
            >
              {profile.name || "User"}
            </div>
            <div
              className="text-sm truncate"
              style={{ color: "var(--text-tertiary)" }}
            >
              {profile.email || "No email set"}
            </div>
            <div
              className="text-xs mt-0.5"
              style={{ color: "var(--text-muted)" }}
            >
              Member since {memberSince}
            </div>
          </div>
        </div>

        {/* EDIT PROFILE */}
        <Section title="Profile">
          <div className="space-y-2.5">
            <Field icon={User} placeholder="Your name" value={draftName} onChange={setDraftName} />
            <Field icon={Mail} placeholder="your@email.com" value={draftEmail} onChange={setDraftEmail} type="email" />
            <div className="flex gap-2 pt-1">
              <button
                onClick={handleSave}
                className="flex-1 py-2 rounded-lg text-sm font-medium transition"
                style={{
                  background: "var(--send-btn-bg)",
                  color: "var(--send-btn-text)",
                }}
              >
                Save profile
              </button>
              <button
                onClick={handleResetProfile}
                className="px-3 py-2 rounded-lg text-sm transition border"
                style={{
                  borderColor: "var(--border-primary)",
                  color: "var(--text-secondary)",
                }}
              >
                Reset
              </button>
            </div>
          </div>
        </Section>

        {/* STATS */}
        <Section title="Your Activity">
          <div className="grid grid-cols-2 gap-2">
            <StatCard icon={MessageSquare} label="Chats" value={stats.totalChats} />
            <StatCard icon={Database} label="Messages" value={stats.totalMessages} />
            <StatCard icon={User} label="Sent" value={stats.userMessages} />
            <StatCard icon={Clock} label="Received" value={stats.aiMessages} />
          </div>
        </Section>

        {/* INFO */}
        <div
          className="text-xs px-3 py-2.5 rounded-lg border"
          style={{
            background: "var(--bg-secondary)",
            borderColor: "var(--border-primary)",
            color: "var(--text-tertiary)",
          }}
        >
          🔒 Your profile is stored locally in your browser. Nothing is sent to any server.
        </div>
      </div>
    </Modal>
  );
}

// =========================================
// HELPERS
// =========================================
function Section({ title, children }) {
  return (
    <div>
      <h3
        className="text-xs font-semibold uppercase tracking-wider mb-2.5"
        style={{ color: "var(--text-tertiary)" }}
      >
        {title}
      </h3>
      {children}
    </div>
  );
}

function Field({ icon: Icon, placeholder, value, onChange, type = "text" }) {
  return (
    <div className="relative">
      <Icon
        size={14}
        className="absolute left-3 top-1/2 -translate-y-1/2"
        style={{ color: "var(--text-muted)" }}
      />
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full text-sm pl-9 pr-3 py-2 rounded-lg outline-none border"
        style={{
          background: "var(--bg-secondary)",
          borderColor: "var(--border-primary)",
          color: "var(--text-primary)",
        }}
      />
    </div>
  );
}

function StatCard({ icon: Icon, label, value }) {
  return (
    <div
      className="flex items-center gap-3 p-3 rounded-lg border"
      style={{
        background: "var(--bg-secondary)",
        borderColor: "var(--border-primary)",
      }}
    >
      <div
        className="w-9 h-9 rounded-lg flex items-center justify-center"
        style={{ background: "var(--accent-bg)" }}
      >
        <Icon size={16} style={{ color: "var(--accent-text)" }} />
      </div>
      <div className="flex flex-col min-w-0">
        <span
          className="text-lg font-semibold leading-tight"
          style={{ color: "var(--text-primary)" }}
        >
          {value}
        </span>
        <span
          className="text-xs"
          style={{ color: "var(--text-tertiary)" }}
        >
          {label}
        </span>
      </div>
    </div>
  );
}
