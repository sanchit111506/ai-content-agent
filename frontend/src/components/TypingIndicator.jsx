import { Sparkles } from "lucide-react";

/**
 * TypingIndicator
 * - Avatar + animated dots
 * - Matches the assistant message row layout
 */
export default function TypingIndicator() {
  return (
    <div className="flex gap-4 fade-in-up">
      {/* Avatar */}
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
        <Sparkles size={16} className="text-white" />
      </div>

      {/* Dots */}
      <div className="flex items-center gap-1.5 px-4 py-3 bg-[#1f1f1f] border border-zinc-800 rounded-2xl">
        <span className="typing-dot w-1.5 h-1.5 rounded-full bg-zinc-400 inline-block" />
        <span className="typing-dot w-1.5 h-1.5 rounded-full bg-zinc-400 inline-block" />
        <span className="typing-dot w-1.5 h-1.5 rounded-full bg-zinc-400 inline-block" />
      </div>
    </div>
  );
}
