import {
	FaChartLine,
	FaChartSimple,
	FaFlagCheckered,
	FaGraduationCap,
	FaLightbulb,
	FaShieldHalved,
	FaUserGroup,
} from "react-icons/fa6";

const features = [
	["GPA Analysis", "Analyze semester-wise GPA trends.", FaChartLine],
	["Academic Progress", "Track completion toward graduation.", FaFlagCheckered],
	["Risk Detection", "Identify academic risks early.", FaShieldHalved],
	["Interventions", "Suggest actions before performance declines.", FaLightbulb],
	["Retention Improvement", "Support continuous academic success.", FaUserGroup],
	["Outcome Insights", "Monitor long-term academic achievement.", FaGraduationCap],
];

const AcademicSuccessFeatures = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<h2 className="text-2xl font-black text-slate-950">
			How AcademicSuccess Helps
		</h2>
		<div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
			{features.map(([title, description, Icon]) => (
				<article key={title} className="rounded-2xl bg-slate-50/80 p-4">
					<div className="flex h-11 w-11 items-center justify-center rounded-full bg-emerald-50 text-lg text-emerald-600">
						<Icon />
					</div>
					<h3 className="mt-4 text-sm font-black text-slate-950">{title}</h3>
					<p className="mt-2 text-xs font-semibold leading-5 text-slate-600">
						{description}
					</p>
				</article>
			))}
		</div>
		<div className="mt-6 flex items-center gap-3 rounded-2xl bg-emerald-50/70 p-4 text-sm font-black text-emerald-700">
			<FaChartSimple />
			Track performance, risks, and graduation progress in one clear view.
		</div>
	</section>
);

export default AcademicSuccessFeatures;
