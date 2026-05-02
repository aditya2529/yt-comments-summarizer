export default function StatBadge({ label, value }) {
  const fmt = (n) => {
    const num = parseInt(n, 10);
    if (isNaN(num)) return n;
    if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
    if (num >= 1_000) return (num / 1_000).toFixed(1) + "K";
    return num.toLocaleString();
  };

  return (
    <div className="flex flex-col">
      <span className="text-white font-semibold text-[15px] leading-tight tabular-nums">{fmt(value)}</span>
      <span className="text-white/40 text-[11px] uppercase tracking-wider mt-0.5">{label}</span>
    </div>
  );
}
