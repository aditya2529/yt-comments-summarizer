import { useState } from "react";
import {
  ThumbsUp, ThumbsDown, Quote, Lightbulb, Users, Star,
  Copy, Check, ExternalLink, Sparkles, RotateCcw, Share2
} from "lucide-react";
import StatBadge from "./StatBadge";
import SentimentMeter from "./SentimentMeter";

const frequencyDot = {
  high: "bg-red-500",
  medium: "bg-amber-500",
  low: "bg-sky-500",
};

export default function SummaryCard({ data, onReset }) {
  const [copied, setCopied] = useState(false);
  const { metadata, summary, comments_analyzed, video_id } = data;
  const s = summary;

  const sentimentClass = `sentiment-${s.overall_sentiment}`;

  const buildText = () =>
    `CommentLens — "${metadata.title}"\n\n${s.one_line_summary}\n\nSentiment: ${s.overall_sentiment} (${s.sentiment_score}/10)\n\nKey Themes:\n${s.key_themes.map((t) => `• ${t.theme}: ${t.description}`).join("\n")}\n\nTop Praises:\n${s.top_praises.map((p) => `• ${p}`).join("\n")}\n\nFun Fact: ${s.fun_fact}\n\nhttps://youtube.com/watch?v=${video_id}`;

  const handleShare = async () => {
    const text = buildText();
    if (navigator.share) {
      try {
        await navigator.share({ title: "CommentLens Summary", text });
        return;
      } catch {}
    }
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4 sm:space-y-5 animate-fade-up pb-16">
      {/* Hero video card */}
      <div className="surface overflow-hidden">
        {metadata.thumbnail && (
          <a
            href={`https://www.youtube.com/watch?v=${video_id}`}
            target="_blank"
            rel="noreferrer"
            className="block relative aspect-video overflow-hidden group"
          >
            <img
              src={metadata.thumbnail}
              alt={metadata.title}
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
            <div className="absolute top-3 right-3 w-9 h-9 rounded-full bg-black/50 backdrop-blur-md flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <ExternalLink size={15} className="text-white" />
            </div>
            <div className="absolute bottom-0 left-0 right-0 p-5 sm:p-6">
              <h2 className="text-white font-bold text-lg sm:text-xl leading-tight mb-1 line-clamp-2 tracking-tight">
                {metadata.title}
              </h2>
              <p className="text-white/70 text-sm">{metadata.channel}</p>
            </div>
          </a>
        )}
        <div className="grid grid-cols-4 gap-2 px-5 sm:px-6 py-4 border-t border-white/5">
          <StatBadge label="Views" value={metadata.view_count} />
          <StatBadge label="Likes" value={metadata.like_count} />
          <StatBadge label="Comments" value={metadata.comment_count} />
          <StatBadge label="Analyzed" value={comments_analyzed} />
        </div>
      </div>

      {/* Headline summary */}
      <div className="surface p-6 sm:p-8 space-y-6">
        <div className="flex items-start gap-3">
          <div className="shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center mt-0.5">
            <Sparkles size={16} className="text-white" />
          </div>
          <p className="text-white text-lg sm:text-xl font-medium leading-snug tracking-tight flex-1">
            {s.one_line_summary}
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <span className={`glass-pill border ${sentimentClass} capitalize`}>
            {s.overall_sentiment}
          </span>
          <span className="text-white/40 text-xs">
            Based on {comments_analyzed} comments
          </span>
        </div>

        <SentimentMeter score={s.sentiment_score} sentiment={s.overall_sentiment} />
      </div>

      {/* Key themes */}
      <div className="surface p-6 sm:p-8">
        <div className="flex items-center gap-2 mb-5">
          <Star size={15} className="text-white/50" />
          <h3 className="text-white/50 text-[11px] font-bold uppercase tracking-[0.15em]">Key Themes</h3>
        </div>
        <div className="space-y-5">
          {s.key_themes.map((theme, i) => (
            <div key={i} className="flex gap-4">
              <div className={`shrink-0 w-2 h-2 rounded-full mt-2 ${frequencyDot[theme.frequency] ?? frequencyDot.low}`} />
              <div className="flex-1 min-w-0">
                <p className="text-white text-base font-semibold leading-tight">{theme.theme}</p>
                <p className="text-white/55 text-sm mt-1.5 leading-relaxed">{theme.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Praises & Criticisms */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
        <div className="surface p-6">
          <div className="flex items-center gap-2 mb-4">
            <ThumbsUp size={14} className="text-emerald-400" />
            <h3 className="text-white/50 text-[11px] font-bold uppercase tracking-[0.15em]">Praises</h3>
          </div>
          <ul className="space-y-3">
            {s.top_praises.map((p, i) => (
              <li key={i} className="flex gap-2.5 text-[14px] text-white/80 leading-relaxed">
                <span className="text-emerald-400 shrink-0 mt-0.5">+</span>
                <span>{p}</span>
              </li>
            ))}
          </ul>
        </div>

        {s.top_criticisms?.length > 0 && (
          <div className="surface p-6">
            <div className="flex items-center gap-2 mb-4">
              <ThumbsDown size={14} className="text-red-400" />
              <h3 className="text-white/50 text-[11px] font-bold uppercase tracking-[0.15em]">Criticisms</h3>
            </div>
            <ul className="space-y-3">
              {s.top_criticisms.map((c, i) => (
                <li key={i} className="flex gap-2.5 text-[14px] text-white/80 leading-relaxed">
                  <span className="text-red-400 shrink-0 mt-0.5">−</span>
                  <span>{c}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Notable quotes */}
      <div className="surface p-6 sm:p-8">
        <div className="flex items-center gap-2 mb-5">
          <Quote size={15} className="text-white/50" />
          <h3 className="text-white/50 text-[11px] font-bold uppercase tracking-[0.15em]">Notable Quotes</h3>
        </div>
        <div className="space-y-5">
          {s.notable_quotes.map((q, i) => (
            <div key={i} className="border-l-2 border-red-500/50 pl-4">
              <p className="text-white text-[15px] italic leading-relaxed">"{q.quote}"</p>
              <p className="text-white/45 text-xs mt-2">{q.reason}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Audience + Fun fact */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
        <div className="surface p-6">
          <div className="flex items-center gap-2 mb-3">
            <Users size={14} className="text-white/50" />
            <h3 className="text-white/50 text-[11px] font-bold uppercase tracking-[0.15em]">Audience</h3>
          </div>
          <p className="text-white/80 text-[14px] leading-relaxed">{s.audience_profile}</p>
        </div>
        <div className="surface p-6">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb size={14} className="text-amber-400" />
            <h3 className="text-white/50 text-[11px] font-bold uppercase tracking-[0.15em]">Fun Fact</h3>
          </div>
          <p className="text-white/80 text-[14px] leading-relaxed">{s.fun_fact}</p>
        </div>
      </div>

      {/* Sticky action bar */}
      <div className="sticky bottom-4 sm:bottom-6 z-10 pt-4">
        <div className="flex gap-3 justify-center">
          <button onClick={handleShare} className="btn-secondary-apple">
            {copied ? <Check size={16} className="text-emerald-400" /> : <Share2 size={16} />}
            {copied ? "Copied" : "Share"}
          </button>
          <button onClick={onReset} className="btn-primary-apple !py-3">
            <RotateCcw size={15} />
            New Summary
          </button>
        </div>
      </div>
    </div>
  );
}
