import { useState } from "react";
import toast from "react-hot-toast";
import {
  Copy,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Check,
} from "lucide-react";

/**
 * MessageActions — shown only on assistant messages.
 * Uses toasts (not window.alert) for feedback.
 */
export default function MessageActions({ content, onReload }) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(null); // "up" | "down" | null

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      toast.success("Copied to clipboard");
      setTimeout(() => setCopied(false), 1500);
    } catch (err) {
      toast.error("Failed to copy");
    }
  };

  const handleFeedback = (type) => {
    setFeedback(type);
    toast.success(type === "up" ? "Thanks for the feedback" : "Got it, we'll improve");
  };

  const handleReload = () => {
    if (onReload) {
      onReload();
      toast("Regenerating…", { icon: "🔄" });
    }
  };

  return (
    <div className="flex items-center gap-1 mt-2 text-zinc-500">
      <ActionButton onClick={handleCopy} title={copied ? "Copied!" : "Copy"}>
        {copied ? <Check size={15} /> : <Copy size={15} />}
      </ActionButton>

      <ActionButton
        onClick={() => handleFeedback("up")}
        title="Good response"
        active={feedback === "up"}
        activeColor="text-green-400"
      >
        <ThumbsUp size={15} />
      </ActionButton>

      <ActionButton
        onClick={() => handleFeedback("down")}
        title="Bad response"
        active={feedback === "down"}
        activeColor="text-red-400"
      >
        <ThumbsDown size={15} />
      </ActionButton>

      {onReload && (
        <ActionButton onClick={handleReload} title="Regenerate">
          <RotateCcw size={15} />
        </ActionButton>
      )}
    </div>
  );
}

// =========================================
// REUSABLE ACTION BUTTON
// =========================================
function ActionButton({ onClick, title, children, active, activeColor }) {
  return (
    <button
      onClick={onClick}
      title={title}
      className={`p-1.5 rounded-md hover:bg-zinc-800 transition ${
        active ? activeColor : "hover:text-white"
      }`}
    >
      {children}
    </button>
  );
}
