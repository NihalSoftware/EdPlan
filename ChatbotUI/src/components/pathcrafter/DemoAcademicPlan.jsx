import {
	FaBookOpen,
	FaCalendarDays,
	FaChartSimple,
	FaClock,
	FaGraduationCap,
	FaStar,
} from "react-icons/fa6";

const summary = [
	["120", "Total Credits", FaGraduationCap],
	["4 Years", "Duration", FaClock],
	["33", "Completed Credits", FaStar],
	["87", "Remaining Credits", FaBookOpen],
	["May 2028", "Expected Graduation", FaCalendarDays],
	["3.62", "Current GPA", FaChartSimple],
];

const semesters = [
	{
		name: "Semester 1",
		credits: 15,
		gpa: "3.70",
		tone: "border-blue-100 bg-blue-50/60 text-blue-700",
		courses: [
			["CS 101", "Introduction to Programming", 4, "Completed"],
			["ENG 111", "College Composition", 3, "Completed"],
			["MATH 151", "Calculus I", 4, "Completed"],
			["UNIV 101", "University Success", 2, "Completed"],
			["COMM 101", "Public Speaking", 2, "Completed"],
		],
	},
	{
		name: "Semester 2",
		credits: 16,
		gpa: "3.54",
		tone: "border-emerald-100 bg-emerald-50/60 text-emerald-700",
		courses: [
			["CS 102", "Data Structures", 4, "Scheduled"],
			["MATH 152", "Calculus II", 4, "Scheduled"],
			["PHYS 101", "Physics I", 4, "Scheduled"],
			["ENG 112", "Technical Writing", 3, "Scheduled"],
			["ART 105", "Creative Elective", 1, "Planned"],
		],
	},
	{
		name: "Semester 3",
		credits: 15,
		gpa: "Projected",
		tone: "border-violet-100 bg-violet-50/60 text-violet-700",
		courses: [
			["CS 201", "Algorithms", 3, "Planned"],
			["CS 210", "Discrete Mathematics", 3, "Planned"],
			["MATH 241", "Linear Algebra", 3, "Planned"],
			["PHYS 102", "Physics II", 4, "Planned"],
			["HIST 111", "Humanities Elective", 2, "Planned"],
		],
	},
	{
		name: "Semester 4",
		credits: 15,
		gpa: "Projected",
		tone: "border-orange-100 bg-orange-50/60 text-orange-700",
		courses: [
			["CS 202", "Object Oriented Programming", 3, "Planned"],
			["CS 215", "Computer Architecture", 3, "Planned"],
			["STAT 201", "Probability & Statistics", 3, "Planned"],
			["DATA 220", "Applied Data Modeling", 3, "Planned"],
			["SOC 101", "Social Science Elective", 3, "Planned"],
		],
	},
];

const DemoAcademicPlan = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-7 shadow-sm backdrop-blur-xl lg:p-9">
		<div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
			<div>
				<h2 className="text-2xl font-black text-slate-950">Demo Academic Plan</h2>
				<p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
					A realistic visual sample for a Computer Science student at Northern New
					Mexico College.
				</p>
			</div>
			<div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-black text-slate-700 shadow-sm">
				Program: B.S. in Computer Science
			</div>
		</div>
		<div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
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
						{semester.courses.map(([code, title, credits, status]) => (
							<div key={code} className="rounded-xl bg-white/85 p-3 text-slate-800">
								<div className="flex items-start justify-between gap-3">
									<div>
										<p className="text-sm font-black">{code}</p>
										<p className="mt-1 text-xs font-semibold leading-5 text-slate-600">
											{title}
										</p>
									</div>
									<span className="text-sm font-black">{credits}</span>
								</div>
								<div className="mt-3 flex items-center justify-between">
									<span className="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-black text-slate-600">
										{status}
									</span>
									<span className="text-[10px] font-black text-slate-500">
										GPA {semester.gpa}
									</span>
								</div>
							</div>
						))}
					</div>
					<div className="mt-5 h-2 overflow-hidden rounded-full bg-white">
						<div className="h-full w-3/5 rounded-full bg-current" />
					</div>
				</article>
			))}
		</div>
	</section>
);

export default DemoAcademicPlan;
