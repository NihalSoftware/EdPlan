import {
	FaBuildingColumns,
	FaCalendarDays,
	FaChartSimple,
	FaCircleNodes,
	FaClock,
	FaWandMagicSparkles,
} from "react-icons/fa6";
import { FaDollarSign } from "react-icons/fa";

const agentIconMap = {
	PathCrafter: FaCircleNodes,
	SchedulePilot: FaCalendarDays,
	UniversityAdvisor: FaBuildingColumns,
	FinanceGuide: FaDollarSign,
	AcademicSuccess: FaChartSimple,
};

const normalizeAgent = (agent, isLoading) => {
	if (typeof agent === "string") {
		return {
			name: agent,
			status: isLoading ? "Running" : "Completed",
		};
	}

	return {
		name: agent?.name || agent?.module || agent?.agent || "Agent",
		status: agent?.status || agent?.state || (isLoading ? "Running" : "Completed"),
	};
};

const ActivatedAgents = ({ telemetry, isLoading }) => {
	const agents = telemetry.activatedModules || [];

	return (
		<section className="rounded-3xl border border-slate-200 bg-white/80 p-4 shadow-sm backdrop-blur-xl">
			<div className="mb-4 flex items-center justify-between gap-3">
				<h2 className="text-base font-black text-slate-950">Activated Agents</h2>
				<span className="text-xs font-black text-indigo-600">{agents.length || ""}</span>
			</div>
			{agents.length ? (
				<div className="space-y-3">
					{agents.map((agent, index) => {
						const normalized = normalizeAgent(agent, isLoading);
						const Icon = agentIconMap[normalized.name] || FaWandMagicSparkles;

						return (
							<div
								key={`${normalized.name}-${index}`}
								className="flex items-center gap-3 rounded-2xl border border-indigo-100 bg-indigo-50/40 p-3.5"
							>
								<div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white text-sm text-indigo-600">
									<Icon />
								</div>
								<div className="min-w-0 flex-1">
									<p className="truncate text-sm font-black text-slate-950">
										{normalized.name}
									</p>
									<p className="mt-1 text-xs font-bold text-slate-500">
										{normalized.status}
									</p>
								</div>
							</div>
						);
					})}
				</div>
			) : (
				<div className="flex min-h-24 flex-col items-center justify-center rounded-2xl border border-slate-100 bg-white/70 p-4 text-center">
					<FaClock className="text-2xl text-slate-400" />
					<p className="mt-3 text-sm font-black text-slate-500">No agents activated yet</p>
					<p className="mt-1 text-xs font-semibold leading-5 text-slate-400">
						Agents will appear here when the orchestrator engages them.
					</p>
				</div>
			)}
		</section>
	);
};

export default ActivatedAgents;
