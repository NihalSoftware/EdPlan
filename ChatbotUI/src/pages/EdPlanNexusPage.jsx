import { useNavigate } from "react-router-dom";
import {
	FaArrowUpRightFromSquare,
	FaBell,
	FaBuildingColumns,
	FaCalendarDays,
	FaChartLine,
	FaCircleNodes,
	FaGraduationCap,
	FaLightbulb,
	FaRegCompass,
	FaRocket,
	FaShieldHalved,
	FaWandMagicSparkles,
	FaUserGraduate,
} from "react-icons/fa6";
import { FaDollarSign } from "react-icons/fa";

const orbitAgents = [
	{ icon: FaGraduationCap, className: "top-[4%] left-1/2 -translate-x-1/2 text-indigo-600" },
	{ icon: FaCalendarDays, className: "top-[24%] right-[12%] text-blue-500" },
	{ icon: FaDollarSign, className: "bottom-[24%] right-[8%] text-emerald-500" },
	{ icon: FaLightbulb, className: "bottom-[5%] left-1/2 -translate-x-1/2 text-orange-500" },
	{ icon: FaBuildingColumns, className: "bottom-[24%] left-[12%] text-blue-600" },
	{ icon: FaUserGraduate, className: "top-[24%] left-[12%] text-slate-700" },
];

const agentCards = [
	{
		name: "PathCrafter",
		description:
			"Designs your personalized academic path based on your interests, goals, and career aspirations.",
		icon: FaCircleNodes,
		accent: "from-violet-500 to-indigo-600",
		shadow: "shadow-violet-200/70",
		path: "/edplan-nexus/pathcrafter",
	},
	{
		name: "SchedulePilot",
		description:
			"Optimizes your class schedules to avoid conflicts and maximize productivity.",
		icon: FaCalendarDays,
		accent: "from-blue-500 to-sky-600",
		shadow: "shadow-blue-200/70",
	},
	{
		name: "UniversityAdvisor",
		description:
			"Compares universities and programs to help you find the best fit.",
		icon: FaBuildingColumns,
		accent: "from-emerald-500 to-green-600",
		shadow: "shadow-emerald-200/70",
	},
	{
		name: "FinanceGuide",
		description:
			"Plans your finances with cost estimates, savings strategies, and financial aid opportunities.",
		icon: FaDollarSign,
		accent: "from-orange-400 to-orange-600",
		shadow: "shadow-orange-200/70",
	},
	{
		name: "CareerNavigator",
		description:
			"Explores career paths, required skills, and future opportunities aligned with your profile.",
		icon: FaChartLine,
		accent: "from-cyan-500 to-teal-600",
		shadow: "shadow-cyan-200/70",
	},
	{
		name: "ScholarshipScout",
		description:
			"Finds scholarships and grants you're eligible for to reduce your education costs.",
		icon: FaLightbulb,
		accent: "from-violet-500 to-purple-600",
		shadow: "shadow-purple-200/70",
	},
];

const featureItems = [
	{ title: "Smart Coordination", description: "Orchestrates all agents", icon: FaWandMagicSparkles },
	{ title: "Personalized for You", description: "Tailored to your goals", icon: FaCircleNodes },
	{ title: "Real-time Insights", description: "Data-driven recommendations", icon: FaRegCompass },
];

