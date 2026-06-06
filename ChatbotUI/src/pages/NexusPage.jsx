import { useEffect, useRef, useState } from "react";
import {
  FaBookOpen,
  FaBullseye,
  FaCalendarAlt,
  FaChartLine,
  FaCheckCircle,
  FaClipboardList,
  FaGraduationCap,
  FaLayerGroup,
  FaRobot,
  FaShieldAlt,
} from "react-icons/fa";
import { FiCalendar } from "react-icons/fi";
import AgentCard from "../components/nexus/AgentCard.jsx";

const agentStyles = {
  pathfinder: {
    accent: "#6D28D9",
    accentBg: "#F0E7FF",
  },
  schedulepilot: {
    accent: "#059669",
    accentBg: "#E6F7EE",
  },
  coursecompass: {
    accent: "#7C3AED",
    accentBg: "#F0E7FF",
  },
};

const NexusPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const agentsSectionRef = useRef(null);

  useEffect(() => {
    fetch("/assets/nexus_data.json")
      .then((res) => res.json())
      .then((json) => setData(json))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <section className="min-h-screen bg-[#F4F7FC] px-4 py-6 sm:px-6 xl:px-8">
        <div className="mx-auto flex w-full max-w-[1400px] items-center justify-center py-32 text-slate-500">Loading Nexus...</div>
      </section>
    );
  }

  if (!data) {
    return (
      <section className="min-h-screen bg-[#F4F7FC] px-4 py-6 sm:px-6 xl:px-8">
        <div className="mx-auto w-full max-w-[1400px] rounded-[24px] border border-[#DCE3F0] bg-white p-10 shadow-sm">Unable to load Nexus content.</div>
      </section>
    );
  }

  const { overview, agents, activity, insights } = data;
  const progress = 45;

  const scrollToAgents = () => {
    agentsSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const overviewCards = [
    {
      label: "Program",
      value: "BS Computer Science",
      detail: "Bachelor of Science",
      Icon: FaGraduationCap,
      color: "#7C3AED",
      bg: "#F0E7FF",
    },
    {
      label: "Credits Earned",
      value: "30 / 72",
      detail: "Total Degree Credits",
      Icon: FaBookOpen,
      color: "#059669",
      bg: "#E6F7EE",
    },
    {
      label: "Current Semester",
      value: "Fall 2026",
      detail: "In Progress",
      Icon: FiCalendar,
      color: "#1668DC",
      bg: "#E8F1FF",
    },
    {
      label: "Graduation Progress",
      value: `${progress}%`,
      detail: "On Track",
      Icon: FaChartLine,
      color: "#F97316",
      bg: "#FFF1E7",
    },
    {
      label: "Expected Graduation",
      value: "Spring 2028",
      detail: "On Time",
      Icon: FaBullseye,
      color: "#7C3AED",
      bg: "#F0E7FF",
    },
  ];

  return (
    <section className="min-h-screen bg-[#F4F7FC] px-4 py-5 sm:px-6 xl:px-7">
      <div className="mx-auto w-full max-w-[1400px] space-y-5">
        <NexusHero student={overview.student} progress={progress} onTryNexus={scrollToAgents} />

        <div className="grid grid-cols-1 gap-3.5 md:grid-cols-2 xl:grid-cols-5">
          {overviewCards.map((card) => (
            <OverviewCard key={card.label} {...card} />
          ))}
        </div>

        <div ref={agentsSectionRef} className="scroll-mt-5 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {agents.map((agent) => {
            const style = agentStyles[agent.id] || agentStyles.pathfinder;
            return (
              <AgentCard
                key={agent.id}
                accent={style.accent}
                accentBg={style.accentBg}
                title={agent.name}
                description={agent.description}
                buttonText={agent.buttonText}
                link={agent.link}
              />
            );
          })}
        </div>

        <div className="grid grid-cols-1 gap-4 xl:grid-cols-[0.95fr_1.05fr_1.15fr]">
          <AcademicHealthPanel />
          <RecentActivityPanel activity={activity} />
          <InsightsPanel insights={insights} />
        </div>
      </div>
    </section>
  );
};

