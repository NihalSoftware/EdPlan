import {
	FaBookOpen,
	FaCalendarWeek,
	FaClock,
	FaGraduationCap,
} from "react-icons/fa6";

const summary = [
	["16", "Total Credits", FaGraduationCap],
	["5", "Courses", FaBookOpen],
	["Mon-Fri", "Preferred Days", FaCalendarWeek],
	["8 AM - 6 PM", "Time Range", FaClock],
];

const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const timeRows = [
	"8 AM",
	"9 AM",
	"10 AM",
	"11 AM",
	"12 PM",
	"1 PM",
	"2 PM",
	"3 PM",
	"4 PM",
	"5 PM",
	"6 PM",
];

const courses = [
	{
		code: "CS 102",
		name: "Data Structures",
		day: "Monday",
		time: "9:00 - 10:15",
		room: "STEM 204",
		row: 1,
		height: 2,
		color: "bg-blue-500 text-white",
	},
	{
		code: "MATH 122",
		name: "Calculus II",
		day: "Tuesday",
		time: "10:30 - 11:45",
		room: "Math 118",
		row: 2,
		height: 2,
		color: "bg-emerald-500 text-white",
	},
	{
		code: "PHYS 101",
		name: "Physics I",
		day: "Wednesday",
		time: "1:00 - 2:50",
		room: "Science 310",
		row: 5,
		height: 3,
		color: "bg-violet-500 text-white",
	},
	{
		code: "ENG 102",
		name: "Technical Writing",
		day: "Thursday",
		time: "9:00 - 10:15",
		room: "Liberal Arts 21",
		row: 1,
		height: 2,
		color: "bg-orange-500 text-white",
	},
	{
		code: "CS 210",
		name: "Discrete Mathematics",
		day: "Friday",
		time: "11:00 - 12:15",
		room: "STEM 212",
		row: 3,
		height: 2,
		color: "bg-cyan-600 text-white",
	},
];

const DemoOptimizedSchedule = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-7 shadow-sm backdrop-blur-xl lg:p-9">
		<div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
			<div>
				<h2 className="text-2xl font-black text-slate-950">Demo Optimized Schedule</h2>
				<p className="mt-2 max-w-3xl text-sm font-semibold leading-6 text-slate-600">
					A sample weekly timetable generated for a Computer Science student who
					prefers daytime classes and a balanced credit load.
				</p>
			</div>
			<span className="rounded-full bg-blue-50 px-4 py-2 text-xs font-black text-blue-700">
				Conflict-free option
			</span>
		</div>
		<div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
			{summary.map(([value, label, Icon]) => (
				<div key={label} className="rounded-2xl bg-blue-50/70 p-4">
					<div className="flex items-center gap-3">
						<div className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-blue-600">
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

		<div className="mt-7 overflow-x-auto rounded-2xl border border-slate-200 bg-white">
			<div className="min-w-[920px]">
				<div className="grid grid-cols-[5rem_repeat(5,minmax(0,1fr))] border-b border-slate-200 bg-slate-50">
					<div className="p-3 text-xs font-black uppercase tracking-wide text-slate-500">
						Time
					</div>
					{days.map((day) => (
						<div
							key={day}
							className="border-l border-slate-200 p-3 text-center text-sm font-black text-slate-800"
						>
							{day}
						</div>
					))}
				</div>
				<div className="grid grid-cols-[5rem_repeat(5,minmax(0,1fr))]">
					<div>
						{timeRows.map((time) => (
							<div
								key={time}
								className="flex h-16 items-start justify-center border-b border-slate-100 pt-2 text-xs font-bold text-slate-500"
							>
								{time}
							</div>
						))}
					</div>
					{days.map((day) => (
						<div key={day} className="relative border-l border-slate-200">
							{timeRows.map((time) => (
								<div key={time} className="h-16 border-b border-slate-100" />
							))}
							{courses
								.filter((course) => course.day === day)
								.map((course) => (
									<div
										key={course.code}
										className={`absolute left-2 right-2 rounded-xl p-3 shadow-lg ${course.color}`}
										style={{
											top: `${course.row * 4}rem`,
											height: `${course.height * 4 - 0.5}rem`,
										}}
									>
										<p className="text-sm font-black">{course.code}</p>
										<p className="mt-1 text-xs font-semibold leading-4 opacity-95">
											{course.name}
										</p>
										<p className="mt-2 text-[11px] font-black opacity-90">
											{course.time}
										</p>
										<p className="text-[11px] font-bold opacity-80">{course.room}</p>
									</div>
								))}
						</div>
					))}
				</div>
			</div>
		</div>

		<div className="mt-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
			<div className="flex flex-wrap gap-3">
				{courses.map((course) => (
					<span
						key={course.code}
						className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-black text-slate-700"
					>
						<span className={`h-2.5 w-2.5 rounded-full ${course.color.split(" ")[0]}`} />
						{course.code}
					</span>
				))}
			</div>
			<button
				type="button"
				className="self-start rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-3 text-sm font-black text-white shadow-lg shadow-blue-200 transition hover:-translate-y-0.5 hover:shadow-blue-300 md:self-auto"
			>
				View Alternative Schedules
			</button>
		</div>
	</section>
);

export default DemoOptimizedSchedule;