const RobotOrbit = () => (
	<div className="relative mx-auto flex h-[280px] w-full max-w-[360px] items-center justify-center overflow-hidden sm:h-[330px]">
		<div className="absolute h-[310px] w-[310px] rounded-full border border-indigo-100 sm:h-[360px] sm:w-[360px]" />
		<div className="absolute h-[240px] w-[240px] rounded-full border border-indigo-100 sm:h-[286px] sm:w-[286px]" />
		<div className="absolute h-[170px] w-[170px] rounded-full border border-indigo-200 sm:h-[206px] sm:w-[206px]" />
		<div className="absolute h-[106px] w-[106px] rounded-full border border-indigo-200 sm:h-[130px] sm:w-[130px]" />
		<div className="absolute h-[330px] w-[330px] rounded-full border border-dashed border-indigo-100 sm:h-[390px] sm:w-[390px]" />
		<div className="edplan-nexus-orbit absolute h-[240px] w-[240px] sm:h-[286px] sm:w-[286px]">
			{orbitAgents.map(({ icon: Icon, className }, index) => (
				<div
					key={index}
					className={`absolute flex h-14 w-14 items-center justify-center rounded-full border border-slate-100 bg-white text-lg shadow-xl shadow-indigo-100/70 ${className}`}
				>
					<Icon />
				</div>
			))}
		</div>

		<div className="relative flex h-24 w-24 items-center justify-center rounded-[2rem] bg-gradient-to-br from-indigo-50 to-violet-100 shadow-2xl shadow-indigo-200">
			<div className="absolute -top-7 h-6 w-3 rounded-full bg-indigo-500">
				<span className="absolute -top-2 left-1/2 h-4 w-4 -translate-x-1/2 rounded-full bg-indigo-500 shadow-lg shadow-indigo-300" />
			</div>
			<div className="absolute -left-3 h-10 w-4 rounded-full bg-indigo-500/80" />
			<div className="absolute -right-3 h-10 w-4 rounded-full bg-indigo-500/80" />
			<div className="flex h-14 w-20 items-center justify-center rounded-3xl bg-gradient-to-b from-indigo-600 to-indigo-800 shadow-inner">
				<div className="flex items-center gap-4">
					<span className="h-2.5 w-2.5 rounded-full bg-sky-100" />
					<span className="h-2.5 w-2.5 rounded-full bg-sky-100" />
				</div>
			</div>
			<div className="absolute bottom-5 h-1.5 w-8 rounded-full bg-sky-100" />
		</div>
	</div>
);

const AgentCard = ({ agent, onLearnMore }) => {
	const Icon = agent.icon;

	return (
		<article className="group rounded-2xl border border-slate-200/80 bg-white/90 p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-indigo-100 hover:shadow-xl hover:shadow-indigo-100/70">
			<div className="flex gap-5">
				<div
					className={`flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br ${agent.accent} text-2xl text-white shadow-xl ${agent.shadow}`}
				>
					<Icon />
				</div>
				<div className="min-w-0">
					<h3 className="text-lg font-bold text-slate-950">{agent.name}</h3>
					<p className="mt-2 max-w-sm text-sm font-medium leading-6 text-slate-600">
						{agent.description}
					</p>
					<button
						type="button"
						onClick={() => onLearnMore(agent)}
						className="mt-4 text-sm font-bold text-indigo-600 transition group-hover:text-indigo-500"
					>
						Learn More &rarr;
					</button>
				</div>
			</div>
		</article>
	);
};