const NexusHero = ({ student, progress, onTryNexus }) => (
  <div className="relative w-full overflow-hidden rounded-[20px] border border-[#DCE3F0] bg-gradient-to-br from-[#F0E7FF] via-white to-[#E8F1FF] p-5 shadow-sm sm:p-6 xl:min-h-[226px]">
    <div className="pointer-events-none absolute right-12 top-7 hidden h-36 w-72 rounded-[50%] border border-[#C4B5FD] opacity-70 lg:block" />
    <div className="pointer-events-none absolute right-20 top-14 hidden h-24 w-64 rotate-[-18deg] rounded-[50%] border border-[#BFD4F7] opacity-70 lg:block" />
    <div className="pointer-events-none absolute right-24 top-10 hidden h-20 w-20 rounded-full bg-gradient-to-br from-[#1D4ED8] to-[#7C3AED] shadow-xl shadow-violet-200 lg:block" />
    <FaGraduationCap className="pointer-events-none absolute right-[7.75rem] top-14 hidden h-16 w-16 rotate-[-8deg] text-slate-900 drop-shadow-xl lg:block" />

    <div className="relative grid w-full gap-6 lg:grid-cols-[minmax(0,1fr)_200px] xl:grid-cols-[minmax(0,1fr)_220px_300px] xl:items-center">
      <div className="min-w-0">
        <p className="text-xs font-semibold text-[#6D28D9]">Welcome back, {student}</p>
        <h1 className="mt-4 max-w-3xl text-3xl font-semibold tracking-tight text-slate-900 xl:text-[2.65rem] xl:leading-tight">AI Academic Intelligence Center</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
          Track your academic journey, optimize your schedule, and get personalized recommendations from intelligent agents.
        </p>
        <div className="mt-5 grid w-full max-w-3xl gap-2 rounded-[12px] border border-[#DCE3F0] bg-white/75 p-3 shadow-sm md:grid-cols-3">
          <HeroMiniMetric Icon={FaCalendarAlt} label="Fall 2026" detail="Current Semester" />
          <HeroMiniMetric Icon={FaLayerGroup} label="BS Computer Science" detail="Your Program" />
          <HeroMiniMetric Icon={FaCalendarAlt} label="Spring 2028" detail="Expected Graduation" />
        </div>
      </div>

      <div className="flex justify-center">
        <div className="relative flex h-36 w-36 items-center justify-center rounded-full bg-white shadow-inner shadow-slate-200">
          <div
            className="absolute inset-0 rounded-full"
            style={{ background: `conic-gradient(#6D28D9 ${progress * 3.6}deg, #E5E7F4 0deg)` }}
          />
          <div className="relative flex h-24 w-24 flex-col items-center justify-center rounded-full bg-white text-center shadow-sm">
            <p className="text-3xl font-semibold text-slate-900">{progress}%</p>
            <p className="mt-1 text-xs font-semibold text-slate-500">Degree Progress</p>
            <FaGraduationCap className="mt-1.5 h-3.5 w-3.5 text-slate-700" />
          </div>
        </div>
      </div>

      <div className="hidden min-h-[158px] xl:flex xl:items-end xl:justify-center">
        <button
          type="button"
          onClick={onTryNexus}
          className="inline-flex h-10 items-center justify-center rounded-full bg-[#6D28D9] px-6 text-sm font-semibold text-white shadow-lg shadow-violet-200 transition hover:-translate-y-0.5 hover:bg-[#5B21B6]"
        >
          Try Nexus
        </button>
      </div>
    </div>
  </div>
);

