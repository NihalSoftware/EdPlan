import { FaArrowRight, FaCheck, FaCircleDot, FaWandMagicSparkles } from "react-icons/fa6";

const currentSkills = ["Python", "SQL", "Data Structures", "Computer Networks", "Git"];
const skillsToLearn = [
	"Machine Learning",
	"Deep Learning",
	"PyTorch",
	"TensorFlow",
	"MLOps",
	"Docker",
	"Kubernetes",
];
const roadmap = [
	"Programming Fundamentals",
	"Data Structures & Algorithms",
	"Python for AI",
	"Machine Learning",
	"Deep Learning",
	"Projects",
	"Internship",
	"ML Engineer",
];
const rows = [
	["Average Salary", "High", "$120,000"],
	["Demand", "High", "High"],
	["Work-Life Balance", "Good", "Moderate"],
	["Remote Opportunities", "High", "Moderate"],
	["Required Skills", "AI/ML", "Security"],
	["Difficulty", "High", "High"],
	["Future Growth", "Excellent", "Excellent"],
	["Recommended Certifications", "AWS ML", "Security+"],
];

const CareerPathDetails = () => (
	<>
		<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
			<h2 className="text-2xl font-black text-slate-950">Skill Gap Analysis</h2>
			<div className="mt-6 grid gap-5 lg:grid-cols-2">
				<div className="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-5">
					<h3 className="font-black text-emerald-800">Current Skills</h3>
					<div className="mt-4 flex flex-wrap gap-2.5">
						{currentSkills.map((skill) => (
							<span
								key={skill}
								className="inline-flex items-center gap-2 rounded-full border border-emerald-100 bg-white px-3.5 py-2 text-sm font-bold text-slate-700"
							>
								<FaCheck className="text-emerald-600" />
								{skill}
							</span>
						))}
					</div>
				</div>
				<div className="rounded-2xl border border-cyan-100 bg-cyan-50/50 p-5">
					<h3 className="font-black text-cyan-800">Skills To Learn</h3>
					<div className="mt-4 flex flex-wrap gap-2.5">
						{skillsToLearn.map((skill) => (
							<span
								key={skill}
								className="rounded-full border border-cyan-100 bg-white px-3.5 py-2 text-sm font-bold text-cyan-700"
							>
								{skill}
							</span>
						))}
					</div>
				</div>
			</div>
		</section>

		<div className="grid gap-8 xl:grid-cols-[0.95fr_1.05fr]">
			<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
				<h2 className="text-2xl font-black text-slate-950">Learning Roadmap</h2>
				<div className="mt-6 space-y-0">
					{roadmap.map((step, index) => (
						<div key={step} className="flex gap-4">
							<div className="flex flex-col items-center">
								<div className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-50 text-cyan-600">
									<FaCircleDot className="text-sm" />
								</div>
								{index < roadmap.length - 1 && <div className="h-6 w-px bg-cyan-100" />}
							</div>
							<p className="pb-4 text-sm font-black text-slate-800">{step}</p>
						</div>
					))}
				</div>
			</section>

			<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
				<h2 className="text-2xl font-black text-slate-950">Compare Career Paths</h2>
				<div className="mt-6 overflow-x-auto rounded-2xl border border-slate-200">
					<table className="min-w-[560px] w-full text-sm">
						<thead className="bg-slate-50 text-left">
							<tr>
								<th className="px-4 py-3 font-black text-slate-700">Criteria</th>
								<th className="px-4 py-3 font-black text-cyan-700">ML Engineer</th>
								<th className="px-4 py-3 font-black text-indigo-700">
									Cybersecurity Engineer
								</th>
							</tr>
						</thead>
						<tbody>
							{rows.map(([label, ml, cyber], index) => (
								<tr key={label} className={index % 2 ? "bg-white" : "bg-slate-50/50"}>
									<td className="border-t border-slate-100 px-4 py-3 font-black text-slate-800">
										{label}
									</td>
									<td className="border-t border-slate-100 px-4 py-3 font-semibold text-slate-700">
										{ml}
									</td>
									<td className="border-t border-slate-100 px-4 py-3 font-semibold text-slate-700">
										{cyber}
									</td>
								</tr>
							))}
						</tbody>
					</table>
				</div>
			</section>
		</div>

		<section className="rounded-3xl border border-cyan-100 bg-gradient-to-r from-cyan-50 to-indigo-50 p-6 shadow-sm backdrop-blur-xl lg:p-8">
			<div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
				<div className="flex gap-4">
					<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white text-cyan-600 shadow-sm">
						<FaWandMagicSparkles />
					</div>
					<div>
						<h2 className="text-xl font-black text-slate-950">
							Our Career Recommendation
						</h2>
						<p className="mt-2 max-w-5xl text-sm font-semibold leading-6 text-slate-700">
							Based on your Computer Science background, strong programming skills,
							and interest in AI, CareerNavigator recommends pursuing Machine
							Learning Engineering. Learning Deep Learning and MLOps will
							significantly increase your readiness.
						</p>
					</div>
				</div>
				<button
					type="button"
					className="inline-flex items-center gap-2 self-start rounded-xl bg-white px-4 py-3 text-sm font-black text-cyan-700 shadow-sm transition hover:shadow-md md:self-auto"
				>
					View Career Roadmap
					<FaArrowRight className="text-xs" />
				</button>
			</div>
		</section>
	</>
);

export default CareerPathDetails;
