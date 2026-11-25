import {
	FaBriefcase,
	FaChartLine,
	FaCode,
	FaCompass,
	FaMedal,
	FaRoad,
	FaScaleBalanced,
} from "react-icons/fa6";

const features = [
	["Career Discovery", "Find careers aligned with your interests.", FaCompass],
	["Skill Gap Analysis", "Identify missing technical and soft skills.", FaCode],
	["Learning Roadmap", "Receive a personalized learning path.", FaRoad],
	["Industry Insights", "Understand demand, salary, and growth.", FaChartLine],
	["Role Comparison", "Compare multiple career options.", FaScaleBalanced],
	["Career Readiness", "Track progress toward your target role.", FaMedal],
];

const CareerNavigatorFeatures = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<h2 className="text-2xl font-black text-slate-950">
			How CareerNavigator Helps You
		</h2>
		<div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
			{features.map(([title, description, Icon]) => (
				<article key={title} className="rounded-2xl bg-slate-50/80 p-4">
					<div className="flex h-11 w-11 items-center justify-center rounded-full bg-cyan-50 text-lg text-cyan-600">
						<Icon />
					</div>
					<h3 className="mt-4 text-sm font-black text-slate-950">{title}</h3>
					<p className="mt-2 text-xs font-semibold leading-5 text-slate-600">
						{description}
					</p>
				</article>
			))}
		</div>
		<div className="mt-6 flex items-center gap-3 rounded-2xl bg-cyan-50/70 p-4 text-sm font-black text-cyan-700">
			<FaBriefcase />
			Turn your academic profile into a practical career direction and skill plan.
		</div>
	</section>
);

export default CareerNavigatorFeatures;
