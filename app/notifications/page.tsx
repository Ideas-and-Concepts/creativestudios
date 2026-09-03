"use client";
import { useEffect, useState } from "react";

type Notification = { id: string; title: string; message: string; type: string; severity: string; isRead: boolean; createdAt: string; actionUrl?: string | null };
export default function NotificationsPage() {
  const [items, setItems] = useState<Notification[]>([]);
  const [error, setError] = useState("");
  async function load() { try { const r = await fetch("/api/notifications", { cache: "no-store" }); const j = await r.json(); if (!r.ok) throw new Error(j.error || "Unable to load notifications"); setItems(j.data || []); } catch (e) { setError(e instanceof Error ? e.message : "Unable to load notifications"); } }
  useEffect(() => { load(); }, []);
  async function markRead(id: string) { await fetch(`/api/notifications?id=${id}`, { method: "PATCH" }); await load(); }
  return <main className="cs-page"><div className="cs-page-header"><div><div className="cs-eyebrow">Workspace</div><h1 className="cs-page-title">Notifications</h1><p className="cs-page-copy">Project alerts and workflow events.</p></div><div className="cs-page-meta">{items.filter(x => !x.isRead).length} unread</div></div>{error && <p>{error}</p>}{items.length === 0 && !error && <p>No notifications recorded yet.</p>}<div style={{display:"grid",gap:10}}>{items.map(item => <article key={item.id} style={{border:"1px solid #e5e7eb",borderRadius:10,padding:16,background:"#fff"}}><div style={{display:"flex",justifyContent:"space-between",gap:12}}><strong>{item.title}</strong><span>{item.severity}</span></div><p>{item.message}</p><small>{item.type} · {new Date(item.createdAt).toLocaleString()}</small>{!item.isRead && <div style={{marginTop:10}}><button onClick={() => markRead(item.id)}>Mark as read</button></div>}</article>)}</div></main>;
}
