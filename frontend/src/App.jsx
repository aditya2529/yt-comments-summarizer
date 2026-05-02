import { useState, useEffect } from "react";
import { Sparkles, Zap, Eye, MessageCircle, Heart, ChevronDown } from "lucide-react";
import URLInput from "./components/URLInput";
import LoadingState from "./components/LoadingState";
import SummaryCard from "./components/SummaryCard";
import { summarize } from "./lib/api";

export default function App() {
  const [state, setState] = useState("idle");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loadStep, setLoadStep] = useState(0);

  useEffect(() => {
    if (state !== "loading") return;
    setLoadStep(0);
    const interval = setInterval(() => setLoadStep((s) => Math.min(s + 1, 4)), 3500);
    return () => clearInterval(interval);
  }, [state]);

  useEffect(() => {
    if (state === "result" || state === "loading") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [state]);

  const handleSubmit = async (url) => {
    setState("loading");
    setError("");
    setResult(null);
    try {
      const data = await summarize(url, 150);
      setResult(data);
      setState("result");
    } catch (err) {
      setError(err.message);
      setState("error");
    }
  };

  const reset = () => {
    setState("idle");
    setResult(null);
    setError("");
  };

  return (
    <div className="min-h-screen mesh-bg">
      {/* NAV */}
      <nav className="sticky top-0 z-50 backdrop-blur-2xl bg-black/40 border-b border-white/5">
        <div className="container-app flex items-center justify-between h-12">
          <button onClick={reset} className="flex items-center gap-2 group">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-red-400 to-red-700 flex items-center justify-center">
              <Sparkles size={12} className="text-white" />
            </div>
            <span className="text-white font-semibold text-[15px] tracking-tight">CommentLens</span>
          </button>
          <span className="text-white/40 text-xs hidden sm:block">AI · YouTube · Insights</span>
        </div>
      </nav>

      {state === "result" && result ? (
        <main className="container-app pt-8 sm:pt-10">
          <SummaryCard data={result} onReset={reset} />
        </main>
      ) : (
        <>
          {/* HERO */}
          <section className="container-app relative pt-12 sm:pt-20 pb-12 sm:pb-20">
            <div className="text-center max-w-3xl mx-auto">
              <div className="inline-flex animate-fade-up">
                <span className="glass-pill text-red-400">
                  <Zap size={11} fill="currentColor" />
                  POWERED BY CLAUDE AI
                </span>
              </div>

              <h1 className="heading-display text-white mt-6 sm:mt-8 animate-fade-up delay-100">
                Read between<br />
                <span className="gradient-text">the comments.</span>
              </h1>

              <p className="body-large mt-5 sm:mt-7 max-w-xl mx-auto animate-fade-up delay-200">
                Paste any YouTube link. Get sentiment, themes, and standout
                opinions from thousands of comments — in seconds.
              </p>

              <div className="mt-9 sm:mt-12 animate-fade-up delay-300">
                {state === "loading" ? (
                  <LoadingState step={loadStep} />
                ) : (
                  <URLInput onSubmit={handleSubmit} loading={false} />
                )}
              </div>

              {state === "error" && (
                <div className="mt-8 max-w-md mx-auto surface p-6 animate-scale-in">
                  <p className="text-red-400 font-semibold text-sm mb-1">Something went wrong</p>
                  <p className="text-white/60 text-sm">{error}</p>
                  <button onClick={reset} className="btn-secondary-apple mt-4 mx-auto">
                    Try again
                  </button>
                </div>
              )}

              {state === "idle" && (
                <div className="mt-8 flex justify-center animate-fade-up delay-400">
                  <ChevronDown size={20} className="text-white/30 animate-bounce" />
                </div>
              )}
            </div>
          </section>

          {/* FEATURE STRIP — Apple-style */}
          {state === "idle" && (
            <>
              <section className="container-app pb-16 sm:pb-24">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-5 max-w-4xl mx-auto">
                  {[
                    { icon: Eye, title: "See sentiment", desc: "Instantly know if viewers loved or hated it.", glow: "from-emerald-500/20" },
                    { icon: MessageCircle, title: "Spot themes", desc: "The conversations everyone is having.", glow: "from-red-500/20" },
                    { icon: Heart, title: "Find the gold", desc: "Standout quotes you'd otherwise miss.", glow: "from-amber-500/20" },
                  ].map((f, i) => (
                    <div
                      key={i}
                      className="surface p-7 sm:p-8 relative overflow-hidden group hover:border-white/15 transition-all"
                    >
                      <div className={`absolute -top-12 -right-12 w-32 h-32 rounded-full bg-gradient-to-br ${f.glow} to-transparent blur-2xl`} />
                      <f.icon size={22} className="text-white/80 mb-4 relative" />
                      <h3 className="text-white font-bold text-lg tracking-tight relative">{f.title}</h3>
                      <p className="text-white/55 text-sm mt-2 leading-relaxed relative">{f.desc}</p>
                    </div>
                  ))}
                </div>
              </section>

              {/* BIG CTA SECTION */}
              <section className="container-app pb-24 sm:pb-32">
                <div className="text-center max-w-2xl mx-auto">
                  <h2 className="heading-section text-white">
                    Built for the curious.
                  </h2>
                  <p className="body-large mt-5">
                    Whether you're a creator analyzing feedback, a researcher,
                    or just want to know what people really think — CommentLens
                    has you covered.
                  </p>
                </div>
              </section>
            </>
          )}
        </>
      )}

      {/* FOOTER */}
      <footer className="border-t border-white/5 mt-12 py-8">
        <div className="container-app text-center text-white/30 text-xs space-y-1">
          <p>CommentLens · Powered by Claude · YouTube Data API</p>
          <p>Analyzes up to 150 top comments per video</p>
        </div>
      </footer>
    </div>
  );
}
