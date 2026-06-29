import {
	FaBookOpen,
	FaBrain,
	FaBullseye,
	FaBuildingColumns,
	FaCheckDouble,
	FaGraduationCap,
	FaListCheck,
	FaRoute,
} from "react-icons/fa6";

const steps = [
	["Student Goals", "Understands desired major, timeline, interests, and academic priorities.", FaBullseye],
	["University Requirements", "Reads the rule set that governs degree completion.", FaBuildingColumns],
	["Program Curriculum", "Maps required courses, electives, and concentration options.", FaBookOpen],
	["Prerequisites", "Sequences courses so dependencies are met before registration.", FaCheckDouble],
	["Degree Audit", "Identifies completed, remaining, and at-risk requirements.", FaListCheck],
	["AI Planning Engine", "Generates a balanced, goal-aligned planning strategy.", FaBrain],
	["Optimized Academic Plan", "Outputs semester-wise course recommendations.", FaRoute],
	["Graduation Roadmap", "Keeps the student oriented around completion milestones.", FaGraduationCap],
];

const WorkflowTimeline = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-7 shadow-sm backdrop-blur-xl lg:p-9">
		<h2 className="text-2xl font-black text-slate-950">Planning Workflow</h2>
		<div className="mt-7 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
			{steps.map(([title, description, Icon], index) => (
				<div key={title} className="relative rounded-2xl border border-indigo-100 bg-indigo-50/40 p-5">
					<div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-indigo-600 shadow-sm">
						<Icon />
					</div>
					<p className="mt-4 text-xs font-black uppercase tracking-wide text-indigo-500">
						Step {index + 1}
					</p>
					<h3 className="mt-1 font-black text-slate-950">{title}</h3>
					<p className="mt-2 text-sm font-medium leading-6 text-slate-600">
						{description}
					</p>
				</div>
			))}
		</div>
	</section>
);

export default WorkflowTimeline;
