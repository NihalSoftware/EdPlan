import { useNavigate } from "react-router-dom";
import {
	FaArrowLeft,
	FaChartLine,
	FaChartSimple,
	FaGraduationCap,
	FaRocket,
	FaUserGraduate,
} from "react-icons/fa6";

const INITIAL_ACADEMICSUCCESS_PROMPT =
	"Analyze my academic performance, GPA, and graduation progress, and suggest improvements.";

const AcademicSuccessHero = () => {
	const navigate = useNavigate();

	const launchAcademicSuccess = () => {
		navigate("/edplan-nexus/workspace", {
			state: {
				initialPrompt: INITIAL_ACADEMICSUCCESS_PROMPT,
				sourceAgent: "AcademicSuccess",
			},
		});
	};

	return (
		<section className="relative overflow-hidden rounded-[2rem] border border-emerald-100 bg-white/75 p-7 shadow-[0_24px_70px_rgba(16,185,129,0.10)] backdrop-blur-xl lg:p-10">
			<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_82%_25%,rgba(16,185,129,0.15),transparent_27%),radial-gradient(circle_at_58%_12%,rgba(99,102,241,0.10),transparent_24%)]" />
			<div className="relative grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-center">
				<div className="flex flex-col gap-7 sm:flex-row sm:items-center">
					<div className="flex h-28 w-28 shrink-0 items-center justify-center rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-600 text-5xl text-white shadow-2xl shadow-emerald-200">
						<FaChartSimple />
					</div>
					<div>
						<div className="flex flex-wrap items-center gap-3">
							<h1 className="text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
								AcademicSuccess
							</h1>
							<span className="rounded-full bg-emerald-100 px-4 py-1.5 text-xs font-black text-emerald-700">
								Student Success Advisor
							</span>
						</div>
						<p className="mt-5 max-w-3xl text-base font-semibold leading-8 text-slate-700 md:text-lg">
							AcademicSuccess continuously monitors academic performance and
							helps students improve GPA, detect risks early, receive personalized
							interventions, and increase graduation success.
						</p>
						<div className="mt-7 flex flex-wrap gap-4">
							<button
								type="button"
								onClick={launchAcademicSuccess}
								className="inline-flex items-center gap-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-4 text-sm font-black text-white shadow-xl shadow-emerald-200 transition hover:-translate-y-0.5 hover:shadow-emerald-300"
							>
								<FaRocket />
								Launch AcademicSuccess
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
					<div className="absolute bottom-7 right-12 h-32 w-48 rounded-[1.75rem] bg-gradient-to-br from-emerald-100 to-indigo-100 shadow-2xl shadow-emerald-100" />
					<div className="absolute bottom-20 right-24 h-24 w-32 rounded-2xl bg-white shadow-xl">
						<div className="mx-auto mt-5 h-12 w-20 rounded-lg bg-emerald-100" />
						<div className="mx-auto mt-3 h-2 w-24 rounded-full bg-indigo-100" />
					</div>
					<div className="absolute bottom-28 right-56 flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-2xl text-emerald-600 shadow-xl">
						<FaGraduationCap />
					</div>
					<div className="absolute bottom-24 right-4 flex h-16 w-16 items-center justify-center rounded-full bg-white text-2xl text-indigo-600 shadow-xl">
						<FaChartLine />
					</div>
					<div className="absolute bottom-8 right-60 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500 text-xl text-white shadow-xl">
						<FaUserGraduate />
					</div>
				</div>
			</div>
		</section>
	);
};

export { INITIAL_ACADEMICSUCCESS_PROMPT };
export default AcademicSuccessHero;
