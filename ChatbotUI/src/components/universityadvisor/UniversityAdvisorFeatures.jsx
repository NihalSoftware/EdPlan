import {
	FaChartLine,
	FaCircleNodes,
	FaGraduationCap,
	FaMagnifyingGlassChart,
} from "react-icons/fa6";

const features = [
	{
		title: "Smart Comparison",
		description: "Compare universities on academics, tuition, and outcomes.",
		icon: FaCircleNodes,
	},
	{
		title: "Personalized Matches",
		description: "Suggests schools that fit goals and preferences.",
		icon: FaGraduationCap,
	},
	{
		title: "Real Insights",
		description: "Highlights rankings, costs, and opportunities.",
		icon: FaChartLine,
	},
	{
		title: "Program Explorer",
		description: "Find programs aligned with academic interests.",
		icon: FaMagnifyingGlassChart,
	},
];

const UniversityAdvisorFeatures = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<h2 className="text-2xl font-black text-slate-950">
			How UniversityAdvisor Helps You
		</h2>
		<div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
			{features.map(({ title, description, icon: Icon }) => (
				<article key={title} className="rounded-2xl bg-slate-50/80 p-5">
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
	</section>
);

export default UniversityAdvisorFeatures;
