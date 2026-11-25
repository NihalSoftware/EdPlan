import { useNavigate } from "react-router-dom";
import {
	FaArrowLeft,
	FaBriefcase,
	FaBullseye,
	FaChartLine,
	FaCompass,
	FaRocket,
} from "react-icons/fa6";

const INITIAL_CAREERNAVIGATOR_PROMPT =
	"Create a personalized career roadmap for me based on my interests and academic profile.";

const CareerNavigatorHero = () => {
	const navigate = useNavigate();

	const launchCareerNavigator = () => {
		navigate("/edplan-nexus/workspace", {
			state: {
				initialPrompt: INITIAL_CAREERNAVIGATOR_PROMPT,
				sourceAgent: "CareerNavigator",
			},
		});
	};

	return (
		<section className="relative overflow-hidden rounded-[2rem] border border-cyan-100 bg-white/75 p-7 shadow-[0_24px_70px_rgba(6,182,212,0.10)] backdrop-blur-xl lg:p-10">
			<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_82%_25%,rgba(6,182,212,0.15),transparent_27%),radial-gradient(circle_at_58%_12%,rgba(99,102,241,0.10),transparent_24%)]" />
			<div className="relative grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-center">
				<div className="flex flex-col gap-7 sm:flex-row sm:items-center">
					<div className="flex h-28 w-28 shrink-0 items-center justify-center rounded-3xl bg-gradient-to-br from-cyan-500 to-indigo-600 text-5xl text-white shadow-2xl shadow-cyan-200">
						<FaCompass />
					</div>
					<div>
						<div className="flex flex-wrap items-center gap-3">
							<h1 className="text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
								CareerNavigator
							</h1>
							<span className="rounded-full bg-cyan-100 px-4 py-1.5 text-xs font-black text-cyan-700">
								Career & Skill Advisor
							</span>
						</div>
						<p className="mt-5 max-w-3xl text-base font-semibold leading-8 text-slate-700 md:text-lg">
							CareerNavigator helps students discover suitable career paths,
							identify skill gaps, compare roles, and build a learning roadmap
							aligned with their academic profile and long-term goals.
						</p>
						<div className="mt-7 flex flex-wrap gap-4">
							<button
								type="button"
								onClick={launchCareerNavigator}
								className="inline-flex items-center gap-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-6 py-4 text-sm font-black text-white shadow-xl shadow-cyan-200 transition hover:-translate-y-0.5 hover:shadow-cyan-300"
							>
								<FaRocket />
								Launch CareerNavigator
							</button>
							<button
								type="button"
								onClick={() => navigate("/edplan-nexus")}
								className="inline-flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-6 py-4 text-sm font-black text-slate-700 shadow-sm transition hover:border-cyan-200 hover:text-cyan-600 hover:shadow-md"
							>
								<FaArrowLeft />
								Back to Nexus
							</button>
						</div>
					</div>
				</div>
				<div className="relative hidden h-56 lg:block">
					<div className="absolute bottom-5 right-8 flex h-24 w-24 items-center justify-center rounded-full bg-white text-4xl text-cyan-600 shadow-2xl shadow-cyan-100">
						<FaBullseye />
					</div>
					<div className="absolute bottom-4 right-48 h-12 w-16 rounded-t-xl bg-indigo-300 shadow-lg" />
					<div className="absolute bottom-4 right-36 h-20 w-16 rounded-t-xl bg-indigo-400 shadow-lg" />
					<div className="absolute bottom-4 right-24 h-28 w-16 rounded-t-xl bg-indigo-500 shadow-lg" />
					<div className="absolute bottom-36 right-32 flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-2xl text-indigo-600 shadow-xl">
						<FaBriefcase />
					</div>
					<div className="absolute bottom-32 right-56 flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-50 text-xl text-cyan-600 shadow-xl">
						<FaChartLine />
					</div>
				</div>
			</div>
		</section>
	);
};

export { INITIAL_CAREERNAVIGATOR_PROMPT };
export default CareerNavigatorHero;
