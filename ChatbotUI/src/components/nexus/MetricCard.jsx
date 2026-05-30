const MetricCard = ({ label, value, detail }) => (
  <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
    <p className="text-sm text-slate-500">{label}</p>
    <div className="mt-3 text-3xl font-semibold text-slate-900">{value}</div>
    {detail && <p className="mt-2 text-sm text-slate-500">{detail}</p>}
  </div>
);

export default MetricCard;
