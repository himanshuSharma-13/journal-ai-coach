"use client";

import { FormEvent, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
type Theme = { theme: string; confidence: number; source: string };
type Entry = { id: string; content: string; occurred_at: string; themes: Theme[] };
type Insight = { id: string; question: string; answer: string; period_start: string; period_end: string; evidence: { entry_id: string; occurred_at: string; excerpt: string }[]; provider: string; created_at: string };

function localDate(date = new Date()) {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
}

function InsightCard({ insight }: { insight: Insight }) {
  // Older responses put Markdown list markers mid-paragraph; give those items their own lines.
  const answer = insight.answer.replace(/\s+- (?=\*\*)/g, "\n- ");

  return (
    <article className="insight-card">
      <div className="insight-card-header">
        <div>
          <p className="insight-kicker">{insight.provider === "groq" ? "AI reflection" : "Basic summary"}</p>
          <h3>{insight.question}</h3>
        </div>
        <time dateTime={insight.created_at}>{new Date(insight.created_at).toLocaleDateString()}</time>
      </div>
      <div className="insight-body"><ReactMarkdown>{answer}</ReactMarkdown></div>
      {insight.evidence.length > 0 && (
        <details className="insight-evidence">
          <summary>Journal evidence ({insight.evidence.length})</summary>
          <div className="insight-evidence-list">
            {insight.evidence.map((item) => (
              <p key={item.entry_id}><time dateTime={item.occurred_at}>{new Date(item.occurred_at).toLocaleDateString()}</time>{item.excerpt}</p>
            ))}
          </div>
        </details>
      )}
    </article>
  );
}

export function JournalWorkspace() {
  const [token, setToken] = useState("");
  const [mode, setMode] = useState<"login" | "register">("register");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [entries, setEntries] = useState<Entry[]>([]);
  const [content, setContent] = useState("");
  const [occurredAt, setOccurredAt] = useState(localDate());
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [question, setQuestion] = useState("What patterns do you notice in this period?");
  const [insights, setInsights] = useState<Insight[]>([]);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const request = async (path: string, options: RequestInit = {}) => {
    const response = await fetch(`${apiUrl}${path}`, { ...options, headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers } });
    if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail || "Something went wrong."); }
    return response.status === 204 ? null : response.json();
  };

  const load = async () => {
    if (!token) return;
    const params = new URLSearchParams();
    if (start) params.set("start", new Date(`${start}T00:00:00`).toISOString());
    if (end) params.set("end", new Date(`${end}T23:59:59`).toISOString());
    const [entryPage, insightList] = await Promise.all([request(`/api/v1/entries?${params}`), request("/api/v1/insights")]);
    setEntries(entryPage.items); setInsights(insightList);
  };

  useEffect(() => { setToken(localStorage.getItem("journal_token") ?? ""); }, []);
  useEffect(() => { load().catch((error) => setMessage(error.message)); }, [token, start, end]);

  async function authenticate(event: FormEvent) {
    event.preventDefault(); setBusy(true); setMessage("");
    try {
      const data = await request(`/api/v1/auth/${mode}`, { method: "POST", body: JSON.stringify({ email, password }) });
      localStorage.setItem("journal_token", data.access_token); setToken(data.access_token); setPassword("");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to continue."); }
    finally { setBusy(false); }
  }

  async function saveEntry(event: FormEvent) {
    event.preventDefault(); setBusy(true); setMessage("");
    try { await request("/api/v1/entries", { method: "POST", body: JSON.stringify({ content, occurred_at: new Date(occurredAt).toISOString() }) }); setContent(""); setOccurredAt(localDate()); await load(); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Unable to save."); }
    finally { setBusy(false); }
  }

  async function editEntry(entry: Entry) {
    const next = window.prompt("Edit your entry", entry.content); if (!next || next === entry.content) return;
    try { await request(`/api/v1/entries/${entry.id}`, { method: "PATCH", body: JSON.stringify({ content: next }) }); await load(); } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to edit."); }
  }
  async function removeEntry(id: string) {
    if (!window.confirm("Permanently delete this entry and its derived context?")) return;
    try { await request(`/api/v1/entries/${id}`, { method: "DELETE" }); await load(); } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to delete."); }
  }
  async function suggestThemes(id: string) { try { await request(`/api/v1/entries/${id}/suggest-themes`, { method: "POST" }); await load(); } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to suggest themes."); } }
  async function createInsight(event: { preventDefault: () => void }) {
    event.preventDefault(); setBusy(true); setMessage("");
    try { await request("/api/v1/insights", { method: "POST", body: JSON.stringify({ question, period_start: new Date(`${start || "2020-01-01"}T00:00:00`).toISOString(), period_end: new Date(`${end || new Date().toISOString().slice(0, 10)}T23:59:59`).toISOString() }) }); await load(); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Unable to create insight."); }
    finally { setBusy(false); }
  }

  if (!token) return <main className="page-shell auth-shell"><section className="hero"><p className="eyebrow">Long-term journal intelligence</p><h1>Keep the whole story.</h1><p className="hero-copy">Write freely today. Ask for grounded reflections when you are ready.</p></section><form className="panel auth-form" onSubmit={authenticate}><p className="panel-label">{mode === "register" ? "Create your space" : "Welcome back"}</p><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required /><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password (8+ characters)" minLength={8} required /><button className="button-primary" disabled={busy}>{busy ? "Working..." : mode === "register" ? "Create account" : "Sign in"}</button><button type="button" className="text-button" onClick={() => setMode(mode === "register" ? "login" : "register")}>{mode === "register" ? "Already have an account? Sign in" : "New here? Create an account"}</button>{message && <p className="form-message error">{message}</p>}</form></main>;

  return <main className="page-shell"><section className="hero compact"><div><p className="eyebrow">Your private record</p><h1>Keep the whole story.</h1></div><button className="button-secondary" onClick={() => { localStorage.removeItem("journal_token"); setToken(""); }}>Sign out</button></section><section className="workspace-grid"><form className="panel entry-form" onSubmit={saveEntry}><div className="section-heading"><p className="panel-label">New Entry</p><span>Free-form writing</span></div><textarea value={content} onChange={(e) => setContent(e.target.value)} minLength={20} required rows={10} placeholder="What is on your mind?" /><input type="datetime-local" value={occurredAt} onChange={(e) => setOccurredAt(e.target.value)} required /><button className="button-primary" disabled={busy}>Save entry</button>{message && <p className="form-message error">{message}</p>}<div className="insight-box"><p className="panel-label">Ask for insight</p><textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={3} /><button type="button" className="button-secondary" onClick={createInsight} disabled={busy}>Reflect on this period</button></div></form><section className="panel timeline-panel"><div className="section-heading"><div><p className="panel-label">Journal Timeline</p><h2>{entries.length} entries shown</h2></div></div><div className="filter-row"><input type="date" value={start} onChange={(e) => setStart(e.target.value)} /><input type="date" value={end} onChange={(e) => setEnd(e.target.value)} /></div><div className="entries-list">{entries.map((entry) => <article className="entry-card" key={entry.id}><div className="entry-meta"><time>{new Date(entry.occurred_at).toLocaleDateString()}</time><span>{entry.themes.map((theme) => theme.theme).join(" · ")}</span></div><p>{entry.content}</p><div className="card-actions"><button type="button" className="text-button" onClick={() => editEntry(entry)}>Edit</button><button type="button" className="text-button" onClick={() => suggestThemes(entry.id)}>Suggest themes</button><button type="button" className="text-button danger" onClick={() => removeEntry(entry.id)}>Delete</button></div></article>)}</div></section></section><section className="panel insight-results"><p className="panel-label">Reflections</p>{insights.map((insight) => <InsightCard key={insight.id} insight={insight} />)}</section></main>;
}
