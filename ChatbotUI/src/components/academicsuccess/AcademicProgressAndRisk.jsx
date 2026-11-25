import {
	FaArrowRight,
	FaCalendarCheck,
	FaCircleCheck,
	FaGraduationCap,
	FaTriangleExclamation,
	FaWandMagicSparkles,
} from "react-icons/fa6";

const risks = ["Low Mathematics grades", "Attendance slightly decreasing"];
const recommendations = ["Attend tutoring", "Meet academic advisor", "Increase weekly study time"];

const AcademicProgressAndRisk = () => (
	<>
		<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
			<h2 className="text-2xl font-black text-slate-950">Academic Progress</h2>
			<div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(16rem,0.8fr)_minmax(16rem,0.8fr)]">
				<div className="rounded-2xl bg-emerald-50/60 p-5">
					<div className="mb-3 flex items-center justify-between gap-4">
						<h3 className="font-black text-slate-950">Degree Progress</h3>
						<span className="text-sm font-black text-emerald-700">82%</span>
					</div>
					<div className="h-3 overflow-hidden rounded-full bg-white">
						<div className="h-full w-[82%] rounded-full bg-emerald-500" />
					</div>
				</div>
				<div className="rounded-2xl bg-slate-50 p-5">
					<FaGraduationCap className="text-xl text-emerald-600" />
					<p className="mt-4 text-2xl font-black text-slate-950">98 / 120</p>
					<p className="text-sm font-bold text-slate-600">Credits</p>
				</div>
				<div className="rounded-2xl bg-slate-50 p-5">
					<FaCalendarCheck className="text-xl text-emerald-600" />
					<p className="mt-4 text-2xl font-black text-slate-950">Spring 2028</p>
					<p className="text-sm font-bold text-slate-600">Expected Graduation</p>
				</div>
			</div>
		</section>

		<div className="grid gap-8 lg:grid-cols-2">
			<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
				<h2 className="text-2xl font-black text-slate-950">
					Academic Risk Assessment
				</h2>
				<div className="mt-6 grid gap-5 sm:grid-cols-[12rem_minmax(0,1fr)]">
					<div className="rounded-2xl bg-amber-50/70 p-5 text-center">
						<FaTriangleExclamation className="mx-auto text-2xl text-amber-500" />
						<p className="mt-4 text-xs font-black uppercase tracking-wide text-amber-700">
							Risk Level
						</p>
						<p className="mt-1 text-2xl font-black text-slate-950">Low</p>
					</div>
					<div className="space-y-4">
						<div>
							<h3 className="font-black text-slate-950">Detected Risks</h3>
							<div className="mt-3 space-y-2">
								{risks.map((risk) => (
									<p key={risk} className="flex items-center gap-2 text-sm font-semibold text-slate-600">
										<span className="h-2 w-2 rounded-full bg-amber-400" />
										{risk}
									</p>
								))}
							</div>
						</div>
						<div>
							<h3 className="font-black text-slate-950">Recommendations</h3>
							<div className="mt-3 space-y-2">
								{recommendations.map((item) => (
									<p key={item} className="flex items-center gap-2 text-sm font-semibold text-slate-600">
										<FaCircleCheck className="text-emerald-500" />
										{item}
									</p>
								))}
							</div>
						</div>
					</div>
				</div>
			</section>

			<section className="rounded-3xl border border-emerald-100 bg-gradient-to-r from-emerald-50 to-teal-50 p-6 shadow-sm backdrop-blur-xl lg:p-8">
				<div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
					<div className="flex gap-4">
						<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white text-emerald-600 shadow-sm">
							<FaWandMagicSparkles />
						</div>
						<div>
							<h2 className="text-xl font-black text-slate-950">
								Our Academic Recommendation
							</h2>
							<p className="mt-2 max-w-3xl text-sm font-semibold leading-6 text-slate-700">
								Based on your recent performance, maintaining your current GPA
								while improving Mathematics and attendance will significantly
								increase your likelihood of graduating on time.
							</p>
						</div>
					</div>
					<button
						type="button"
						className="inline-flex items-center gap-2 self-start rounded-xl bg-white px-4 py-3 text-sm font-black text-emerald-700 shadow-sm transition hover:shadow-md md:self-auto"
					>
						View Improvement Plan
						<FaArrowRight className="text-xs" />
					</button>
				</div>
			</section>
		</div>
	</>
);

export default AcademicProgressAndRisk;
