import { useState } from "react";
import { ArrowRight, Loader2 } from "lucide-react";

export default function URLInput({ onSubmit, loading, autoFocus = false }) {
  const [url, setUrl] = useState("");
  const isValidUrl = url.includes("youtube.com") || url.includes("youtu.be");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim() && isValidUrl) onSubmit(url.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-xl mx-auto">
      <div className="surface flex items-center gap-2 p-2 pl-5 sm:pl-6 transition-all focus-within:border-white/20">
        <input
          type="url"
          inputMode="url"
          autoComplete="off"
          autoCapitalize="off"
          autoCorrect="off"
          spellCheck="false"
          autoFocus={autoFocus}
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste a YouTube link"
          disabled={loading}
          className="flex-1 bg-transparent outline-none text-[15px] sm:text-base text-white placeholder-white/35 py-3 min-w-0"
        />
        <button
          type="submit"
          disabled={loading || !isValidUrl}
          aria-label="Summarize"
          className="btn-primary-apple !p-0 !w-12 !h-12 sm:!w-auto sm:!px-6 sm:!h-12 shrink-0"
        >
          {loading ? (
            <Loader2 size={20} className="animate-spin" />
          ) : (
            <>
              <span className="hidden sm:inline">Summarize</span>
              <ArrowRight size={20} className="sm:hidden" />
            </>
          )}
        </button>
      </div>
      {url && !isValidUrl && (
        <p className="text-red-400/70 text-xs mt-3 ml-1 text-center">
          That doesn't look like a YouTube link
        </p>
      )}
    </form>
  );
}