const HeroMiniMetric = ({ Icon, label, detail }) => (
  <div className="flex items-center gap-2.5 border-[#E6EAF3] md:border-r md:last:border-r-0">
    <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-[9px] bg-[#EEF4FF] text-[#1668DC]">
      <Icon className="h-[1.125rem] w-[1.125rem]" />
    </span>
    <div className="min-w-0">
      <p className="text-xs font-semibold text-slate-900">{label}</p>
      <p className="text-xs text-slate-500">{detail}</p>
    </div>
  </div>
);

const OverviewCard = ({ label, value, detail, Icon, color, bg }) => (
  <div className="min-h-[96px] rounded-[16px] border border-[#DCE3F0] bg-white p-4 shadow-sm">
    <div className="flex items-start gap-3">
      <span className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-[14px]" style={{ backgroundColor: bg, color }}>
        <Icon className="h-5 w-5" />
      </span>
      <div className="min-w-0">
        <p className="text-xs font-semibold text-slate-500">{label}</p>
        <p className="mt-1.5 text-base font-semibold leading-snug text-slate-900 break-words">{value}</p>
        <p className="mt-0.5 text-xs text-slate-500">{detail}</p>
      </div>
    </div>
  </div>
);

const AcademicHealthPanel = () => (
  <div className="rounded-[18px] border border-[#DCE3F0] bg-white p-5 shadow-sm">
    <div className="flex items-center gap-2">
      <h2 className="text-base font-semibold text-slate-900">Academic Health</h2>
      <FaCheckCircle className="h-4 w-4 text-slate-400" />
    </div>
    <div className="mt-4 grid gap-4 md:grid-cols-[112px_1fr] md:items-center">
      <div className="relative flex h-28 w-28 items-center justify-center rounded-full bg-white">
        <div className="absolute inset-0 rounded-full" style={{ background: "conic-gradient(#059669 313deg, #E6EAF3 0deg)" }} />
        <div className="relative flex h-20 w-20 flex-col items-center justify-center rounded-full bg-white">
          <p className="text-3xl font-semibold text-slate-900">87</p>
          <p className="text-xs text-slate-500">/100</p>
        </div>
      </div>
      <div className="space-y-2.5">
        <HealthLine title="On track for graduation" detail="You are progressing as planned." positive />
        <HealthLine title="Balanced workload" detail="Your course load is well balanced." positive />
        <HealthLine title="Prerequisites clear" detail="You have no missing prerequisites." positive />
        <HealthLine title="Consider ML electives" detail="Great match for your interests." />
      </div>
    </div>
    <button type="button" className="mt-4 h-9 w-full rounded-[10px] border border-[#DCE3F0] text-xs font-semibold text-emerald-700">
      View Full Analysis
    </button>
  </div>
);

const HealthLine = ({ title, detail, positive = false }) => (
  <div className="flex items-start gap-2.5">
    <span className={`mt-1 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full ${positive ? "bg-emerald-50 text-emerald-600" : "bg-orange-50 text-orange-500"}`}>
      <FaCheckCircle className="h-3 w-3" />
    </span>
    <div>
      <p className="text-xs font-semibold text-slate-900">{title}</p>
      <p className="text-xs leading-4 text-slate-500">{detail}</p>
    </div>
  </div>
);

const RecentActivityPanel = ({ activity }) => (
  <div className="rounded-[18px] border border-[#DCE3F0] bg-white p-5 shadow-sm">
    <div className="flex items-center justify-between">
      <h2 className="text-base font-semibold text-slate-900">Recent Activity</h2>
      <button type="button" className="text-xs font-semibold text-[#1668DC]">View all</button>
    </div>
    <div className="mt-4 space-y-4">
      {activity.map((item, index) => {
        const ActivityIcon = [FaGraduationCap, FaCalendarAlt, FaBullseye][index % 3];
        return (
          <div key={item.title} className="flex gap-3">
            <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-[#EEF4FF] text-[#1668DC]">
              <ActivityIcon className="h-3.5 w-3.5" />
            </span>
            <div>
              <p className="text-xs font-semibold text-slate-900">{item.title}</p>
              <p className="mt-1 text-xs text-slate-500">{item.time}</p>
            </div>
          </div>
        );
      })}
      <div className="flex gap-3">
        <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-[#E8F1FF] text-[#1668DC]">
          <FaClipboardList className="h-3.5 w-3.5" />
        </span>
        <div>
          <p className="text-xs font-semibold text-slate-900">Academic profile updated</p>
          <p className="mt-1 text-xs text-slate-500">Yesterday, 04:30 PM</p>
        </div>
      </div>
    </div>
  </div>
);

const InsightsPanel = ({ insights }) => {
  const enrichedInsights = [
    "You are on track to graduate in Spring 2028. Great job staying consistent!",
    "Machine Learning electives align well with your goals. Consider adding more ML-related courses.",
    "Your current workload is well balanced. Keep up the good work!",
    "COMP-350 is recommended for next semester. Strong next step for your program.",
  ];

  return (
    <div className="rounded-[18px] border border-[#DCE3F0] bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-900">AI Insights</h2>
        <button type="button" className="text-xs font-semibold text-[#1668DC]">View all</button>
      </div>
      <div className="mt-4 space-y-2.5">
        {enrichedInsights.map((insight, index) => (
          <InsightRow key={insight} insight={insights[index] || insight} index={index} />
        ))}
      </div>
    </div>
  );
};

const InsightRow = ({ insight, index }) => {
  const InsightIcon = [FaCheckCircle, FaBookOpen, FaRobot, FaBullseye][index % 4];

  return (
    <div className="flex gap-3 rounded-[12px] border border-[#E6EAF3] bg-slate-50 p-3">
      <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-white text-[#7C3AED]">
        <InsightIcon className="h-3.5 w-3.5" />
      </span>
      <p className="text-xs leading-5 text-slate-700">{insight}</p>
    </div>
  );
};

export default NexusPage;
