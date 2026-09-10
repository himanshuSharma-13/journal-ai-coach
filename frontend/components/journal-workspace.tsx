"use client";

import { FormEvent, useEffect, useState } from "react";

type JournalEntry = {
  id: string;
  content: string;
  occurred_at: string;
  source: string;
  created_at: string;
};

type EntryPage = { items: JournalEntry[]; total: number };
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function toLocalInputValue(date = new Date()) {
  const offset = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

export function JournalWorkspace() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [content, setContent] = useState("");
  const [occurredAt, setOccurredAt] = useState(toLocalInputValue());
  const [status, setStatus] = useState<"idle" | "loading" | "saving" | "error">("loading");
  const [message, setMessage] = useState("");

  async function loadEntries() {
    setStatus("loading");
    setMessage("");
    const params = new URLSearchParams();
    if (start) params.set("start", new Date(`${start}T00:00:00`).toISOString());
    if (end) params.set("end", new Date(`${end}T23:59:59`).toISOString());

    try {
      const response = await fetch(`${apiUrl}/api/v1/entries?${params.toString()}`);
      if (!response.ok) throw new Error("Could not load journal entries.");
      const page: EntryPage = await response.json();
      setEntries(page.items);
      setTotal(page.total);
      setStatus("idle");
    } catch {
      setStatus("error");
      setMessage(`Could not reach the API at ${apiUrl}. Start the FastAPI backend, then refresh.`);
    }
  }

  useEffect(() => {
    void loadEntries();
  }, [start, end]);

  async function saveEntry(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("saving");
    setMessage("");
    try {
      const response = await fetch(`${apiUrl}/api/v1/entries`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content,
          occurred_at: new Date(occurredAt).toISOString(),
          source: "manual"
        })
      });
      if (!response.ok) {
        const detail = await response.json();
        throw new Error(detail.detail?.[0]?.msg ?? "Your entry could not be saved.");
      }
      setContent("");
      setOccurredAt(toLocalInputValue());
      setMessage("Entry saved. It is now part of your long-term journal history.");
      await loadEntries();
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Your entry could not be saved.");
    }
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">Journal Foundation</p>
        <h1>Keep the whole story.</h1>
        <p className="hero-copy">A simple, private place to write freely today and understand your patterns only when you choose to ask later.</p>
      </section>

      <section className="workspace-grid">
        <form className="panel entry-form" onSubmit={saveEntry}>
          <div className="section-heading"><p className="panel-label">New Entry</p><span>Free-form writing</span></div>
          <label>
            What is on your mind?
            <textarea value={content} onChange={(event) => setContent(event.target.value)} minLength={20} maxLength={20000} required placeholder="Write freely. Your original words stay your source of truth." rows={12} />
          </label>
          <label>
            When did this happen?
            <input type="datetime-local" value={occurredAt} onChange={(event) => setOccurredAt(event.target.value)} required />
          </label>
          <button className="button-primary" disabled={status === "saving"}>{status === "saving" ? "Saving..." : "Save entry"}</button>
          {message && <p className={`form-message ${status === "error" ? "error" : ""}`}>{message}</p>}
        </form>

        <section className="panel timeline-panel">
          <div className="section-heading"><div><p className="panel-label">Journal Timeline</p><h2>{total} entries in your record</h2></div></div>
          <div className="filter-row"><input aria-label="Start date" type="date" value={start} onChange={(event) => setStart(event.target.value)} /><input aria-label="End date" type="date" value={end} onChange={(event) => setEnd(event.target.value)} /></div>
          <div className="entries-list">
            {status === "loading" && <p className="empty-state">Loading your journal history...</p>}
            {status === "error" && <p className="empty-state error">{message}</p>}
            {status === "idle" && entries.length === 0 && <p className="empty-state">Your first entry will appear here.</p>}
            {entries.map((entry) => <article className="entry-card" key={entry.id}><div className="entry-meta"><time dateTime={entry.occurred_at}>{new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(entry.occurred_at))}</time></div><p>{entry.content}</p></article>)}
          </div>
        </section>
      </section>
    </main>
  );
}
