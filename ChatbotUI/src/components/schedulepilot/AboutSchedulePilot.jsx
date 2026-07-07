import {
	FaArrowsRotate,
	FaBolt,
	FaClock,
	FaGaugeHigh,
	FaLayerGroup,
	FaShieldHalved,
} from "react-icons/fa6";

const features = [
	{
		title: "Conflict-Free Scheduling",
		description: "Detects overlaps and protects required class meeting times.",
		icon: FaShieldHalved,
	},
	{
		title: "Multiple Schedule Options",
		description: "Compares several viable plans so students can choose with confidence.",
		icon: FaLayerGroup,
	},
	{
		title: "Preference-Aware Planning",
		description: "Considers preferred days, times, course load, and availability.",
		icon: FaClock,
	},
	{
		title: "Balanced Workload",
		description: "Distributes demanding courses and credits across the week.",
		icon: FaGaugeHigh,
	},
	{
		title: "Real-Time Updates",
		description: "Supports fast revisions as course availability or priorities change.",
		icon: FaArrowsRotate,
	},
	{
		title: "Productive Class Blocks",
		description: "Groups compatible classes to reduce gaps and campus backtracking.",
		icon: FaBolt,
	},
];

const AboutSchedulePilot = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-7 shadow-sm backdrop-blur-xl lg:p-9">
		<div className="max-w-4xl">
			<h2 className="text-2xl font-black text-slate-950">About SchedulePilot</h2>
			<p className="mt-4 text-sm font-semibold leading-7 text-slate-700 md:text-base">
				SchedulePilot is the EdPlan Nexus scheduling specialist. It helps students
				transform required courses, university meeting times, personal preferences,
				and workload goals into practical weekly schedules that are easier to follow
				and less likely to create conflicts.
			</p>
		</div>
		<div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
			{features.map(({ title, description, icon: Icon }) => (
				<article
					key={title}
					className="group rounded-2xl border border-slate-100 bg-slate-50/70 p-5 transition duration-300 hover:-translate-y-1 hover:border-blue-100 hover:bg-white hover:shadow-xl hover:shadow-blue-100/70"
				>
					<div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-200">
						<Icon />
					</div>
					<h3 className="mt-4 font-black text-slate-950">{title}</h3>
					<p className="mt-2 text-sm font-medium leading-6 text-slate-600">
						{description}
					</p>
				</article>
			))}
		</div>
	</section>
);

export default AboutSchedulePilot;
