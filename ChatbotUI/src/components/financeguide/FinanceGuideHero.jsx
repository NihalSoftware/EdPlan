import { useNavigate } from "react-router-dom";
import { FaArrowLeft, FaCalculator, FaGraduationCap, FaRocket } from "react-icons/fa6";
import { FaDollarSign } from "react-icons/fa";

const INITIAL_FINANCEGUIDE_PROMPT =
	"Help me estimate the cost of my education and suggest financial aid opportunities.";

const FinanceGuideHero = () => {
	const navigate = useNavigate();

	const launchFinanceGuide = () => {
		navigate("/edplan-nexus/workspace", {
			state: {
				initialPrompt: INITIAL_FINANCEGUIDE_PROMPT,
				sourceAgent: "FinanceGuide",
			},
		});
	};

	return (
		<section className="relative overflow-hidden rounded-[2rem] border border-orange-100 bg-white/75 p-7 shadow-[0_24px_70px_rgba(249,115,22,0.10)] backdrop-blur-xl lg:p-10">
			<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_82%_25%,rgba(249,115,22,0.16),transparent_27%),radial-gradient(circle_at_58%_12%,rgba(99,102,241,0.10),transparent_24%)]" />
			<div className="relative grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-center">
				<div className="flex flex-col gap-7 sm:flex-row sm:items-center">
					<div className="flex h-28 w-28 shrink-0 items-center justify-center rounded-3xl bg-gradient-to-br from-orange-400 to-orange-600 text-5xl text-white shadow-2xl shadow-orange-200">
						<FaDollarSign />
					</div>
					<div>
						<div className="flex flex-wrap items-center gap-3">
							<h1 className="text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
								FinanceGuide
							</h1>
							<span className="rounded-full bg-orange-100 px-4 py-1.5 text-xs font-black text-orange-700">
								Education Financial Planner
							</span>
						</div>
						<p className="mt-5 max-w-3xl text-base font-semibold leading-8 text-slate-700 md:text-lg">
							FinanceGuide helps students estimate the full cost of education,
							discover scholarships, compare tuition, calculate living expenses,
							and build an affordable education plan.
						</p>
						<div className="mt-7 flex flex-wrap gap-4">
							<button
								type="button"
								onClick={launchFinanceGuide}
								className="inline-flex items-center gap-3 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-4 text-sm font-black text-white shadow-xl shadow-orange-200 transition hover:-translate-y-0.5 hover:shadow-orange-300"
							>
								<FaRocket />
								Launch FinanceGuide
							</button>
							<button
								type="button"
								onClick={() => navigate("/edplan-nexus")}
								className="inline-flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-6 py-4 text-sm font-black text-slate-700 shadow-sm transition hover:border-orange-200 hover:text-orange-600 hover:shadow-md"
							>
								<FaArrowLeft />
								Back to Nexus
							</button>
						</div>
					</div>
				</div>
				<div className="relative hidden h-56 lg:block">
					<div className="absolute bottom-6 right-20 flex h-28 w-24 items-center justify-center rounded-3xl bg-gradient-to-br from-indigo-200 to-violet-300 shadow-2xl shadow-indigo-100">
						<FaGraduationCap className="text-5xl text-indigo-600" />
					</div>
					<div className="absolute bottom-10 right-4 flex h-24 w-20 items-center justify-center rounded-2xl bg-white text-4xl text-orange-500 shadow-xl">
						<FaCalculator />
					</div>
					<div className="absolute bottom-3 right-36 flex h-16 w-16 items-center justify-center rounded-full bg-orange-400 text-2xl text-white shadow-xl">
						<FaDollarSign />
					</div>
					<div className="absolute bottom-4 right-52 h-10 w-10 rounded-full bg-yellow-300 shadow-lg" />
					<div className="absolute bottom-16 right-48 h-10 w-10 rounded-full bg-yellow-300 shadow-lg" />
				</div>
			</div>
		</section>
	);
};

export { INITIAL_FINANCEGUIDE_PROMPT };
export default FinanceGuideHero;
