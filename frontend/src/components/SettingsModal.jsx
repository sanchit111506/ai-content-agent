import { useState } from "react";
import toast from "react-hot-toast";
import {
  Sun,
  Moon,
  Trash2,
  Database,
  Zap,
  Sparkles,
  Telescope,
  Server,
  AlertTriangle,
} from "lucide-react";

import Modal from "./Modal";
import { useTheme } from "../contexts/ThemeContext";
import useLocalStorage from "../hooks/useLocalStorage";
import API from "../services/api";

const MODES = [
  { id: "Auto", label: "Auto", icon: Zap, description: "Fast (phi3:mini)" },
  { id: "Moderate", label: "Moderate", icon: Sparkles, description: "Balanced (qwen2.5:7b)" },
  { id: "DeepSearch", label: "DeepSearch", icon: Telescope, description: "Deep (qwen2.5:7b)" },
];

export default function SettingsModal({ open, onClose, onClearAllChats }) {
  const { theme, setTheme } = useTheme();
  const [defaultMode, setDefaultMode] = useLocalStorage("universal_ai_mode", "Auto");
  const [backendUrl, setBackendUrl] = useLocalStorage(
    "universal_ai_backend_url",
    "http://127.0.0.1:8000"
  );
  const [confirmClear, setConfirmClear] = useState(false);

  const handleClearAllChats = () => {
    if (!confirmClear) {
      setConfirmClear(true);
      setTimeout(() => setConfirmClear(false), 3000);
      return;
    }
    onClearAllChats?.();
    setConfirmClear(false);
    toast.success("All chats cleared");
    onClose();
  };

  const handleClearBackendMemory = async () => {
    try {
      await API.post("/memory/clear");
      toast.success("Backend memory cleared");
    } catch (err) {
      toast.error("Could not reach backend — is it running?");
    }
  };

  const handleSaveBackendUrl = () => {
    toast.success("Backend URL saved — reload the page to apply");
  };

  return (
    <Modal open={open} onClose={onClose} title="Settings" maxWidth="max-w-lg">
      <div className="space-y-6">
        {/* THEME */}
        <Section title="Appearance">
          <div className="grid grid-cols-2 gap-2">
            <ThemeCard
              active={theme === "light"}
              onClick={() => setTheme("light")}
              icon={Sun}
              label="Light"
            />
            <ThemeCard
              active={theme === "dark"}
              onClick={() => setTheme("dark")}
              icon={Moon}
              label="Dark"
            />
          </div>
        </Section>

        {/* DEFAULT MODE */}
        <Section title="Default Mode">
          <div className="grid grid-cols-3 gap-2">
            {MODES.map((m) => {
              const Icon = m.icon;
              const active = defaultMode === m.id;
              return (
                <button
                  key={m.id}
                  onClick={() => setDefaultMode(m.id)}
                  title={m.description}
                  className="flex flex-col items-center gap-1.5 p-3 rounded-lg border transition"
                  style={{
                    background: active ? "var(--accent-bg)" : "var(--bg-secondary)",
                    borderColor: active ? "transparent" : "var(--border-primary)",
                    color: active ? "var(--accent-text)" : "var(--text-secondary)",
                  }}
                >
                  <Icon size={18} />
                  <span className="text-xs font-medium">{m.label}</span>
                </button>
              );
            })}
          </div>
          <p className="text-xs mt-2" style={{ color: "var(--text-tertiary)" }}>
            New chats will start in this mode.
          </p>
        </Section>

        {/* BACKEND */}
        <Section title="Backend Connection">
          <div className="space-y-2">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Server
                  size={14}
                  className="absolute left-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--text-muted)" }}
                />
                <input
                  type="text"
                  value={backendUrl}
                  onChange={(e) => setBackendUrl(e.target.value)}
                  className="w-full text-sm pl-9 pr-3 py-2 rounded-lg outline-none border"
                  style={{
                    background: "var(--bg-secondary)",
                    borderColor: "var(--border-primary)",
                    color: "var(--text-primary)",
                  }}
                />
              </div>
              <button
                onClick={handleSaveBackendUrl}
                className="px-3 py-2 rounded-lg text-sm font-medium transition"
                style={{
                  background: "var(--send-btn-bg)",
                  color: "var(--send-btn-text)",
                }}
              >
                Save
              </button>
            </div>
            <p className="text-xs" style={{ color: "var(--text-tertiary)" }}>
              Default: http://127.0.0.1:8000
            </p>
          </div>
        </Section>

        {/* DATA */}
        <Section title="Data">
          <div className="space-y-2">
            <button
              onClick={handleClearBackendMemory}
              className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition border"
              style={{
                background: "var(--bg-secondary)",
                borderColor: "var(--border-primary)",
                color: "var(--text-primary)",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-hover)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "var(--bg-secondary)")}
            >
              <span className="flex items-center gap-2">
                <Database size={15} />
                Clear backend memory
              </span>
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                Server-side
              </span>
            </button>
          </div>
        </Section>

        {/* DANGER ZONE */}
        <Section title="Danger Zone">
          <button
            onClick={handleClearAllChats}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium transition border"
            style={{
              background: confirmClear ? "#dc2626" : "transparent",
              borderColor: confirmClear ? "#dc2626" : "#ef4444",
              color: confirmClear ? "#ffffff" : "#ef4444",
            }}
          >
            {confirmClear ? (
              <>
                <AlertTriangle size={15} />
                Click again to confirm — this cannot be undone
              </>
            ) : (
              <>
                <Trash2 size={15} />
                Clear all chat history (local)
              </>
            )}
          </button>
        </Section>
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

function ThemeCard({ active, onClick, icon: Icon, label }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-3 px-4 py-3 rounded-lg border transition"
      style={{
        background: active ? "var(--accent-bg)" : "var(--bg-secondary)",
        borderColor: active ? "transparent" : "var(--border-primary)",
        color: active ? "var(--accent-text)" : "var(--text-secondary)",
      }}
    >
      <Icon size={18} />
      <span className="text-sm font-medium">{label}</span>
    </button>
  );
}
