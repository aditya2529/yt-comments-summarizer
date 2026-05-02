const steps = [
  "Fetching the video",
  "Reading comments",
  "Spotting patterns",
  "Crafting insights",
  "Almost there",
];

export default function LoadingState({ step = 0 }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 sm:py-28 gap-8 animate-scale-in">
      <div className="relative">
        <div className="absolute inset-0 rounded-full bg-red-500/30 blur-3xl animate-glow" />
        <div className="relative w-24 h-24 rounded-full border border-white/10 flex items-center justify-center bg-black/40 backdrop-blur-xl">
          <div className="absolute inset-2 rounded-full border-2 border-transparent border-t-red-500 animate-spin" />
          <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
        </div>
      </div>

      <div className="text-center space-y-2 px-6">
        <p className="text-white text-xl sm:text-2xl font-semibold tracking-tight">
          {steps[Math.min(step, steps.length - 1)]}
        </p>
        <p className="text-white/40 text-sm">Usually takes 10–20 seconds</p>
      </div>

      <div className="flex gap-2">
        {steps.map((_, i) => (
          <div
            key={i}
            className={`h-1 rounded-full transition-all duration-700 ${
              i <= step ? "w-8 bg-red-500" : "w-2 bg-white/10"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
