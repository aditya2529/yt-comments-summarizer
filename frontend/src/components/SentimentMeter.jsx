export default function SentimentMeter({ score, sentiment }) {
  const pct = ((score - 1) / 9) * 100;

  const gradients = {
    positive: "from-emerald-400 to-emerald-500",
    negative: "from-red-400 to-red-500",
    mixed: "from-amber-400 to-amber-500",
    neutral: "from-sky-400 to-sky-500",
  };

  const gradient = gradients[sentiment] ?? gradients.neutral;

  return (
    <div className="space-y-3">
      <div className="flex justify-between text-[11px] text-white/40 font-medium uppercase tracking-wider">
        <span>Negative</span>
        <span>Positive</span>
      </div>
      <div className="relative h-2 bg-white/8 rounded-full overflow-hidden">
        <div
          className={`absolute inset-y-0 left-0 rounded-full bg-gradient-to-r ${gradient} transition-all duration-1000 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="text-right">
        <span className="text-white font-bold text-2xl tabular-nums">{score}</span>
        <span className="text-white/40 text-sm">/10</span>
      </div>
    </div>
  );
}
