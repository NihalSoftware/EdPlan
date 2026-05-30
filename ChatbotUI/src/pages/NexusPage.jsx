import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FaBookOpen, FaClipboardList, FaGraduationCap, FaRobot, FaShieldAlt, FaUniversity, FaUser } from "react-icons/fa";
import { FiCalendar } from "react-icons/fi";
import AgentCard from "../components/nexus/AgentCard.jsx";

const cardIcons = {
  student: FaUser,
  university: FaUniversity,
  program: FaShieldAlt,
  year: FiCalendar,
  plans: FaClipboardList,
  schedules: FaBookOpen,
  recommendations: FaGraduationCap,
  confidence: FaRobot,
};

const agentStyles = {
  pathfinder: {
    accent: "#1668DC",
    accentBg: "#E8F1FF",
    Icon: FaRobot,
  },
  schedulepilot: {
    accent: "#059669",
    accentBg: "#E6F7EE",
    Icon: FaRobot,
  },
  coursecompass: {
    accent: "#7C3AED",
    accentBg: "#F0E7FF",
    Icon: FaRobot,
  },
};

const NexusPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/assets/nexus_data.json")
      .then((res) => res.json())
      .then((json) => setData(json))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <section className="p-6 min-h-screen bg-[#F4F7FC]">
        <div className="mx-auto flex max-w-6xl items-center justify-center py-32 text-slate-500">
          Loading Nexus...
        </div>
      </section>
    );
  }

  if (!data) {
    return (
      <section className="p-6 min-h-screen bg-[#F4F7FC]">
        <div className="mx-auto max-w-6xl rounded-[24px] bg-white p-10 shadow-sm border border-[#DCE3F0]">Unable to load Nexus content.</div>
      </section>
    );
  }

  const { overview, agents, activity, insights } = data;

  const overviewCards = [
    { key: "student", label: "Student", value: overview.student, Icon: cardIcons.student, iconBg: "bg-[#E8F1FF]", iconColor: "#1668DC" },
    { key: "university", label: "University", value: overview.university, Icon: cardIcons.university, iconBg: "bg-[#E8F1FF]", iconColor: "#1668DC" },
    { key: "program", label: "Program", value: overview.program, Icon: cardIcons.program, iconBg: "bg-[#E8F1FF]", iconColor: "#1668DC" },
    { key: "year", label: "Academic Year", value: overview.year, Icon: cardIcons.year, iconBg: "bg-[#E8F1FF]", iconColor: "#1668DC" },
  ];

  const statCards = [
    { key: "plans", label: "Education Plans", value: overview.stats[0].value, detail: overview.stats[0].detail, Icon: cardIcons.plans, accent: "#1668DC" },
    { key: "schedules", label: "Schedules", value: overview.stats[1].value, detail: overview.stats[1].detail, Icon: cardIcons.schedules, accent: "#059669" },
    { key: "recommendations", label: "Recommendations", value: overview.stats[2].value, detail: overview.stats[2].detail, Icon: cardIcons.recommendations, accent: "#7C3AED" },
    { key: "confidence", label: "AI Confidence", value: overview.stats[3].value, detail: overview.stats[3].detail, Icon: cardIcons.confidence, accent: "#F97316" },
  ];

  return (
    <section className="p-6 min-h-screen bg-[#F4F7FC]">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="rounded-[24px] border border-[#DCE3F0] bg-white p-8 shadow-sm">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
            <div className="max-w-3xl">
              <p className="text-xs uppercase tracking-[0.4em] text-slate-400">EdPlan Nexus</p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-slate-900">AI-powered academic intelligence center</h1>
              <p className="mt-4 text-base leading-7 text-slate-600">
                Explore your academic roadmap, optimize your semester schedule, and discover course recommendations powered by intelligent academic agents.
              </p>
            </div>

            <Link
              to="/nexus/pathfinder"
              className="inline-flex h-12 items-center justify-center rounded-full bg-[#1668DC] px-6 text-sm font-semibold text-white transition hover:bg-[#1659c9]"
            >
              Launch PathFinder
            </Link>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-4">
          {overviewCards.map((card) => (
            <div key={card.key} className="rounded-[20px] border border-[#DCE3F0] bg-white p-5 shadow-sm min-w-0">
              <div className="flex items-start gap-4">
                <div className={`flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl ${card.iconBg}`}>
                  <card.Icon className="h-5 w-5" style={{ color: card.iconColor }} />
                </div>
                <div className="min-w-0">
                  <p className="text-xs uppercase tracking-[0.35em] text-slate-400">{card.label}</p>
                  <p className="mt-3 text-lg font-semibold leading-snug text-slate-900 break-words whitespace-normal">{card.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid gap-4 lg:grid-cols-4">
          {statCards.map((card) => (
            <div key={card.key} className="rounded-[20px] border border-[#DCE3F0] bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between gap-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl" style={{ backgroundColor: `${card.accent}1A`, color: card.accent }}>
                  <card.Icon className="h-5 w-5" />
                </div>
                <div className="text-right">
                  <p className="text-xs uppercase tracking-[0.35em] text-slate-400">{card.label}</p>
                  <p className="mt-3 text-2xl font-semibold text-slate-900">{card.value}</p>
                </div>
              </div>
              <p className="mt-4 text-sm text-slate-500">{card.detail}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          {agents.map((agent) => {
            const style = agentStyles[agent.id] || agentStyles.pathfinder;
            return (
              <AgentCard
                key={agent.id}
                Icon={style.Icon}
                accent={style.accent}
                accentBg={style.accentBg}
                title={agent.name}
                description={agent.description}
                metrics={agent.metrics}
                buttonText={agent.buttonText}
                link={agent.link}
              />
            );
          })}
        </div>

        <div className="grid gap-5 lg:grid-cols-[1.4fr_0.9fr]">
          <div className="rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">Recent Activity</h2>
                <p className="mt-2 text-sm text-slate-500">Track the latest AI-generated updates to your plan, schedule, and recommendations.</p>
              </div>
              <button className="rounded-full border border-[#DCE3F0] px-4 py-2 text-xs font-semibold text-slate-600">View all</button>
            </div>
            <div className="mt-6 space-y-4">
              {activity.map((item) => (
                <div key={item.title} className="rounded-3xl border border-[#E8EFFA] bg-slate-50 p-4">
                  <p className="font-semibold text-slate-900">{item.title}</p>
                  <p className="mt-1 text-sm text-slate-500">{item.time}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">AI Insights</h2>
                <p className="mt-2 text-sm text-slate-500">Personalized guidance the system has identified for your academic path.</p>
              </div>
              <button className="rounded-full border border-[#DCE3F0] px-4 py-2 text-xs font-semibold text-slate-600">View all</button>
            </div>
            <div className="mt-6 space-y-3">
              {insights.map((insight) => (
                <div key={insight} className="rounded-3xl border border-[#E8EFFA] bg-slate-50 p-4">
                  <p className="text-sm text-slate-700">{insight}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default NexusPage;
