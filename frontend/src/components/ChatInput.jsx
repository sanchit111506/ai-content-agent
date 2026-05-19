import { useRef, useEffect } from "react";
import { Paperclip, ArrowUp, Square, Mic } from "lucide-react";
import FilePreview from "./FilePreview";

export default function ChatInput({
  input,
  setInput,
  onSend,
  onStop,
  loading,
  selectedFiles,
  onFileChange,
  onRemoveFile,
}) {
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 200)}px`;
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading) onSend();
    }
  };

  const canSend = (input.trim() || selectedFiles.length > 0) && !loading;

  return (
    <div className="px-4 pb-4">
      <div className="max-w-3xl mx-auto">
        {selectedFiles.length > 0 && (
          <FilePreview
            files={selectedFiles}
            removable
            onRemove={onRemoveFile}
          />
        )}

        <div
          className="flex items-end gap-2 rounded-3xl px-3 py-2.5 border transition shadow-sm"
          style={{
            background: "var(--bg-input)",
            borderColor: "var(--border-primary)",
          }}
        >
          {/* Attach */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
            className="p-2 rounded-lg transition flex-shrink-0 disabled:opacity-50"
            style={{ color: "var(--text-tertiary)" }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.currentTarget.style.background = "var(--bg-hover)";
                e.currentTarget.style.color = "var(--text-primary)";
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.color = "var(--text-tertiary)";
            }}
            title="Attach file"
          >
            <Paperclip size={18} />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            hidden
            onChange={onFileChange}
          />

          {/* Textarea */}
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything…"
            rows={1}
            className="chat-textarea flex-1 bg-transparent outline-none text-[15px] py-1.5 px-1"
            style={{ color: "var(--text-primary)" }}
          />

          {/* Mic */}
          <button
            className="p-2 rounded-lg transition flex-shrink-0"
            style={{ color: "var(--text-tertiary)" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "var(--bg-hover)";
              e.currentTarget.style.color = "var(--text-primary)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.color = "var(--text-tertiary)";
            }}
            title="Voice input (coming soon)"
          >
            <Mic size={18} />
          </button>

          {/* Send / Stop */}
          {loading ? (
            <button
              onClick={onStop}
              className="p-2 rounded-lg transition flex-shrink-0"
              style={{
                background: "var(--send-btn-bg)",
                color: "var(--send-btn-text)",
              }}
              title="Stop generating"
            >
              <Square size={16} fill="currentColor" />
            </button>
          ) : (
            <button
              onClick={onSend}
              disabled={!canSend}
              className="p-2 rounded-lg transition flex-shrink-0"
              style={{
                background: canSend ? "var(--send-btn-bg)" : "var(--bg-hover)",
                color: canSend ? "var(--send-btn-text)" : "var(--text-muted)",
                cursor: canSend ? "pointer" : "not-allowed",
              }}
              title="Send message"
            >
              <ArrowUp size={18} />
            </button>
          )}
        </div>

        <p
          className="text-center text-xs mt-2"
          style={{ color: "var(--text-muted)" }}
        >
          Universal AI can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
}
