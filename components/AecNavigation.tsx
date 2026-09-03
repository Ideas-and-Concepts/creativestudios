"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, Building2, ClipboardList, FileText, FolderKanban, HardHat, LayoutDashboard, Menu, Search, Settings, ShieldCheck, Wrench, X } from "lucide-react";
import { useState } from "react";

const groups = [
  { name: "Architecture", items: [{ label: "Dashboard", href: "/", icon: LayoutDashboard }, { label: "Projects", href: "/projects", icon: FolderKanban }, { label: "Architecture", href: "/architecture", icon: Building2 }, { label: "Documents", href: "/documents", icon: FileText }, { label: "Drawings", href: "/drawings", icon: ClipboardList }] },
  { name: "Engineering", items: [{ label: "Engineering", href: "/engineering", icon: Wrench }, { label: "MEP", href: "/mep", icon: Wrench }, { label: "BOQ", href: "/boq", icon: ClipboardList }, { label: "RFIs", href: "/rfis", icon: FileText }, { label: "Approvals", href: "/approvals", icon: ShieldCheck }] },
  { name: "Construction", items: [{ label: "Procurement", href: "/procurement", icon: ClipboardList }, { label: "Construction", href: "/construction", icon: HardHat }, { label: "Cost Control", href: "/cost-control", icon: ClipboardList }, { label: "Tasks", href: "/tasks", icon: ClipboardList }, { label: "Reports", href: "/reports", icon: FileText }] },
  { name: "Workspace", items: [{ label: "Settings", href: "/settings", icon: Settings }] },
];

export default function AecNavigation() {
  const pathname = usePathname() ?? "/";
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (href: string) => href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);

  return (
    <>
      <style>{`
        .cs-side{position:fixed;z-index:1200;inset:0 auto 0 0;width:250px;background:#fff;border-right:1px solid #e5e7eb;padding:18px 14px;display:flex;flex-direction:column;overflow-y:auto}
        .cs-brand{display:flex;flex-direction:column;align-items:center;text-decoration:none;color:#111827;padding:4px 0 17px;border-bottom:1px solid #eef0f3}
        .cs-brand img{width:58px;height:58px;object-fit:contain;margin-bottom:9px}.cs-brand strong{font-size:13px;font-weight:700}.cs-brand span{font-size:9px;color:#94a3b8;margin-top:3px}
        .cs-section-title{margin:17px 8px 7px;font-size:9px;color:#2563eb;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
        .cs-side-nav{display:grid;gap:2px}.cs-nav-link{display:flex;align-items:center;gap:10px;padding:8px 9px;border-radius:7px;text-decoration:none;color:#475569;font-size:11px;font-weight:600}.cs-nav-link svg{width:14px;height:14px;stroke-width:1.8}.cs-nav-link:hover{background:#f8fafc;color:#111827}.cs-nav-link.active{background:#edf4ff;color:#2563eb;font-weight:700}
        .cs-side-bottom{margin-top:auto;padding-top:12px;border-top:1px solid #eef0f3;display:grid;gap:2px}
        .cs-top{position:fixed;z-index:1100;top:0;left:250px;right:0;height:64px;background:rgba(255,255,255,.96);border-bottom:1px solid #e5e7eb;box-shadow:0 2px 14px rgba(15,23,42,.06);backdrop-filter:blur(10px);display:grid;grid-template-columns:1fr auto 1fr;align-items:center;padding:0 18px}
        .cs-menu-btn,.cs-top-icon{border:0;background:transparent;color:#334155;width:34px;height:34px;border-radius:7px;display:grid;place-items:center;cursor:pointer}.cs-menu-btn:hover,.cs-top-icon:hover{background:#f1f5f9}.cs-top-center{justify-self:center}.cs-top-center img{width:36px;height:36px;object-fit:contain}.cs-top-actions{justify-self:end;display:flex;align-items:center;gap:4px}.cs-avatar{width:29px;height:29px;border:1px solid #dbe2ea;border-radius:50%;display:grid;place-items:center;color:#475569;background:#fff;margin-left:3px}.cs-avatar svg{width:16px;height:16px}
        .cs-search{display:flex;align-items:center;gap:7px;border:1px solid #e5e7eb;border-radius:7px;padding:6px 9px;color:#94a3b8;font-size:10px;margin-right:4px}.cs-search svg{width:14px;height:14px}
        .cs-mobile-backdrop{display:none}
        @media(max-width:900px){.cs-side{transform:translateX(-101%);transition:transform .2s ease;box-shadow:10px 0 35px rgba(15,23,42,.12)}.cs-side.open{transform:translateX(0)}.cs-top{left:0}.cs-mobile-backdrop{display:block;position:fixed;inset:0;background:rgba(15,23,42,.22);z-index:1150}.cs-search{display:none}}
      `}</style>

      {mobileOpen && <button className="cs-mobile-backdrop" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />}

      <aside className={`cs-side${mobileOpen ? " open" : ""}`} aria-label="Creative Studios navigation">
        <Link href="/" className="cs-brand" onClick={() => setMobileOpen(false)}>
          <img src="/assets/creative-studios.png" alt="Creative Studios" />
          <strong>Creative Studios</strong>
          <span>AEC Collaboration Platform</span>
        </Link>

        {groups.map((group) => (
          <section key={group.name}>
            <div className="cs-section-title">{group.name}</div>
            <nav className="cs-side-nav">
              {group.items.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                return <Link key={item.href} href={item.href} className={`cs-nav-link${active ? " active" : ""}`} onClick={() => setMobileOpen(false)}><Icon aria-hidden="true" />{item.label}</Link>;
              })}
            </nav>
          </section>
        ))}

        <div className="cs-side-bottom">
          <Link href="/settings" className={`cs-nav-link${isActive("/settings") ? " active" : ""}`} onClick={() => setMobileOpen(false)}><Settings aria-hidden="true" />Settings</Link>
          <a className="cs-nav-link" href="https://creativestudios.streamlit.app/" target="_blank" rel="noreferrer"><LayoutDashboard aria-hidden="true" />Streamlit Cloud</a>
        </div>
      </aside>

      <header className="cs-top">
        <button className="cs-menu-btn" aria-label="Open navigation" onClick={() => setMobileOpen((value) => !value)}>{mobileOpen ? <X /> : <Menu />}</button>
        <Link href="/" className="cs-top-center" aria-label="Creative Studios home"><img src="/assets/creative-studios.png" alt="" /></Link>
        <div className="cs-top-actions">
          <div className="cs-search"><Search />Search</div>
          <button className="cs-top-icon" aria-label="Search"><Search /></button>
          <button className="cs-top-icon" aria-label="Notifications"><Bell /></button>
          <span className="cs-avatar" aria-label="User profile"><span style={{fontSize:"11px",fontWeight:700}}>CS</span></span>
        </div>
      </header>
    </>
  );
}
