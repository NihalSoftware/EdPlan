import { useNavigate } from "react-router-dom";
import { FaArrowLeft, FaCalendarDays, FaRocket } from "react-icons/fa6";

const INITIAL_SCHEDULEPILOT_PROMPT = "Create a schedule plan for me.";

const SchedulePilotHero = () => {
	const navigate = useNavigate();

	const launchSchedulePilot = () => {
		navigate("/edplan-nexus/workspace", {
			state: {
				initialPrompt: INITIAL_SCHEDULEPILOT_PROMPT,
				sourceAgent: "SchedulePilot",
			},
		});
	};

	return (
		<section className="relative overflow-hidden rounded-[2rem] border border-blue-100 bg-white/75 p-7 shadow-[0_24px_70px_rgba(37,99,235,0.10)] backdrop-blur-xl lg:p-10">
			<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_82%_25%,rgba(59,130,246,0.16),transparent_27%),radial-gradient(circle_at_58%_12%,rgba(99,102,241,0.12),transparent_24%)]" />
			<div className="relative grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-center">
				<div className="flex flex-col gap-7 sm:flex-row sm:items-center">
					<div className="flex h-28 w-28 shrink-0 items-center justify-center rounded-3xl bg-gradient-to-br from-blue-500 to-indigo-700 text-5xl text-white shadow-2xl shadow-blue-200">
						<FaCalendarDays />
					</div>
					<div>
						<div className="flex flex-wrap items-center gap-3">
							<h1 className="text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
								SchedulePilot
							</h1>
							<span className="rounded-full bg-blue-100 px-4 py-1.5 text-xs font-black text-blue-700">
								Schedule Optimizer
							</span>
						</div>
						<p className="mt-5 max-w-3xl text-base font-semibold leading-8 text-slate-700 md:text-lg">
							SchedulePilot creates optimized, conflict-free class schedules based on
							student preferences, required courses, credit targets, time availability,
							and university scheduling rules.
						</p>
						<div className="mt-7 flex flex-wrap gap-4">
							<button
								type="button"
								onClick={launchSchedulePilot}
								className="inline-flex items-center gap-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4 text-sm font-black text-white shadow-xl shadow-blue-200 transition hover:-translate-y-0.5 hover:shadow-blue-300"
							>
								<FaRocket />
								Launch SchedulePilot
							</button>
							<button
								type="button"
								onClick={() => navigate("/edplan-nexus")}
								className="inline-flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-6 py-4 text-sm font-black text-slate-700 shadow-sm transition hover:border-blue-200 hover:text-blue-600 hover:shadow-md"
							>
								<FaArrowLeft />
								Back to Nexus
							</button>
						</div>
					</div>
				</div>
				<div className="relative hidden h-56 lg:block">
					<div className="absolute right-4 top-4 grid w-72 grid-cols-5 gap-2 rounded-[1.75rem] border border-blue-100 bg-white/70 p-4 shadow-2xl shadow-blue-100">
						{Array.from({ length: 20 }).map((_, index) => (
							<div
								key={index}
								className={`h-8 rounded-lg ${
									[1, 7, 12, 18].includes(index)
										? "bg-blue-500"
										: [3, 9, 14].includes(index)
										? "bg-indigo-300"
										: "bg-blue-50"
								}`}
							/>
						))}
					</div>
					<div className="absolute bottom-2 right-24 h-12 w-36 rounded-full bg-gradient-to-r from-blue-300 to-indigo-300 blur-xl" />
				</div>
			</div>
		</section>
	);
};

export { INITIAL_SCHEDULEPILOT_PROMPT };
export default SchedulePilotHero;
