import { Zap, Sparkles, Telescope } from "lucide-react";
import { useTheme } from "../contexts/ThemeContext";

const MODES = [
  { id: "Auto",       label: "Auto",       icon: Zap,       description: "Fast • phi3:mini" },
  { id: "Moderate",   label: "Moderate",   icon: Sparkles,  description: "Balanced • qwen2.5:7b" },
  { id: "DeepSearch", label: "DeepSearch", icon: Telescope, description: "Deep reasoning • qwen2.5:14b" },
];

export default function AgentSelector({ selectedMode, setSelectedMode }) {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  return (
    <div
      className="inline-flex items-center p-1 rounded-full border"
      style={{
        background: isDark ? "#1f1f1f" : "#ffffff",
        borderColor: "var(--border-primary)",
      }}
    >
      {MODES.map((mode) => {
        const Icon = mode.icon;
        const isActive = selectedMode === mode.id;
        return (
          <button
            key={mode.id}
            onClick={() => setSelectedMode(mode.id)}
            title={mode.description}
            className="flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium transition"
            style={{
              background: isActive ? "var(--pill-active-bg)" : "transparent",
              color: isActive
                ? "var(--pill-active-text)"
                : "var(--text-secondary)",
            }}
            onMouseEnter={(e) => {
              if (!isActive) {
                e.currentTarget.style.color = "var(--text-primary)";
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive) {
                e.currentTarget.style.color = "var(--text-secondary)";
              }
            }}
          >
            <Icon size={14} />
            {mode.label}
          </button>
        );
      })}
    </div>
  );
}
