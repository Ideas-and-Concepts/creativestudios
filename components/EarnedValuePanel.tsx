"use client";

import { useEffect, useState } from "react";

type Evm = {
  asOf: string;
  bac: number;
  pv: number;
  ev: number;
  ac: number;
  cv: number;
  sv: number;
  cpi: number | null;
  spi: number | null;
  eac: number;
  etc: number;
  vac: number;
  physicalProgress: number;
  financialProgress: number;
  baselineCoverage: number;
  activitiesCount: number;
};

const empty: Evm = { asOf: "", bac: 0, pv: 0, ev: 0, ac: 0, cv: 0, sv: 0, cpi: null, spi: null, eac: 0, etc: 0, vac: 0, physicalProgress: 0, financialProgress: 0, baselineCoverage: 0, activitiesCount: 0 };
const money = (value: number) => new Intl.NumberFormat(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
const ratio = (value: number | null) => value === null ? "N/A" : value.toFixed(3);
const health = (value: number | null) => value === null ? "No baseline" : value >= 1 ? "On target" : "Needs attention";

export default function EarnedValuePanel({ projectId }: { projectId: string }) {
  const [data, setData] = useState<Evm>(empty);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!projectId) return;
    let cancelled = false;
    setLoading(true); setError("");
    fetch(`/api/cost-control/earned-value?projectId=${encodeURIComponent(projectId)}`, { cache: "no-store" })
      .then(async (response) => {
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error ?? "Unable to load earned value metrics.");
        if (!cancelled) setData(payload.data ?? empty);
      })
      .catch((err) => { if (!cancelled) setError(err instanceof Error ? err.message : "Unable to load earned value metrics."); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [projectId]);

  if (!projectId) return null;

  return (
    <section className="workspace-card" style={{ marginBottom: "24px" }}>
      <div className="list-toolbar">
        <div><div className="section-label">Project Controls</div><h2>Earned Value Management</h2><p>Schedule and cost performance derived from BOQ, construction progress and approved actual-cost records.</p></div>
        <strong>{loading ? "Calculating..." : data.asOf ? `As of ${new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(data.asOf))}` : "Live"}</strong>
      </div>
      {error ? <div className="project-alert error" role="status">{error}</div> : <>
        <div className="project-stats" style={{ marginTop: "16px" }}>
          <div className="project-stat"><span>BAC</span><strong>{money(data.bac)}</strong></div>
          <div className="project-stat"><span>PV</span><strong>{money(data.pv)}</strong></div>
          <div className="project-stat"><span>EV</span><strong>{money(data.ev)}</strong></div>
          <div className="project-stat"><span>AC</span><strong>{money(data.ac)}</strong></div>
        </div>
        <div className="project-stats" style={{ marginTop: "12px" }}>
          <div className="project-stat"><span>CV</span><strong>{money(data.cv)}</strong></div>
          <div className="project-stat"><span>SV</span><strong>{money(data.sv)}</strong></div>
          <div className="project-stat"><span>CPI</span><strong>{ratio(data.cpi)}</strong></div>
          <div className="project-stat"><span>SPI</span><strong>{ratio(data.spi)}</strong></div>
          <div className="project-stat"><span>VAC</span><strong>{money(data.vac)}</strong></div>
        </div>
        <div className="project-stats" style={{ marginTop: "12px" }}>
          <div className="project-stat"><span>EAC</span><strong>{money(data.eac)}</strong></div>
          <div className="project-stat"><span>ETC</span><strong>{money(data.etc)}</strong></div>
          <div className="project-stat"><span>Physical Progress</span><strong>{data.physicalProgress.toFixed(1)}%</strong></div>
          <div className="project-stat"><span>Financial Progress</span><strong>{data.financialProgress.toFixed(1)}%</strong></div>
          <div className="project-stat"><span>Performance</span><strong>{health(data.cpi)} / {health(data.spi)}</strong></div>
        </div>
        <p style={{ marginTop: "14px" }}>Baseline coverage: {data.baselineCoverage} of {data.activitiesCount} construction activities have a BOQ value and planned start/finish dates. PV uses a linear time-phased baseline for those activities. Commitments are not treated as actual cost.</p>
      </>}
    </section>
  );
}
