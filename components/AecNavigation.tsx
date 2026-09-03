"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const groups = [
  { name: "Architecture", items: [{ label: "Projects", href: "/projects" }, { label: "Architecture", href: "/architecture" }, { label: "Documents", href: "/documents" }, { label: "Drawings", href: "/drawings" }] },
  { name: "Engineering", items: [{ label: "Engineering", href: "/engineering" }, { label: "MEP", href: "/mep" }, { label: "BOQ", href: "/boq" }, { label: "RFIs", href: "/rfis" }, { label: "Approvals", href: "/approvals" }] },
  { name: "Construction", items: [{ label: "Procurement", href: "/procurement" }, { label: "Construction", href: "/construction" }, { label: "Cost Control", href: "/cost-control" }, { label: "Tasks", href: "/tasks" }, { label: "Reports", href: "/reports" }] },
];

export default function AecNavigation() {
  const pathname = usePathname();

  return (
    <>
      <style>{`
        .aec-nav{position:sticky;top:0;z-index:1000;width:100%;background:#fff;border-bottom:1px solid #e2e8f0;box-shadow:0 2px 12px rgba(15,23,42,.06)}
        .aec-nav-inner{max-width:1500px;margin:0 auto;min-height:78px;padding:10px 20px;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:20px}
        .aec-brand{display:flex;align-items:center;justify-content:center;gap:10px;text-decoration:none;color:#0f172a;min-width:190px}.aec-brand img{width:48px;height:48px;object-fit:contain;display:block}.aec-brand-copy{text-align:left}.aec-brand strong{font-size:14px;line-height:1.1}.aec-brand span{display:block;color:#64748b;font-size:10px;margin-top:3px}
        .aec-menu{grid-column:1 / -1;display:flex;justify-content:center;align-items:center;gap:6px;flex-wrap:wrap}.aec-menu details{position:relative}.aec-menu summary{list-style:none;cursor:pointer;color:#475569;font-size:12px;font-weight:700;padding:9px 12px;border:1px solid transparent;border-radius:8px}.aec-menu summary::-webkit-details-marker{display:none}.aec-menu summary:hover,.aec-menu details[open] summary{color:#1d4ed8;background:#eff6ff;border-color:#bfdbfe}
        .aec-dropdown{position:absolute;top:calc(100% + 6px);left:0;min-width:190px;padding:7px;background:#fff;border:1px solid #dbe4f0;border-radius:10px;box-shadow:0 12px 30px rgba(15,23,42,.12)}.aec-dropdown a{display:block;padding:9px 10px;border-radius:7px;text-decoration:none;color:#475569;font-size:12px}.aec-dropdown a:hover,.aec-dropdown a.active{background:#eff6ff;color:#1d4ed8;font-weight:700}
        .aec-dashboard{justify-self:end;text-decoration:none;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:9px 12px;font-size:12px;font-weight:700}.aec-dashboard:hover{background:#dbeafe}
        @media(max-width:850px){.aec-nav-inner{grid-template-columns:1fr;gap:8px;padding:10px 14px}.aec-brand{justify-content:center}.aec-menu{grid-column:auto;justify-content:flex-start;overflow-x:auto;flex-wrap:nowrap;padding-bottom:2px}.aec-dashboard{justify-self:stretch;text-align:center}.aec-dropdown{position:fixed;left:14px;right:14px;top:138px}}
      `}</style>
      <header className="aec-nav">
        <div className="aec-nav-inner">
          <div />
          <Link href="/" className="aec-brand">
            <img src="/assets/creative-studios.png" alt="Creative Studios" />
            <div className="aec-brand-copy"><strong>Creative Studios</strong><span>AEC Collaboration Platform</span></div>
          </Link>
          <Link href="/" className="aec-dashboard">Dashboard</Link>
          <nav className="aec-menu" aria-label="AEC page navigation">
            {groups.map((group) => <details key={group.name}><summary>{group.name}</summary><div className="aec-dropdown">{group.items.map((item) => <Link key={item.href} href={item.href} className={pathname === item.href ? "active" : ""}>{item.label}</Link>)}</div></details>)}
          </nav>
        </div>
      </header>
    </>
  );
}
