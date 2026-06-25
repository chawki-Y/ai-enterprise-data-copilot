import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  BriefcaseBusiness,
  Landmark,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  ShieldCheck,
} from "lucide-react";

import { ChatMessage } from "./components/ChatMessage.jsx";
import { Composer } from "./components/Composer.jsx";
import { Sidebar } from "./components/Sidebar.jsx";
import { askQuestion, fetchHistory, fetchSampleQuestions } from "./lib/api.js";

const fallbackExamples = [
  "Show trades pending validation",
  "Show failed settlements this week",
  "Show P&L by book",
  "Show top 5 counterparties by exposure",
  "Show trades by instrument",
  "Show market value by portfolio",
  "Show trades booked today",
  "Show settlement status by counterparty",
];

const initialMessages = [
  {
    id: "welcome",
    role: "assistant",
    content:
      "Ask a capital markets operations question. I will generate safe SQL, run it against PostgreSQL, and return the answer, query, and result set.",
    sql:
      "SELECT b.name AS book, b.desk, ROUND(SUM(t.pnl)::numeric, 2) AS total_pnl\nFROM trades t\nJOIN books b ON b.id = t.book_id\nGROUP BY b.name, b.desk\nORDER BY total_pnl DESC\nLIMIT 100",
    columns: ["book", "desk", "total_pnl"],
    rows: [
      { book: "IR_EUR_SWAP", desk: "Rates", total_pnl: 182400 },
      { book: "FX_G10_FORWARD", desk: "FX", total_pnl: 103200 },
      { book: "EQ_INDEX_DELTA1", desk: "Equities", total_pnl: 71500 },
      { book: "CR_CASH_BONDS", desk: "Credit", total_pnl: 12750 },
    ],
  },
];

function Metric({ icon: Icon, label, value, tone }) {
  return (
    <div className="rounded-md border border-white/10 bg-neutral-900/80 p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-neutral-500">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
        </div>
        <div className={`grid h-10 w-10 place-items-center rounded-md ${tone}`}>
          <Icon size={19} aria-hidden="true" />
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [examples, setExamples] = useState(fallbackExamples);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [desktopSidebarOpen, setDesktopSidebarOpen] = useState(true);

  const assistantReplyCount = useMemo(
    () => messages.filter((message) => message.role === "assistant").length,
    [messages],
  );

  useEffect(() => {
    fetchHistory().then(setHistory).catch(() => setHistory([]));
    fetchSampleQuestions()
      .then((questions) => setExamples(questions.length ? questions : fallbackExamples))
      .catch(() => setExamples(fallbackExamples));
  }, []);

  async function submitQuestion(question) {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    setInput("");
    setSidebarOpen(false);
    setLoading(true);
    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", content: trimmed },
    ]);

    try {
      const response = await askQuestion(trimmed);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
          sql: response.sql,
          columns: response.columns,
          rows: response.rows,
        },
      ]);
      fetchHistory().then(setHistory).catch(() => {});
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          type: "error",
          content: error.message,
          columns: [],
          rows: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    submitQuestion(input);
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-neutral-950 text-neutral-100">
      <div className="flex h-screen overflow-hidden">
        <div
          className={`fixed inset-y-0 left-0 z-40 w-80 transform transition lg:static lg:translate-x-0 ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          } ${desktopSidebarOpen ? "lg:block" : "lg:hidden"}`}
        >
          <Sidebar history={history} examples={examples} onExampleClick={submitQuestion} />
        </div>

        {sidebarOpen && (
          <button
            className="fixed inset-0 z-30 bg-black/70 lg:hidden"
            aria-label="Close sidebar"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <main className="flex min-w-0 flex-1 flex-col">
          <header className="flex items-center justify-between border-b border-white/10 bg-neutral-950/95 px-4 py-3">
            <div className="flex items-center gap-3">
              <button
                type="button"
                aria-label="Open sidebar"
                onClick={() => setSidebarOpen(true)}
                className="grid h-10 w-10 place-items-center rounded-md border border-white/10 text-neutral-200 transition hover:bg-white/10 lg:hidden"
              >
                <Menu size={20} aria-hidden="true" />
              </button>
              <div className="grid h-10 w-10 place-items-center rounded-md bg-emerald-400 text-neutral-950">
                <Landmark size={20} aria-hidden="true" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">Capital Markets Data Copilot</p>
                <p className="text-xs text-neutral-500">Trade lifecycle analytics</p>
              </div>
            </div>

            <div className="hidden items-center gap-3 text-xs text-neutral-400 sm:flex">
              <span className="flex items-center gap-2 rounded-md border border-emerald-300/20 bg-emerald-300/10 px-3 py-2 text-emerald-200">
                <ShieldCheck size={15} aria-hidden="true" />
                Read-only SQL
              </span>
              <span className="rounded-md border border-white/10 px-3 py-2">
                {assistantReplyCount} assistant replies
              </span>
            </div>

            <button
              type="button"
              aria-label={desktopSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
              onClick={() => setDesktopSidebarOpen((current) => !current)}
              className="hidden h-10 w-10 place-items-center rounded-md border border-white/10 text-neutral-400 transition hover:bg-white/10 lg:grid"
            >
              {desktopSidebarOpen ? (
                <PanelLeftClose size={18} aria-hidden="true" />
              ) : (
                <PanelLeftOpen size={18} aria-hidden="true" />
              )}
            </button>
          </header>

          <div className="flex-1 overflow-y-auto">
            <div className="mx-auto flex max-w-6xl flex-col gap-5 px-4 py-6">
              <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <Metric
                  icon={BriefcaseBusiness}
                  label="Lifecycle Coverage"
                  value="Trades"
                  tone="bg-cyan-300/15 text-cyan-200"
                />
                <Metric
                  icon={BarChart3}
                  label="Analytics"
                  value="P&L"
                  tone="bg-emerald-300/15 text-emerald-200"
                />
                <Metric
                  icon={Activity}
                  label="Controls"
                  value="Validation"
                  tone="bg-amber-300/15 text-amber-200"
                />
                <Metric
                  icon={ShieldCheck}
                  label="Safety"
                  value="SELECT only"
                  tone="bg-violet-300/15 text-violet-200"
                />
              </section>

              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}

              {loading && (
                <ChatMessage
                  message={{
                    id: "loading",
                    role: "assistant",
                    content: "Generating SQL, checking safety rules, querying PostgreSQL, and formatting results...",
                  }}
                />
              )}
            </div>
          </div>

          <Composer value={input} onChange={setInput} onSubmit={handleSubmit} loading={loading} />
        </main>
      </div>
    </div>
  );
}
