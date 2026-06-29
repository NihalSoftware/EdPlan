import {
	FaBookOpen,
	FaBriefcase,
	FaChartLine,
	FaCheckDouble,
	FaClock,
	FaGaugeHigh,
	FaGraduationCap,
	FaLayerGroup,
	FaRoute,
	FaShuffle,
} from "react-icons/fa6";

const features = [
	["Personalized Academic Planning", "Plans around degree goals, institution rules, interests, and pace.", FaRoute],
	["Semester-wise Roadmaps", "Transforms the full degree into clear, balanced semester plans.", FaLayerGroup],
	["Graduation Timeline", "Shows expected completion milestones and graduation readiness.", FaClock],
	["Prerequisite Intelligence", "Keeps course order realistic by respecting prerequisite chains.", FaCheckDouble],
	["Credit Load Optimization", "Balances heavy and lighter terms to reduce academic overload.", FaGaugeHigh],
	["Elective Recommendations", "Surfaces electives that support interests and specialization goals.", FaBookOpen],
	["Career Alignment", "Connects course choices to career pathways and future opportunities.", FaBriefcase],
	["Degree Requirement Tracking", "Makes remaining requirements visible and easier to act on.", FaGraduationCap],
	["Transfer Credit Support", "Accounts for accepted credits and helps avoid repeated coursework.", FaShuffle],
	["Academic Progress Monitoring", "Adapts recommendations as progress and performance change.", FaChartLine],
];

const FeatureGrid = () => (
	<section>
		<div className="mb-5">
			<h2 className="text-2xl font-black text-slate-950">Key Features</h2>
			<p className="mt-2 text-sm font-semibold text-slate-600">
				A planning engine built for clarity, sequencing, and long-term academic momentum.
			</p>
		</div>
		<div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-5">
			{features.map(([title, description, Icon]) => (
				<article
					key={title}
					className="group rounded-2xl border border-slate-200 bg-white/85 p-5 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-indigo-100 hover:shadow-xl hover:shadow-indigo-100/70"
				>
					<div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-200">
						<Icon />
					</div>
					<h3 className="mt-4 font-black leading-6 text-slate-950">{title}</h3>
					<p className="mt-2 text-sm font-medium leading-6 text-slate-600">
						{description}
					</p>
				</article>
			))}
		</div>
	</section>
);

export default FeatureGrid;
