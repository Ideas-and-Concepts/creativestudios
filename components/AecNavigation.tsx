"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, Building2, ClipboardList, FileText, FolderKanban, HardHat, LayoutDashboard, Menu, Settings, ShieldCheck, Wrench, X } from "lucide-react";
import { useEffect, useState } from "react";

const groups = [
  { label: "Workspace", items: [
    { label: "Dashboard", href: "/", icon: LayoutDashboard },
    { label: "Projects", href: "/projects", icon: FolderKanban },
    { label: "Documents", href: "/documents", icon: FileText },
    { label: "Notifications", href: "/notifications", icon: Bell },
    { label: "Reports", href: "/reports", icon: FileText },
  ] },
  { label: "Architecture", items: [
    { label: "Architecture", href: "/architecture", icon: Building2 },
    { label: "Drawings", href: "/drawings", icon: ClipboardList },
  ] },
  { label: "Engineering", items: [
    { label: "Engineering", href: "/engineering", icon: Wrench },
    { label: "MEP", href: "/mep", icon: Wrench },
    { label: "BOQ", href: "/boq", icon: ClipboardList },
    { label: "RFIs", href: "/rfis", icon: FileText },
    { label: "Approvals", href: "/approvals", icon: ShieldCheck },
  ] },
  { label: "Construction", items: [
    { label: "Procurement", href: "/procurement", icon: ClipboardList },
    { label: "Construction", href: "/construction", icon: HardHat },
    { label: "Cost Control", href: "/cost-control", icon: ClipboardList },
    { label: "Tasks", href: "/tasks", icon: ClipboardList },
  ] },
];

function NavigationContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname() ?? "/";
  const isActive = (href: string) => href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
  return <nav className="cs-drawer-nav" aria-label="Modules">
    {groups.map((group) => <div className="cs-drawer-group" key={group.label}>
      <div className="cs-drawer-label">{group.label}</div>
      {group.items.map((item) => { const Icon = item.icon; return <Link key={item.href} href={item.href} onClick={onNavigate} className={`cs-drawer-link${isActive(item.href) ? " active" : ""}`}><Icon aria-hidden="true" />{item.label}</Link>; })}
    </div>)}
    <div className="cs-drawer-group"><div className="cs-drawer-label">System</div><Link href="/audit-log" onClick={onNavigate} className={`cs-drawer-link${isActive("/audit-log") ? " active" : ""}`}><ClipboardList aria-hidden="true" />Audit Trail</Link><Link href="/settings" onClick={onNavigate} className={`cs-drawer-link${isActive("/settings") ? " active" : ""}`}><Settings aria-hidden="true" />Settings</Link></div>
  </nav>;
}

function DrawerHeader({ close }: { close?: () => void }) {
  return <div className="cs-drawer-head"><img className="cs-drawer-brand" src="/assets/creative-studios.png" alt="Creative Studios" /><div><div className="cs-drawer-title">Creative Studios</div><div className="cs-drawer-subtitle">AEC Collaboration Platform</div></div>{close && <button className="cs-drawer-close" aria-label="Close menu" onClick={close}><X /></button>}</div>;
}

