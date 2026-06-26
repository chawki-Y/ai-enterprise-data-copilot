import React, { useEffect } from "react";
import { Bot, Code2, PanelRightOpen, ServerCog } from "lucide-react";

const sampleQuestions = [
  "Give me an operations morning summary.",
  "Why was trade TRD-20260625-000004 rejected?",
  "Is any market data stale?",
  "Summarize today's P&L.",
];

export default function App() {
  useEffect(() => {
    if (!window.TradeOpsCopilot) {
      return undefined;
    }

    const instance = window.TradeOpsCopilot.init({
      apiBaseUrl: "",
      title: "Trade Ops Copilot",
      subtitle: "Embedded assistant demo",
      buttonLabel: "Ask Copilot",
    });

    return () => instance.destroy();
  }, []);

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950">
      <section className="mx-auto grid min-h-screen max-w-6xl content-center gap-8 px-5 py-10">
        <div className="max-w-3xl">
          <p className="text-sm font-bold uppercase tracking-wide text-emerald-700">Standalone template</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
            Embeddable Trade Operations Copilot
          </h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-600">
            This page is only a test shell. The actual copilot is a reusable widget that can be
            imported into any website with one script tag and one initialization call.
          </p>
        </div>

        <section className="grid gap-4 md:grid-cols-3">
          <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <PanelRightOpen className="text-emerald-700" size={28} />
            <h2 className="mt-4 text-lg font-semibold">Right-side panel</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              A floating button opens the assistant inside a fixed panel on the right side of the
              host website.
            </p>
          </article>

          <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <ServerCog className="text-emerald-700" size={28} />
            <h2 className="mt-4 text-lg font-semibold">Existing API aware</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              The FastAPI agent reads from the Trade Operations Node API instead of duplicating its
              trade, market data, audit, and operations logic.
            </p>
          </article>

          <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <Bot className="text-emerald-700" size={28} />
            <h2 className="mt-4 text-lg font-semibold">Agent responses</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              It can investigate rejected trades, summarize P&L, explain market data freshness, and
              highlight operational risks.
            </p>
          </article>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <Code2 className="text-emerald-700" size={22} />
            <h2 className="text-lg font-semibold">Import snippet</h2>
          </div>
          <pre className="mt-4 overflow-x-auto rounded-md bg-slate-950 p-4 text-sm text-emerald-100">
            <code>{`<script src="http://127.0.0.1:5173/trade-ops-copilot.js"></script>
<script>
  window.TradeOpsCopilot.init({
    apiBaseUrl: "http://127.0.0.1:8000",
    title: "Trade Ops Copilot"
  });
</script>`}</code>
          </pre>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold">Try these prompts from the floating button</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {sampleQuestions.map((question) => (
              <span
                key={question}
                className="rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700"
              >
                {question}
              </span>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}
