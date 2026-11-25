import {
	FaBullseye,
	FaChartLine,
	FaCircleNodes,
	FaGraduationCap,
	FaLightbulb,
} from "react-icons/fa6";

const pillars = [
	{
		icon: FaCircleNodes,
		title: "Personalized Planning",
		description:
			"Tailored plans based on goals and requirements.",
	},
	{
		icon: FaGraduationCap,
		title: "Smart Course Mapping",
		description:
			"Automatically maps courses and prerequisites.",
	},
	{
		icon: FaBullseye,
		title: "Graduation Roadmap",
		description:
			"Shows the clearest path to graduate on time.",
	},
	{
		icon: FaChartLine,
		title: "Progress Tracking",
		description:
			"Tracks completed credits and remaining work.",
	},
	{
		icon: FaLightbulb,
		title: "Adaptive Suggestions",
		description:
			"Recommends smarter choices as progress changes.",
	},
];

const Overview = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<h2 className="text-2xl font-black text-slate-950">About PathCrafter</h2>
		<p className="mt-4 max-w-5xl text-sm font-semibold leading-7 text-slate-700 md:text-base">
			PathCrafter helps students build a clear and achievable academic roadmap.
			It considers program curriculum, prerequisites, completed credits, and
			career goals to create a personalized semester-by-semester plan.
		</p>
		<p className="mt-3 max-w-5xl text-sm font-semibold leading-7 text-slate-700 md:text-base">
			The result is an easier way to understand what to take next, stay on track,
			and make confident planning decisions every term.
		</p>
		<div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
			{pillars.map(({ icon: Icon, title, description }) => (
				<div key={title} className="rounded-2xl bg-slate-50/80 p-4">
					<div className="flex h-11 w-11 items-center justify-center rounded-full bg-indigo-50 text-lg text-indigo-600">
						<Icon />
					</div>
					<h3 className="mt-4 text-sm font-black text-slate-950">{title}</h3>
					<p className="mt-2 text-xs font-semibold leading-5 text-slate-600">
						{description}
					</p>
				</div>
			))}
		</div>
	</section>
);

export default Overview;
