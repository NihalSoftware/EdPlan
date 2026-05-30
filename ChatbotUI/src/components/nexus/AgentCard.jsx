import { Link } from "react-router-dom";

const AgentCard = ({ Icon, accent, accentBg, title, description, metrics, buttonText, link }) => (
  <div className="rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm shadow-slate-200/30 min-h-[430px] flex flex-col justify-between">
    <div>
      <div className="inline-flex h-16 w-16 items-center justify-center rounded-3xl" style={{ backgroundColor: accentBg, color: accent }}>
        {Icon && <Icon className="h-8 w-8" />}
      </div>

      <div className="mt-6 space-y-3">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-2xl font-semibold text-slate-900 break-words">{title}</h2>
        </div>
        <p className="text-sm leading-6 text-slate-600 break-words">{description}</p>
      </div>

      <div className="mt-8 grid gap-3 sm:grid-cols-3">
        {metrics.map((metric) => (
          <div key={metric.label} className="rounded-3xl border border-[#E6EAF3] bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">{metric.label}</p>
            <p className="mt-2 text-lg font-semibold text-slate-900 break-words whitespace-normal">{metric.value}</p>
          </div>
        ))}
      </div>
    </div>

    <Link
      to={link}
      className="mt-8 inline-flex h-12 items-center justify-center rounded-full text-sm font-semibold text-white transition"
      style={{ backgroundColor: accent, boxShadow: `0 12px 24px ${accent}20` }}
    >
      {buttonText}
    </Link>
  </div>
);

export default AgentCard;