export default function AecNavigation() {
  const [open, setOpen] = useState(false);
  useEffect(() => { document.body.style.overflow = open ? "hidden" : ""; return () => { document.body.style.overflow = ""; }; }, [open]);
  return <>
    <style>{` .cs-shell-logo{position:fixed;z-index:1400;top:14px;left:18px;width:52px;height:52px;padding:7px;background:#fff;border:1px solid #e5e7eb;border-radius:50%;box-shadow:0 7px 22px rgba(15,23,42,.10);object-fit:contain}.cs-menu-button{position:fixed;z-index:1600;top:21px;left:82px;width:38px;height:38px;border:1px solid #e2e8f0;border-radius:8px;background:#fff;color:#334155;display:grid;place-items:center;cursor:pointer;box-shadow:0 4px 14px rgba(15,23,42,.08)}.cs-menu-button:hover{background:#f8fafc;color:#2563eb}.cs-menu-button svg{width:18px;height:18px}.cs-shell-actions{position:fixed;z-index:1600;top:21px;right:22px;display:flex;align-items:center;gap:5px}.cs-shell-action{width:38px;height:38px;border:1px solid #e2e8f0;border-radius:8px;background:#fff;color:#475569;display:grid;place-items:center;cursor:pointer}.cs-shell-action:hover{background:#f8fafc;color:#2563eb}.cs-shell-action svg{width:16px;height:16px}.cs-avatar{width:38px;height:38px;border:1px solid #dbe2ea;border-radius:50%;display:grid;place-items:center;color:#475569;background:#fff;font-size:10px;font-weight:800}.cs-nav-backdrop{position:fixed;inset:0;z-index:1450;background:rgba(15,23,42,.28);backdrop-filter:blur(2px)}.cs-drawer{position:fixed;z-index:1500;inset:0 auto 0 0;width:288px;max-width:86vw;height:100dvh;max-height:100dvh;background:#fff;border-right:1px solid #e5e7eb;box-shadow:18px 0 50px rgba(15,23,42,.18);display:flex;flex-direction:column;overflow:hidden}.cs-desktop-drawer{display:flex;z-index:1200;box-shadow:4px 0 22px rgba(15,23,42,.06);transform:none;animation:none}.cs-mobile-drawer{display:none;animation:csDrawerIn .16s ease-out}@keyframes csDrawerIn{from{transform:translateX(-100%)}to{transform:translateX(0)}}.cs-drawer-head{flex:0 0 auto;display:flex;align-items:center;gap:11px;padding:20px 18px 16px;border-bottom:1px solid #e5e7eb;background:#fff}.cs-drawer-brand{width:43px;height:43px;border:1px solid #e5e7eb;border-radius:50%;padding:5px;object-fit:contain}.cs-drawer-title{font-size:14px;font-weight:800;color:#111827}.cs-drawer-subtitle{font-size:9px;color:#64748b;margin-top:2px}.cs-drawer-close{margin-left:auto;width:32px;height:32px;border:0;background:transparent;color:#64748b;border-radius:7px;display:grid;place-items:center;cursor:pointer}.cs-drawer-close:hover{background:#f1f5f9;color:#111827}.cs-drawer-close svg{width:17px;height:17px}.cs-drawer-nav{flex:1 1 auto;min-height:0;overflow-y:auto;overflow-x:hidden;overscroll-behavior:contain;padding:12px 12px 24px;scrollbar-width:thin;scrollbar-color:#cbd5e1 transparent;scrollbar-gutter:stable}.cs-drawer-nav::-webkit-scrollbar{width:7px}.cs-drawer-nav::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:999px}.cs-drawer-group{margin-bottom:16px}.cs-drawer-label{font-size:9px;color:#94a3b8;font-weight:800;text-transform:uppercase;letter-spacing:.08em;padding:0 9px 6px}.cs-drawer-link{display:flex;align-items:center;gap:9px;min-height:36px;padding:9px 10px;border:1px solid transparent;border-radius:8px;text-decoration:none;color:#64748b;font-size:11px;font-weight:650;margin-bottom:2px;white-space:nowrap}.cs-drawer-link svg{width:15px;height:15px;stroke-width:1.8;flex:0 0 auto}.cs-drawer-link:hover{background:#f8fafc;color:#111827}.cs-drawer-link.active{background:#eff6ff;border-color:#dbeafe;color:#2563eb;font-weight:750}.cs-drawer-footer{flex:0 0 auto;border-top:1px solid #e5e7eb;padding:13px 16px;font-size:9px;color:#94a3b8;background:#fff}@media(min-width:901px){.cs-menu-button{display:none}.cs-shell-logo{display:none}.cs-shell-actions{z-index:1400}}@media(max-width:900px){.cs-desktop-drawer{display:none}.cs-mobile-drawer{display:flex}.cs-menu-button{z-index:1600}}@media(max-width:700px){.cs-shell-logo{top:10px;left:12px;width:44px;height:44px}.cs-menu-button{top:13px;left:66px;width:38px;height:38px}.cs-shell-actions{top:13px;right:10px}.cs-shell-action{display:none}.cs-avatar{width:38px;height:38px}}`}</style>
    <img className="cs-shell-logo" src="/assets/creative-studios.png" alt="Creative Studios" />
    <aside className="cs-drawer cs-desktop-drawer" aria-label="Creative Studios navigation"><DrawerHeader /><NavigationContent /><div className="cs-drawer-footer">Creative Studios · AEC Collaboration Platform</div></aside>
    <button className="cs-menu-button" aria-label={open ? "Close navigation menu" : "Open navigation menu"} aria-expanded={open} onClick={() => setOpen((value) => !value)}>{open ? <X /> : <Menu />}</button>
    <div className="cs-shell-actions" aria-label="Workspace actions"><Link className="cs-shell-action" aria-label="Notifications" href="/notifications"><Bell /></Link><span className="cs-avatar" aria-label="User profile">CS</span></div>
    {open && <><button className="cs-nav-backdrop" aria-label="Close navigation" onClick={() => setOpen(false)} /><aside className="cs-drawer cs-mobile-drawer" aria-label="Creative Studios navigation"><DrawerHeader close={() => setOpen(false)} /><NavigationContent onNavigate={() => setOpen(false)} /><div className="cs-drawer-footer">Creative Studios · AEC Collaboration Platform</div></aside></>}
  </>;
}
