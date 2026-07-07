import { useNavigate } from "react-router-dom";
import { FaArrowLeft, FaCircleNodes, FaRocket } from "react-icons/fa6";

const INITIAL_PATHCRAFTER_PROMPT = "Create an academic plan for me.";

const PathCrafterHero = () => {
	const navigate = useNavigate();

	const launchPathCrafter = () => {
		navigate("/edplan-nexus/workspace", {
			state: {
				initialPrompt: INITIAL_PATHCRAFTER_PROMPT,
				sourceAgent: "PathCrafter",
			},
		});
	};

	return (
		<section className="relative overflow-hidden rounded-[2rem] border border-indigo-100 bg-white/75 p-7 shadow-[0_24px_70px_rgba(79,70,229,0.10)] backdrop-blur-xl lg:p-10">
			<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_84%_28%,rgba(99,102,241,0.16),transparent_27%),radial-gradient(circle_at_60%_15%,rgba(167,139,250,0.12),transparent_24%)]" />
			<div className="relative grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-center">
				<div className="flex flex-col gap-7 sm:flex-row sm:items-center">
					<div className="flex h-28 w-28 shrink-0 items-center justify-center rounded-3xl bg-gradient-to-br from-indigo-500 to-violet-700 text-5xl text-white shadow-2xl shadow-indigo-200">
						<FaCircleNodes />
					</div>
					<div>
						<div className="flex flex-wrap items-center gap-3">
							<h1 className="text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
								PathCrafter
							</h1>
							<span className="rounded-full bg-indigo-100 px-4 py-1.5 text-xs font-black text-indigo-700">
								Education Planner
							</span>
						</div>
						<p className="mt-5 max-w-3xl text-base font-semibold leading-8 text-slate-700 md:text-lg">
							Your intelligent academic planning companion that builds personalized
							semester-by-semester education plans aligned with your university
							requirements, graduation goals, career aspirations, and academic performance.
						</p>
						<div className="mt-7 flex flex-wrap gap-4">
							<button
								type="button"
								onClick={launchPathCrafter}
								className="inline-flex items-center gap-3 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-4 text-sm font-black text-white shadow-xl shadow-indigo-200 transition hover:-translate-y-0.5 hover:shadow-indigo-300"
							>
								<FaRocket />
								Launch PathCrafter
							</button>
							<button
								type="button"
								onClick={() => navigate("/edplan-nexus")}
								className="inline-flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-6 py-4 text-sm font-black text-slate-700 shadow-sm transition hover:border-indigo-200 hover:text-indigo-600 hover:shadow-md"
							>
								<FaArrowLeft />
								Back to Nexus
							</button>
						</div>
					</div>
				</div>
				<div className="relative hidden h-56 lg:block">
					<div className="absolute bottom-2 right-8 h-24 w-44 rounded-[2rem] bg-gradient-to-br from-indigo-200 to-violet-300 shadow-2xl shadow-indigo-100" />
					<div className="absolute bottom-14 right-16 h-20 w-36 rounded-[1.5rem] bg-gradient-to-br from-indigo-300 to-violet-400 shadow-xl" />
					<div className="absolute bottom-28 right-24 h-16 w-28 rounded-[1.25rem] bg-gradient-to-br from-indigo-400 to-violet-500 shadow-xl" />
					<div className="absolute bottom-40 right-28 h-12 w-20 rotate-3 rounded-md bg-indigo-600 [clip-path:polygon(50%_0,100%_35%,50%_70%,0_35%)]" />
					<div className="absolute bottom-4 right-0 h-20 w-28 rounded-full border-[12px] border-indigo-300 border-l-transparent border-t-transparent" />
				</div>
			</div>
		</section>
	);
};

export { INITIAL_PATHCRAFTER_PROMPT };
export default PathCrafterHero;
