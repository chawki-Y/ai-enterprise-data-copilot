import React from "react";
import { Loader2, SendHorizontal } from "lucide-react";

export function Composer({ value, onChange, onSubmit, loading }) {
  return (
    <form onSubmit={onSubmit} className="border-t border-white/10 bg-neutral-950/95 p-4">
      <div className="mx-auto flex max-w-5xl items-end gap-3 rounded-md border border-white/10 bg-neutral-900 p-2 focus-within:border-emerald-300/60">
        <textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          rows={1}
          placeholder="Ask about trades, books, counterparties, settlements, P&L..."
          className="max-h-36 min-h-11 flex-1 resize-none bg-transparent px-2 py-3 text-sm text-white outline-none placeholder:text-neutral-500"
        />
        <button
          type="submit"
          disabled={loading || !value.trim()}
          aria-label="Send question"
          className="grid h-11 w-11 shrink-0 place-items-center rounded-md bg-emerald-300 text-neutral-950 transition hover:bg-emerald-200 focus:outline-none focus:ring-2 focus:ring-emerald-100 disabled:cursor-not-allowed disabled:bg-neutral-700 disabled:text-neutral-400"
        >
          {loading ? <Loader2 className="animate-spin" size={19} aria-hidden="true" /> : <SendHorizontal size={19} aria-hidden="true" />}
        </button>
      </div>
    </form>
  );
}
