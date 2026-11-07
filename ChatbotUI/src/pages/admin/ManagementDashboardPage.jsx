import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { LuChartNoAxesCombined, LuShieldCheck, LuUsers, LuGraduationCap, LuTarget, LuDownload, LuRefreshCw, LuMenu, LuX, LuArrowUpRight, LuInfo } from "react-icons/lu";
import { load } from "../../utils/storage.js";
import { checkAnalyticsAccess, exportAnalytics, getAnalytics } from "../../services/adminAnalytics.js";
import { BreakdownPanel, KpiCard, TrendChart } from "../../components/admin/AnalyticsPanels.jsx";
import "./ManagementDashboardPage.css";

const defaults = { period: "30" };
const navItems = [["overview", "Dashboard overview", LuChartNoAxesCombined], ["engagement", "Engagement", LuUsers], ["progress", "Plan quality & progress", LuGraduationCap], ["impact", "Impact & outcomes", LuTarget], ["methodology", "Definitions & coverage", LuInfo]];

export default function ManagementDashboardPage() {
  const [access, setAccess] = useState("checking");
  const [filters, setFilters] = useState(defaults);
  const [data, setData] = useState(null);
  const [options, setOptions] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [refresh, setRefresh] = useState(0);
  const [menu, setMenu] = useState(false);
  const [custom, setCustom] = useState({ start: "", end: "" });
  useEffect(() => {
    if (!load("AuthToken")) { setAccess("signed-out"); return; }
    const controller = new AbortController();
    checkAnalyticsAccess(controller.signal).then(() => setAccess("allowed")).catch((err) => {
      if (controller.signal.aborted) return;
      setAccess(err.response?.status === 403 ? "denied" : err.response?.status === 401 ? "signed-out" : "error");
    });
    return () => controller.abort();
  }, [refresh]);
  useEffect(() => {
    if (access !== "allowed") return;
    if (filters.period === "custom" && (!filters.start || !filters.end)) { setData(null); setBusy(false); setError(""); return; }
    const controller = new AbortController();
    setBusy(true); setError(""); setData(null);
    getAnalytics(filters, controller.signal).then(({ data: result }) => {
      if (controller.signal.aborted) return;
      setData(result);
      setOptions((previous) => Object.fromEntries(["institution", "program", "degree"].map((key) => [key, [...new Set([...(previous[key] || []), ...(result.options[key] || [])])].sort()])));
    }).catch((err) => {
      if (controller.signal.aborted) return;
      if ([401, 403].includes(err.response?.status)) setAccess(err.response.status === 401 ? "signed-out" : "denied");
      else setError("The analytics service could not load this report. Check the reporting range or try again.");
    }).finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [access, filters, refresh]);

  const filter = (key, value) => setFilters((old) => { const next = { ...old }; if (value) next[key] = value; else delete next[key]; return next; });
  const download = async () => {
    setExporting(true); setError("");
    try { await exportAnalytics(filters); } catch { setError("Export failed. Please retry after refreshing the report."); }
    finally { setExporting(false); }
  };

  if (access !== "allowed") return <main className="management-access"><LuShieldCheck aria-hidden="true" /><h1>{access === "checking" ? "Checking management access…" : access === "denied" ? "Management access required" : access === "signed-out" ? "Sign in to management reporting" : "Unable to verify access"}</h1><p>{access === "denied" ? "Your account does not have permission to read aggregate management analytics." : "Access is checked by the server before any reporting data is requested."}</p>{access === "signed-out" && <Link to="/login?next=%2Fadmin%2Fdashboard">Sign in</Link>}{access === "error" && <button onClick={() => setRefresh((x) => x + 1)}>Retry access check</button>}<Link to="/home">Return to student site</Link></main>;

  const metric = (id) => data?.metrics.find((m) => m.id === id);
  return <div className="management-shell">
    {menu && <button className="management-backdrop" aria-label="Close navigation" onClick={() => setMenu(false)} />}
    <aside className={`management-sidebar${menu ? " is-open" : ""}`}>
      <div className="management-brand"><span className="management-brand-symbol">✺</span><div>EdPlan<span>AI</span><small>STUDENT SUCCESS INTELLIGENCE</small></div><button aria-label="Close navigation" onClick={() => setMenu(false)}><LuX /></button></div>
      <p className="management-nav-label">MANAGEMENT WORKSPACE</p>
      <nav aria-label="Management navigation">{navItems.map(([id, label, Icon]) => <a key={id} href={`#${id}`} onClick={() => setMenu(false)}><Icon aria-hidden="true" />{label}</a>)}</nav>
      <div className="management-sidebar-note"><LuShieldCheck aria-hidden="true" /><strong>Aggregate insights only</strong><p>Student identities and private plan content stay outside this workspace.</p></div>
      <Link className="management-back-to-site" to="/home">Student site <LuArrowUpRight aria-hidden="true" /></Link>
    </aside>
    <main className="management-main" id="overview">
      <header className="management-topbar"><div><button className="management-menu" aria-label="Open navigation" onClick={() => setMenu(true)}><LuMenu /></button><span>Management <b>/ Dashboard overview</b></span></div><span className="management-access-badge"><LuShieldCheck aria-hidden="true" />Authorized aggregate access</span></header>
      <div className="management-body">
        <div className="management-heading"><div><p className="management-eyebrow">ENGAGEMENT · PROGRESS · IMPACT</p><h1>Student success, in perspective.</h1><p>A clear view of planning activity. An honest view of what comes next.</p></div><button className="management-export" disabled={!data || busy || exporting} onClick={download}><LuDownload aria-hidden="true" />{exporting ? "Exporting…" : "Export report"}</button></div>
        <section className="management-context" aria-label="Reporting context"><div><LuUsers aria-hidden="true" /><p><strong>Reporting population: {data?.population || "EdPlan AI users"}</strong><span>Active student accounts. Plan selections do not indicate enrollment.</span></p></div><span className="management-context-tag">PLATFORM PARTICIPATION</span></section>
        <section className="management-filters" aria-label="Report filters">
          <label>Reporting period<select value={filters.period} onChange={(e) => setFilters((old) => { const next = { ...old, period: e.target.value }; delete next.start; delete next.end; return next; })}><option value="7">Last 7 days</option><option value="30">Last 30 days</option><option value="90">Last 90 days</option><option value="all">All time</option><option value="custom">Custom range</option></select></label>
          {["institution", "program", "degree"].map((key) => <label key={key}>{key === "institution" ? "Selected plan institution" : key === "degree" ? "Credential" : "Academic program"}<select value={filters[key] || ""} onChange={(e) => filter(key, e.target.value)}><option value="">All {key === "degree" ? "credentials" : `${key}s`}</option>{(options[key] || []).map((value) => <option key={value} value={value}>{value}</option>)}</select></label>)}
          <button className="management-refresh" title="Refresh report" disabled={busy} onClick={() => setRefresh((x) => x + 1)}><LuRefreshCw aria-hidden="true" /><span>Refresh</span></button>
          <button className="management-reset" onClick={() => setFilters(defaults)}>Reset filters</button>
          {filters.period === "custom" && <form className="management-custom" onSubmit={(e) => { e.preventDefault(); setFilters((old) => ({ ...old, ...custom })); }}><label>From (UTC)<input required type="date" value={custom.start} onChange={(e) => setCustom((x) => ({ ...x, start: e.target.value }))} /></label><label>Through (UTC)<input required type="date" min={custom.start} value={custom.end} onChange={(e) => setCustom((x) => ({ ...x, end: e.target.value }))} /></label><button>Apply dates</button></form>}
        </section>
        {error && <div className="management-error" role="alert">{error}<button onClick={() => setRefresh((x) => x + 1)}>Retry</button></div>}
        {busy && <div className="management-loading" role="status">Loading authorized aggregate data…</div>}
        {data && !busy && <>
          <div className="management-freshness"><span>{data.period_start ? `${data.period_start.slice(0, 10)} — ${data.period_end_exclusive.slice(0, 10)} (end exclusive)` : "All-time report"} · UTC</span><span>Refreshed {new Date(data.refreshed_at).toLocaleString()} · on request <a href="#methodology">Methodology</a></span></div>
          <section className="management-pillars" aria-label="Three independently measured dimensions">
            <article><span className="management-pillar-icon"><LuUsers aria-hidden="true" /></span><div><h2>Engagement</h2><p>Are students using EdPlan AI?</p><strong>{metric("plans")?.status === "available" ? "Planning activity measured" : "Insufficient reportable cohort"}</strong><small>Stored plan creation · daily UTC cohorts</small></div></article>
            <article><span className="management-pillar-icon purple"><LuGraduationCap aria-hidden="true" /></span><div><h2>Progress</h2><p>Are plans academically sound?</p><strong>Not assessed for reporting</strong><small>Versioned academic validation required</small></div></article>
            <article><span className="management-pillar-icon green"><LuTarget aria-hidden="true" /></span><div><h2>Impact</h2><p>Are verified outcomes improving?</p><strong>Awaiting partner integration</strong><small>No enrollment or completion claims</small></div></article>
          </section>
          <section className="management-kpis" aria-label="Core reporting metrics">{["students", "planning_students", "plans", "shares"].map((id) => <KpiCard key={id} metric={metric(id)} />)}</section>
          <section className="management-kpis" aria-label="Planning coverage metrics">{["institutions", "average", "quality", "completion"].map((id) => <KpiCard key={id} metric={metric(id)} />)}</section>
          <div className="management-grid"><section className="management-panel" id="engagement"><div className="management-panel-heading"><div><h2>Planning activity trend</h2><p>Daily plan creations and distinct creators · UTC</p></div><span className="management-tag">ENGAGEMENT</span></div><TrendChart rows={data.trend} /></section><section className="management-panel"><div className="management-panel-heading"><div><h2>Attention required</h2><p>Aggregate evidence and next steps</p></div><span className="management-attention-count">{data.attention.length}</span></div><ul className="management-attention">{data.attention.map((item) => <li key={item.title}><strong>{item.title}</strong><p>{item.evidence}</p><details><summary>Recommended follow-up</summary><p>{item.action}</p><small>Owner: {item.owner}</small></details></li>)}</ul></section></div>
          <div className="management-grid"><section className="management-panel"><div className="management-panel-heading"><div><h2>Popular programs</h2><p>Plan counts · select a program to filter</p></div><span className="management-tag">DEMAND</span></div><BreakdownPanel rows={data.programs} onSelect={(v) => filter("program", v)} total={metric("plans")?.value} /></section><section className="management-panel"><div className="management-panel-heading"><div><h2>College distribution</h2><p>Selected plan institutions, not enrollment</p></div></div><BreakdownPanel rows={data.institutions} onSelect={(v) => filter("institution", v)} noun="institution" total={metric("plans")?.value} /></section></div>
          <div className="management-grid"><section className="management-panel" id="progress"><span className="management-tag purple">PROGRESS</span><h2>Plan quality & readiness</h2><p className="management-unavailable">{data.unavailable["Plan completion / academic validity"]}</p><p className="management-clarification">Planning completeness is distinct from completing college courses. No quality percentages are inferred from saved plans.</p></section><section className="management-panel" id="impact"><span className="management-tag green">IMPACT</span><h2>Verified outcomes</h2><p className="management-unavailable">{data.unavailable["Verified enrollment and outcomes"]}</p><p className="management-clarification">{data.unavailable["Advisor shares and review"]}</p></section></div>
          <section className="management-decision"><div><span className="management-eyebrow">YOUR FIVE-MINUTE BRIEFING</span><h2>From insight to next steps</h2><p>Deterministic narrative · no predictions or causal attribution</p></div><ul>{data.decision_note.map((note) => <li key={note}>{note}</li>)}</ul></section>
          <section className="management-panel management-methodology" id="methodology"><h2>Metric dictionary & reporting coverage</h2><p>{data.coverage}</p><details><summary>Privacy and small-cohort policy</summary><p>{data.privacy}</p></details><details><summary>Metric definitions, denominators & sources</summary><div className="management-data-table"><table><thead><tr><th>Metric / pillar</th><th>Definition</th><th>Source / availability</th></tr></thead><tbody>{data.metrics.map((m) => <tr key={m.id}><td><strong>{m.label}</strong><br />{m.pillar}</td><td>{m.definition}</td><td>{m.source}<br />{m.status}</td></tr>)}</tbody></table></div></details><details><summary>Untracked dimensions and future integrations</summary><ul>{Object.entries(data.unavailable).map(([label, reason]) => <li key={label}><strong>{label}: </strong>{reason}</li>)}</ul></details></section>
          <footer className="management-footer">Track engagement · Understand plan quality · Support advisors · Identify gaps · Measure verified impact</footer>
        </>}
      </div>
    </main>
  </div>;
}
