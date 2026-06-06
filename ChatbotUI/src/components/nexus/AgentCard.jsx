import { Link } from "react-router-dom";
import { FaArrowRight, FaCalendarCheck, FaCheckCircle, FaCompass, FaRobot } from "react-icons/fa";

const ctaContent = {
  PathFinder: {
    label: "Student Planner",
    button: "Launch PathFinder",
  },
  SchedulePilot: {
    label: "Schedule Builder",
    button: "Launch SchedulePilot",
  },
  CourseCompass: {
    label: "Course Advisor",
    button: "Launch CourseCompass",
  },
};

const agentFeatures = {
  PathFinder: ["Degree Roadmaps", "Graduation Forecasting", "Credit & Course Optimization"],
  SchedulePilot: ["Smart Scheduling", "Workload Balancing", "Conflict Optimization"],
  CourseCompass: ["Personalized Recommendations", "Skill & Career Matching", "Prerequisite Guidance"],
};

const agentUsage = {
  PathFinder: "Today, 11:45 AM",
  SchedulePilot: "Today, 11:20 AM",
  CourseCompass: "Today, 10:55 AM",
};

const AgentIllustration = ({ title, accent, accentBg }) => {
  if (title === "SchedulePilot") {
    return (
      <div className="relative h-28 w-full min-w-[140px] flex-shrink-0 overflow-hidden rounded-[18px] bg-gradient-to-br from-emerald-50 to-white xl:h-[7.5rem]">
        <div className="absolute right-4 top-7 h-[4.5rem] w-[5.5rem] rotate-3 rounded-[12px] border border-emerald-100 bg-white shadow-lg shadow-emerald-100">
          <div className="flex h-5 items-center justify-center gap-2 rounded-t-[12px] bg-emerald-100">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
          </div>
          <div className="grid grid-cols-3 gap-1 p-2.5">
            {[1, 2, 3, 4, 5, 6].map((item) => (
              <span key={item} className="h-3 rounded bg-emerald-50" />
            ))}
          </div>
        </div>
        <FaCalendarCheck className="absolute bottom-6 right-7 h-8 w-8 text-emerald-500" />
      </div>
    );
  }

  if (title === "CourseCompass") {
    return (
      <div className="relative h-28 w-full min-w-[140px] flex-shrink-0 overflow-hidden rounded-[18px] bg-gradient-to-br from-violet-50 to-white xl:h-[7.5rem]">
        <div className="absolute bottom-4 right-5 flex h-20 w-20 rotate-[-15deg] items-center justify-center rounded-full border-[8px] border-violet-200 bg-white shadow-lg shadow-violet-100">
          <FaCompass className="h-8 w-8 text-violet-600" />
        </div>
        <span className="absolute right-6 top-5 h-5 w-8 rounded-full bg-violet-200" />
        <span className="absolute left-8 top-11 h-3 w-3 rounded-full bg-violet-300" />
      </div>
    );
  }

  return (
    <div className="relative h-28 w-full min-w-[140px] flex-shrink-0 overflow-hidden rounded-[18px] xl:h-[7.5rem]" style={{ background: `linear-gradient(135deg, ${accentBg}, #ffffff)` }}>
      <div className="absolute left-5 top-6 flex h-16 w-16 items-center justify-center rounded-[22px] shadow-lg" style={{ backgroundColor: accentBg, color: accent }}>
        <FaRobot className="h-8 w-8" />
      </div>
      <div className="absolute bottom-7 right-5 h-2 w-[4.5rem] rounded-full" style={{ backgroundColor: `${accent}33` }} />
      <div className="absolute bottom-9 right-12 h-14 w-2 rotate-[-12deg] rounded-full" style={{ backgroundColor: `${accent}55` }} />
      <span className="absolute bottom-14 right-9 h-6 w-6 rounded-full" style={{ backgroundColor: accent }} />
    </div>
  );
};

const AgentCard = ({ accent, accentBg, title, description, buttonText, link }) => {
  const cta = ctaContent[title] || {
    label: "AI Agent",
    button: buttonText,
  };
  const features = agentFeatures[title] || [];

  return (
    <div className="flex h-full min-h-[258px] w-full flex-col overflow-hidden rounded-[18px] border border-[#DCE3F0] bg-white shadow-sm shadow-slate-200/30">
      <div className="grid flex-1 gap-4 p-5 lg:grid-cols-[minmax(0,1fr)_150px] xl:grid-cols-[minmax(0,1fr)_160px]">
        <div className="flex min-w-0 flex-col">
          <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-xl font-semibold text-slate-900 break-words">{title}</h2>
          <span className="rounded-full px-2.5 py-1 text-xs font-semibold" style={{ backgroundColor: accentBg, color: accent }}>
              AI Agent
            </span>
          </div>
          <p className="mt-2.5 text-sm leading-5 text-slate-600 break-words">{description}</p>
          <div className="mt-4 space-y-1.5">
            {features.map((feature) => (
              <div key={feature} className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                <FaCheckCircle className="h-3.5 w-3.5" style={{ color: accent }} />
                {feature}
              </div>
            ))}
          </div>
          <p className="mt-auto pt-4 text-xs text-slate-500">Last used: {agentUsage[title] || "Today"}</p>
        </div>
        <AgentIllustration title={title} accent={accent} accentBg={accentBg} />
      </div>
      <div className="mt-auto flex flex-col gap-3 border-t border-[#E6EAF3] px-5 py-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs uppercase tracking-[0.25em] text-slate-400">{cta.label}</p>
        <Link
          to={link}
          className="inline-flex h-10 items-center justify-center gap-2.5 rounded-full px-4 text-xs font-semibold text-white transition"
          style={{ backgroundColor: accent, boxShadow: `0 12px 24px ${accent}20` }}
        >
          {cta.button}
          <FaArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </div>
  );
};

export default AgentCard;
