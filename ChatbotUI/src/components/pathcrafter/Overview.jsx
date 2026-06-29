import {
	FaBullseye,
	FaChartLine,
	FaCircleNodes,
	FaGraduationCap,
} from "react-icons/fa6";

const pillars = [
	{
		icon: FaCircleNodes,
		title: "Personalized Academic Planning",
		description:
			"Build a semester-wise path tailored to your degree, university requirements, personal goals, transfer status, and preferred pace.",
	},
	{
		icon: FaGraduationCap,
		title: "Smart Course Mapping",
		description:
			"Sequence courses with prerequisites, corequisites, availability, and graduation requirements in mind.",
	},
	{
		icon: FaBullseye,
		title: "Goal-Aligned Pathways",
		description:
			"Adapt the plan for early graduation, balanced semesters, career goals, specialization tracks, and academic performance.",
	},
	{
		icon: FaChartLine,
		title: "Continuous Optimization",
		description:
			"Keep the plan responsive as interests, grades, completed credits, and program requirements evolve.",
	},
];

const Overview = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-7 shadow-sm backdrop-blur-xl lg:p-9">
		<h2 className="text-2xl font-black text-slate-950">About PathCrafter</h2>
		<p className="mt-4 max-w-4xl text-sm font-semibold leading-7 text-slate-700 md:text-base">
			PathCrafter is EdPlan Nexus&apos;s academic planning specialist. It turns
			program curriculum, university rules, completed credits, course sequencing,
			prerequisite dependencies, semester workload, and graduation targets into a
			clear roadmap students can understand and act on.
		</p>
		<p className="mt-4 max-w-4xl text-sm font-semibold leading-7 text-slate-700 md:text-base">
			The experience is designed for long-range clarity: students see what to take,
			when to take it, why each course belongs in sequence, and how each semester
			supports progress toward graduation and career readiness.
		</p>
		<div className="mt-8 grid gap-5 md:grid-cols-2">
			{pillars.map(({ icon: Icon, title, description }) => (
				<div key={title} className="flex gap-5 rounded-2xl bg-slate-50/80 p-5">
					<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-lg text-indigo-600">
						<Icon />
					</div>
					<div>
						<h3 className="font-black text-slate-950">{title}</h3>
						<p className="mt-2 text-sm font-medium leading-6 text-slate-600">
							{description}
						</p>
					</div>
				</div>
			))}
		</div>
		<div className="mt-8 rounded-2xl border border-indigo-100 bg-indigo-50/70 p-5 text-sm font-black leading-7 text-indigo-700">
			PathCrafter helps students never miss a requirement, stay on track, and
			graduate with clarity and confidence.
		</div>
	</section>
);

export default Overview;
