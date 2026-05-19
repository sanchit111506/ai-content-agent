import { Sparkles, Code2, FileText, Calculator, Search } from "lucide-react";

const SUGGESTIONS = [
  { icon: Code2,      title: "Write code",   prompt: "Write a Python FastAPI endpoint that uploads files" },
  { icon: FileText,   title: "Summarize",    prompt: "Summarize the key points of quantum computing" },
  { icon: Calculator, title: "Solve math",   prompt: "Solve the integral of x^2 * sin(x) dx step by step" },
  { icon: Search,     title: "Research",     prompt: "Latest news on AI developments this week" },
];

export default function WelcomeScreen({ onSuggestion }) {
  return (
    <div className="h-full flex flex-col items-center justify-center px-4">
      {/* Logo bubble — gradient stays vibrant in both themes */}
      <div
        className="w-14 h-14 rounded-2xl flex items-center justify-center mb-5"
        style={{ background: "var(--logo-icon-bg)" }}
      >
        <Sparkles size={26} className="text-white" />
      </div>

      {/* Title — uses theme primary text */}
      <h1
        className="text-2xl font-semibold mb-1"
        style={{ color: "var(--text-primary)" }}
      >
        How can I help you today?
      </h1>
      <p
        className="text-sm mb-10"
        style={{ color: "var(--text-tertiary)" }}
      >
        Choose a suggestion below or type your own question.
      </p>

      {/* Suggestion cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-2xl">
        {SUGGESTIONS.map((s) => {
          const Icon = s.icon;
          return (
            <button
              key={s.title}
              onClick={() => onSuggestion(s.prompt)}
              className="flex items-start gap-3 p-3.5 rounded-xl border transition text-left"
              style={{
                background: "var(--bg-elevated)",
                borderColor: "var(--border-primary)",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "var(--bg-hover)";
                e.currentTarget.style.borderColor = "var(--border-secondary)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "var(--bg-elevated)";
                e.currentTarget.style.borderColor = "var(--border-primary)";
              }}
            >
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ background: "var(--bg-hover)" }}
              >
                <Icon size={16} style={{ color: "var(--text-secondary)" }} />
              </div>
              <div className="flex flex-col min-w-0">
                <span
                  className="text-sm font-medium mb-0.5"
                  style={{ color: "var(--text-primary)" }}
                >
                  {s.title}
                </span>
                <span
                  className="text-xs line-clamp-2"
                  style={{ color: "var(--text-tertiary)" }}
                >
                  {s.prompt}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
