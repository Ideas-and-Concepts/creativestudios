"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, Building2, ClipboardList, FileText, FolderKanban, HardHat, LayoutDashboard, Menu, Search, Settings, ShieldCheck, Wrench, X, Sun } from "lucide-react";
import { useState } from "react";

const primary = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Projects", href: "/projects", icon: FolderKanban },
  { label: "Documents", href: "/documents", icon: FileText },
  { label: "Drawings", href: "/drawings", icon: ClipboardList },
  { label: "RFIs", href: "/rfis", icon: FileText },
  { label: "Tasks", href: "/tasks", icon: ClipboardList },
  { label: "Reports", href: "/reports", icon: FileText },
];

const more = [
  { label: "Architecture", href: "/architecture", icon: Building2 },
  { label: "Engineering", href: "/engineering", icon: Wrench },
  { label: "MEP", href: "/mep", icon: Wrench },
  { label: "BOQ", href: "/boq", icon: ClipboardList },
  { label: "Approvals", href: "/approvals", icon: ShieldCheck },
  { label: "Procurement", href: "/procurement", icon: ClipboardList },
  { label: "Construction", href: "/construction", icon: HardHat },
  { label: "Cost Control", href: "/cost-control", icon: ClipboardList },
  { label: "Settings", href: "/settings", icon: Settings },
];

export default function AecNavigation() {
  const pathname = usePathname() ?? "/";
  const [mobileOpen, setMobileOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const isActive = (href: string) => href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);

  return (
    <>
      <style>{`
        .cs-shell-logo{position:fixed;z-index:1300;top:14px;left:24px;width:52px;height:52px;padding:7px;background:#fff;border:1px solid #eef2f7;border-radius:50%;box-shadow:0 7px 22px rgba(15,23,42,.10);object-fit:contain}
        .cs-top{position:fixed;z-index:1200;top:14px;left:calc(50% - min(690px,calc(50vw - 28px)));right:calc(50% - min(690px,calc(50vw - 28px)));height:50px;background:rgba(255,255,255,.98);border:1px solid #e5e7eb;border-radius:10px;box-shadow:0 7px 24px rgba(15,23,42,.09);display:flex;align-items:center;padding:0 8px;backdrop-filter:blur(12px)}
        .cs-top-nav{display:flex;align-items:center;gap:2px;flex:1;min-width:0;overflow-x:auto;scrollbar-width:none}.cs-top-nav::-webkit-scrollbar{display:none}.cs-nav-link{display:flex;align-items:center;gap:6px;height:36px;padding:0 10px;border-radius:7px;text-decoration:none;color:#475569;font-size:10px;font-weight:650;white-space:nowrap}.cs-nav-link svg{width:13px;height:13px;stroke-width:1.8}.cs-nav-link:hover{background:#f8fafc;color:#111827}.cs-nav-link.active{color:#2563eb;background:#eff6ff;font-weight:750;box-shadow:inset 0 -2px 0 #2563eb}
        .cs-top-actions{display:flex;align-items:center;gap:2px;margin-left:4px}.cs-top-icon{border:0;background:transparent;color:#334155;width:32px;height:32px;border-radius:7px;display:grid;place-items:center;cursor:pointer}.cs-top-icon:hover{background:#f1f5f9}.cs-top-icon svg{width:15px;height:15px}.cs-avatar{width:28px;height:28px;border:1px solid #dbe2ea;border-radius:50%;display:grid;place-items:center;color:#475569;background:#fff;font-size:9px;font-weight:750;margin-left:3px}.cs-more-wrap{position:relative}.cs-more-menu{position:absolute;right:0;top:43px;width:210px;padding:6px;background:#fff;border:1px solid #e2e8f0;border-radius:9px;box-shadow:0 16px 38px rgba(15,23,42,.14)}.cs-more-menu a{display:flex;align-items:center;gap:8px;padding:8px 9px;border-radius:6px;color:#334155;text-decoration:none;font-size:10px}.cs-more-menu a:hover,.cs-more-menu a.active{background:#eff6ff;color:#2563eb}.cs-mobile-button{display:none}
        @media(max-width:900px){.cs-shell-logo{left:12px;top:10px;width:44px;height:44px}.cs-top{left:66px;right:10px;top:10px;height:44px}.cs-nav-link{padding:0 8px;font-size:9px}.cs-nav-link svg{display:none}.cs-top-icon{width:29px;height:29px}.cs-top-icon.search-desktop{display:none}.cs-more-menu{top:38px}.cs-mobile-button{display:grid;border:0;background:transparent;color:#334155;width:30px;height:30px;place-items:center;cursor:pointer}.cs-mobile-button svg{width:16px;height:16px}}
      `}</style>

      <img className="cs-shell-logo" src="/assets/creative-studios.png" alt="Creative Studios" />

      <header className="cs-top" aria-label="Creative Studios navigation">
        <button className="cs-mobile-button" aria-label="Toggle navigation" onClick={() => setMobileOpen((value) => !value)}>{mobileOpen ? <X /> : <Menu />}</button>
        <nav className={`cs-top-nav${mobileOpen ? " mobile-open" : ""}`}>
          {primary.map((item) => { const Icon = item.icon; return <Link key={item.href} href={item.href} className={`cs-nav-link${isActive(item.href) ? " active" : ""}`}><Icon aria-hidden="true" />{item.label}</Link>; })}
          <div className="cs-more-wrap">
            <button className={`cs-nav-link${more.some((item) => isActive(item.href)) ? " active" : ""}`} onClick={() => setMoreOpen((value) => !value)} aria-expanded={moreOpen}>More</button>
            {moreOpen && <div className="cs-more-menu">{more.map((item) => { const Icon = item.icon; return <Link key={item.href} href={item.href} className={isActive(item.href) ? "active" : ""} onClick={() => setMoreOpen(false)}><Icon size={13} />{item.label}</Link>; })}</div>}
          </div>
        </nav>
        <div className="cs-top-actions">
          <button className="cs-top-icon search-desktop" aria-label="Search"><Search /></button>
          <button className="cs-top-icon" aria-label="Theme"><Sun /></button>
          <button className="cs-top-icon" aria-label="Notifications"><Bell /></button>
          <span className="cs-avatar" aria-label="User profile">CS</span>
        </div>
      </header>
    </>
  );
}
