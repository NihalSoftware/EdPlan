const number = (value) => value == null ? "—" : new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(value);

export function KpiCard({ metric }) {
  return <article className={`management-kpi tone-${metric.pillar.toLowerCase()}`}>
    <span>{metric.label}</span><strong>{number(metric.value)}</strong>
    <p>{metric.status === "available" ? metric.delta == null ? "See definition for reporting scope" : `${metric.delta > 0 ? "+" : ""}${metric.delta}% vs prior period` : metric.status === "suppressed" ? "Withheld · small cohort" : "Not tracked yet"}</p>
    <details><summary>Definition & source</summary><p>{metric.definition}</p><p>Source: {metric.source}</p></details>
  </article>;
}

export function TrendChart({ rows }) {
  if (!rows.length) return <p className="management-unavailable">No releasable daily series. Data may be absent or contain small student cohorts.</p>;
  const maximum = Math.max(1, ...rows.map((row) => row.plans));
  const point = (row, index, key) => `${36 + index / Math.max(1, rows.length - 1) * 600},${155 - row[key] / maximum * 125}`;
  return <>
    <div className="management-chart-legend"><span>● Plans created</span><span>● Students creating plans</span></div>
    <svg className="management-trend" viewBox="0 0 660 185" role="img" aria-label={`Daily planning activity, ${rows[0].date} to ${rows.at(-1).date}. Exact counts in data table below.`}>
      {[0, 1, 2, 3].map((tick) => <g key={tick}><line x1="36" x2="636" y1={155 - tick * 41.67} y2={155 - tick * 41.67} stroke="#e8edf5" /><text x="29" y={159 - tick * 41.67} textAnchor="end">{number(maximum * tick / 3)}</text></g>)}
      <polyline points={rows.map((row, i) => point(row, i, "plans")).join(" ")} fill="none" stroke="#1768e7" strokeWidth="3" />
      <polyline points={rows.map((row, i) => point(row, i, "students")).join(" ")} fill="none" stroke="#1f9d65" strokeWidth="2" strokeDasharray="5 3" />
      {rows.length === 1 && <circle cx="36" cy={155 - rows[0].plans / maximum * 125} r="4" fill="#1768e7" />}
      <text x="36" y="179">{rows[0].date}</text><text x="636" y="179" textAnchor="end">{rows.at(-1).date}</text>
    </svg>
    <details className="management-data-table"><summary>View accessible data table</summary><div><table><caption>Daily UTC creation counts; students can appear on multiple days.</caption><thead><tr><th>Date</th><th>Plans</th><th>Students</th></tr></thead><tbody>{rows.map((r) => <tr key={r.date}><td>{r.date}</td><td>{r.plans}</td><td>{r.students}</td></tr>)}</tbody></table></div></details>
  </>;
}

export function BreakdownPanel({ rows, onSelect, noun = "program", total }) {
  if (!rows.length) return <p className="management-unavailable">No releasable {noun} breakdown. The entire panel is withheld when any cell is below the disclosure threshold.</p>;
  const max = Math.max(1, ...rows.map((r) => r.plans));
  return <><ul className="management-bars">{rows.slice(0, 8).map((row) => <li key={row.label}>
    <div><button onClick={() => onSelect(row.label)} title={`Filter by ${row.label}`}>{row.label}</button><b>{number(row.plans)} <small>plans</small></b></div>
    <div className="management-bar-track"><span style={{ width: `${row.plans / max * 100}%` }} /></div>
    <small>{number(row.students)} distinct students{total ? ` · ${Math.round(row.plans / total * 100)}% of filtered plans` : ""}</small>
  </li>)}</ul><details className="management-data-table"><summary>View all {noun} counts</summary><div><table><caption>Counts for selected plan cohort</caption><thead><tr><th>{noun}</th><th>Plans</th><th>Students</th></tr></thead><tbody>{rows.map((r) => <tr key={r.label}><td>{r.label}</td><td>{r.plans}</td><td>{r.students}</td></tr>)}</tbody></table></div></details></>;
}
