import { useNavigate } from "react-router-dom";
import { FaArrowLeft, FaBuildingColumns, FaRocket } from "react-icons/fa6";

const INITIAL_UNIVERSITYADVISOR_PROMPT =
	"Suggest the best universities for me and compare them based on my goals.";

const UniversityAdvisorHero = () => {
	const navigate = useNavigate();

	const launchUniversityAdvisor = () => {
		navigate("/edplan-nexus/workspace", {
			state: {
				initialPrompt: INITIAL_UNIVERSITYADVISOR_PROMPT,
				sourceAgent: "UniversityAdvisor",
			},
		});
	};

	return (
		<section className="relative overflow-hidden rounded-[2rem] border border-emerald-100 bg-white/75 p-7 shadow-[0_24px_70px_rgba(16,185,129,0.10)] backdrop-blur-xl lg:p-10">
			<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_82%_25%,rgba(16,185,129,0.15),transparent_27%),radial-gradient(circle_at_58%_12%,rgba(99,102,241,0.10),transparent_24%)]" />
			<div className="relative grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-center">
				<div className="flex flex-col gap-7 sm:flex-row sm:items-center">
					<div className="flex h-28 w-28 shrink-0 items-center justify-center rounded-3xl bg-gradient-to-br from-emerald-500 to-green-700 text-5xl text-white shadow-2xl shadow-emerald-200">
						<FaBuildingColumns />
					</div>
					<div>
						<div className="flex flex-wrap items-center gap-3">
							<h1 className="text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
								UniversityAdvisor
							</h1>
							<span className="rounded-full bg-emerald-100 px-4 py-1.5 text-xs font-black text-emerald-700">
								University Comparator
							</span>
						</div>
						<p className="mt-5 max-w-3xl text-base font-semibold leading-8 text-slate-700 md:text-lg">
							UniversityAdvisor compares universities, tuition, transfer opportunities,
							academic quality, programs, and career outcomes so students can make
							informed college decisions with confidence.
						</p>
						<div className="mt-7 flex flex-wrap gap-4">
							<button
								type="button"
								onClick={launchUniversityAdvisor}
								className="inline-flex items-center gap-3 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 px-6 py-4 text-sm font-black text-white shadow-xl shadow-emerald-200 transition hover:-translate-y-0.5 hover:shadow-emerald-300"
							>
								<FaRocket />
								Launch UniversityAdvisor
							</button>
							<button
								type="button"
								onClick={() => navigate("/edplan-nexus")}
								className="inline-flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-6 py-4 text-sm font-black text-slate-700 shadow-sm transition hover:border-emerald-200 hover:text-emerald-600 hover:shadow-md"
							>
								<FaArrowLeft />
								Back to Nexus
							</button>
						</div>
					</div>
				</div>
				<div className="relative hidden h-56 lg:block">
					<div className="absolute bottom-8 right-10 h-28 w-52 rounded-[1.75rem] bg-gradient-to-br from-emerald-100 to-indigo-100 shadow-2xl shadow-emerald-100" />
					<div className="absolute bottom-24 right-24 h-20 w-32 rounded-t-[2rem] border-8 border-slate-200 bg-white shadow-xl">
						<div className="mx-auto mt-4 h-12 w-20 rounded-t-2xl bg-slate-100" />
					</div>
					<div className="absolute bottom-18 right-20 h-12 w-40 rounded-md bg-white shadow-xl" />
					<div className="absolute bottom-30 right-16 h-10 w-48 bg-emerald-200 [clip-path:polygon(50%_0,100%_100%,0_100%)]" />
					<div className="absolute bottom-10 right-56 h-20 w-8 rounded-full bg-emerald-400" />
					<div className="absolute bottom-10 right-2 h-24 w-9 rounded-full bg-emerald-300" />
				</div>
			</div>
		</section>
	);
};

export { INITIAL_UNIVERSITYADVISOR_PROMPT };
export default UniversityAdvisorHero;
