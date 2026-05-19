import { useState } from "react";
import { Copy, Check } from "lucide-react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

/**
 * CodeBlock — wraps a syntax-highlighted block with
 *  - language label
 *  - copy button (with success state)
 */
export default function CodeBlock({ language, value }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="my-3 rounded-lg overflow-hidden border border-zinc-800 bg-[#1a1a1a]">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-1.5 bg-[#0f0f0f] border-b border-zinc-800 text-xs">
        <span className="text-zinc-400 font-mono lowercase">
          {language || "code"}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
        >
          {copied ? (
            <>
              <Check size={12} /> Copied
            </>
          ) : (
            <>
              <Copy size={12} /> Copy
            </>
          )}
        </button>
      </div>

      {/* Code */}
      <SyntaxHighlighter
        language={language || "text"}
        style={oneDark}
        customStyle={{
          margin: 0,
          padding: "12px 16px",
          background: "transparent",
          fontSize: "13.5px",
          lineHeight: "1.6",
        }}
        codeTagProps={{
          style: {
            fontFamily:
              '"JetBrains Mono", "Menlo", Consolas, monospace',
          },
        }}
      >
        {value}
      </SyntaxHighlighter>
    </div>
  );
}