const EdPlanNexusPage = () => {
	const navigate = useNavigate();

	return (
		<section className="min-h-screen bg-[radial-gradient(circle_at_82%_8%,rgba(99,102,241,0.11),transparent_30%),linear-gradient(135deg,#f8fbff_0%,#ffffff_45%,#f7f5ff_100%)] text-slate-950">
			<header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 px-5 py-3 backdrop-blur-xl sm:px-8 lg:px-12">
				<div className="flex items-center justify-end gap-5">
					<button
						type="button"
						className="flex h-10 w-10 items-center justify-center rounded-full text-slate-700 transition hover:bg-slate-100"
						aria-label="Notifications"
					>
						<FaBell />
					</button>
					<button
						type="button"
						className="flex items-center gap-3 rounded-full border border-slate-200 bg-white py-2 pl-2 pr-4 text-sm font-bold text-slate-800 shadow-sm transition hover:border-indigo-200 hover:shadow-md"
					>
						<span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
							V
						</span>
						Verify it&apos;s you
					</button>
				</div>
			</header>

			<div className="mx-auto max-w-[1560px] px-5 py-7 sm:px-8 lg:px-12">
				<div className="mb-7">
					<h1 className="text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
						EdPlan Nexus
					</h1>
					<p className="mt-3 max-w-3xl text-base font-medium leading-7 text-slate-700 md:text-lg">
						Your AI-powered education ecosystem with specialized agents working together
						to plan, guide, and optimize your academic journey.
					</p>
				</div>

				<div className="relative overflow-hidden rounded-3xl border border-indigo-200 bg-white/72 p-5 shadow-[0_22px_70px_rgba(79,70,229,0.10)] backdrop-blur-xl sm:p-8">
					<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_27%_44%,rgba(99,102,241,0.12),transparent_24%),radial-gradient(circle_at_72%_35%,rgba(129,140,248,0.10),transparent_26%)]" />
					<div className="relative grid items-center gap-8 lg:grid-cols-[0.9fr_1.35fr]">
						<RobotOrbit />

						<div>
							<div className="inline-flex rounded-full bg-indigo-100 px-3 py-1 text-xs font-black uppercase tracking-wide text-indigo-600">
								Master Agent
							</div>
							<h2 className="mt-5 flex flex-wrap items-center gap-3 text-3xl font-black tracking-tight text-slate-950">
								EdPlan Orchestrator
								<FaWandMagicSparkles className="text-xl text-indigo-500" />
							</h2>
							<p className="mt-4 max-w-3xl text-base font-medium leading-7 text-slate-700">
								Your intelligent command center that coordinates all specialized agents
								to deliver personalized, comprehensive education planning and guidance.
							</p>
							<div className="mt-7 flex flex-wrap items-center gap-4">
								<button
									type="button"
									onClick={() => navigate("/edplan-nexus/workspace")}
									className="inline-flex items-center gap-3 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 px-7 py-4 text-base font-black text-white shadow-xl shadow-indigo-200 transition hover:-translate-y-0.5 hover:shadow-2xl hover:shadow-indigo-300"
								>
									<FaRocket />
									Launch Now
								</button>
							</div>

							<div className="mt-8 grid gap-4 md:grid-cols-3">
								{featureItems.map(({ title, description, icon: Icon }) => (
									<div
										key={title}
										className="flex items-center gap-4 border-slate-200 md:border-l md:pl-6 first:md:border-l-0 first:md:pl-0"
									>
										<Icon className="text-2xl text-slate-500" />
										<div>
											<h3 className="text-sm font-black text-slate-800">{title}</h3>
											<p className="mt-1 text-xs font-semibold text-slate-500">
												{description}
											</p>
										</div>
									</div>
								))}
							</div>
						</div>
					</div>
				</div>

				<div className="mt-7">
					<h2 className="text-2xl font-black tracking-tight text-slate-950">
						Meet Your Specialized Agents
					</h2>
					<p className="mt-2 text-sm font-medium text-slate-600 md:text-base">
						Each agent is an expert in their domain, working together under the
						Orchestrator&apos;s guidance.
					</p>
				</div>

				<div className="mt-5 grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
					{agentCards.map((agent) => (
						<AgentCard
							key={agent.name}
							agent={agent}
							onLearnMore={(selectedAgent) => {
								if (selectedAgent.path) {
									navigate(selectedAgent.path);
								}
							}}
						/>
					))}
				</div>

				<div className="mt-8 rounded-2xl border border-indigo-100 bg-white/75 p-5 shadow-sm backdrop-blur-xl">
					<div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
						<div className="flex items-center gap-5">
							<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-indigo-50 text-xl text-slate-600">
								<FaShieldHalved />
							</div>
							<div>
								<h3 className="font-black text-slate-900">
									Your data is secure and private.
								</h3>
								<p className="mt-1 text-sm font-medium leading-6 text-slate-600">
									EdPlan Nexus is designed to keep your information safe while delivering
									personalized insights.
								</p>
							</div>
						</div>
						<button
							type="button"
							className="inline-flex items-center gap-2 self-start text-sm font-black text-indigo-600 transition hover:text-indigo-500 md:self-auto"
						>
							Learn more about EdPlan Nexus
							<FaArrowUpRightFromSquare className="text-xs" />
						</button>
					</div>
				</div>
			</div>
		</section>
	);
};

export default EdPlanNexusPage;
