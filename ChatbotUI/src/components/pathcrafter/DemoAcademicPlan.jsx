import {
	FaBookOpen,
	FaCalendarDays,
	FaGraduationCap,
	FaLayerGroup,
} from "react-icons/fa6";
import { FaClipboardList } from "react-icons/fa";

const summary = [
	["120", "Total Credits", FaGraduationCap],
	["8", "Semesters", FaCalendarDays],
	["42", "Total Courses", FaBookOpen],
	["18", "Electives", FaClipboardList],
	["May 2028", "Expected Graduation", FaCalendarDays],
];

const semesters = [
	{
		name: "Semester 1",
		credits: 15,
		tone: "border-blue-100 bg-blue-50/60 text-blue-700",
		courses: [
			["CS 101", 4],
			["MATH 121", 4],
			["ENG 111", 3],
			["UNIV 101", 2],
			["SCI 101", 2],
		],
	},
	{
		name: "Semester 2",
		credits: 15,
		tone: "border-emerald-100 bg-emerald-50/60 text-emerald-700",
		courses: [
			["CS 102", 4],
			["MATH 122", 4],
			["PHYS 101", 4],
			["ENG 102", 3],
		],
	},
	{
		name: "Semester 3",
		credits: 15,
		tone: "border-violet-100 bg-violet-50/60 text-violet-700",
		courses: [
			["CS 201", 4],
			["MATH 241", 4],
			["PHYS 102", 4],
			["CS 210", 3],
		],
	},
	{
		name: "Semester 4",
		credits: 14,
		tone: "border-orange-100 bg-orange-50/60 text-orange-700",
		courses: [
			["CS 202", 4],
			["CS 215", 4],
			["STAT 201", 3],
			["Humanities Elective", 3],
		],
	},
];

const DemoAcademicPlan = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
			<div>
				<h2 className="text-2xl font-black text-slate-950">Demo Academic Plan</h2>
				<p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
					Sample 4-year plan for a B.S. in Computer Science student.
				</p>
			</div>
			<div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-black text-slate-700 shadow-sm">
				Program: B.S. in Computer Science
			</div>
		</div>
		<div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
			{summary.map(([value, label, Icon]) => (
				<div key={label} className="rounded-2xl bg-indigo-50/60 p-4">
					<div className="flex items-center gap-3">
						<div className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-indigo-600">
							<Icon />
						</div>
						<div>
							<p className="text-lg font-black text-slate-950">{value}</p>
							<p className="text-xs font-bold text-slate-500">{label}</p>
						</div>
					</div>
				</div>
			))}
		</div>
		<div className="mt-6 grid gap-5 lg:grid-cols-4">
			{semesters.map((semester) => (
				<article key={semester.name} className={`rounded-2xl border p-5 ${semester.tone}`}>
					<div className="mb-4 flex items-center justify-between">
						<h3 className="font-black">{semester.name}</h3>
						<span className="rounded-full bg-white/80 px-3 py-1 text-xs font-black">
							{semester.credits} Credits
						</span>
					</div>
					<div className="space-y-3">
						{semester.courses.map(([courseName, credits]) => (
							<div key={courseName} className="rounded-xl bg-white/85 p-3 text-slate-800">
								<div className="flex items-center justify-between gap-3">
									<p className="text-sm font-black">{courseName}</p>
									<span className="text-sm font-black">{credits}</span>
								</div>
							</div>
						))}
					</div>
					<div className="mt-5 flex items-center justify-between border-t border-white/80 pt-4">
						<span className="text-sm font-black">Total Credits</span>
						<span className="text-sm font-black">{semester.credits}</span>
					</div>
				</article>
			))}
		</div>
		<div className="mt-6 flex justify-center">
			<button
				type="button"
				className="inline-flex items-center gap-3 rounded-xl border border-indigo-100 bg-indigo-50 px-5 py-3 text-sm font-black text-indigo-700 shadow-sm transition hover:border-indigo-200 hover:bg-white hover:shadow-md"
			>
				Show Year 2 (Semesters 5-8)
				<FaLayerGroup className="text-xs" />
			</button>
		</div>
	</section>
);

export default DemoAcademicPlan;
