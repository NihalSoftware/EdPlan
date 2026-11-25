import {
	FaBookOpen,
	FaCalendarDays,
	FaChartLine,
	FaCircleCheck,
	FaGraduationCap,
	FaUserCheck,
} from "react-icons/fa6";

const stats = [
	["3.48 / 4.00", "Current GPA", "Good", FaChartLine],
	["3.62 / 4.00", "Semester GPA", "Spring 2026", FaCalendarDays],
	["98", "Credits Completed", "of 120", FaBookOpen],
	["22", "Credits Remaining", "to graduate", FaGraduationCap],
	["92%", "Attendance", "This semester", FaUserCheck],
	["82%", "Graduation Progress", "On track", FaCircleCheck],
];

const AcademicDashboard = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<h2 className="text-2xl font-black text-slate-950">Your Academic Overview</h2>
		<div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
			{stats.map(([value, label, detail, Icon]) => (
				<div key={label} className="rounded-2xl bg-emerald-50/60 p-4">
					<div className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-emerald-600">
						<Icon />
					</div>
					<p className="mt-4 text-lg font-black text-slate-950">{value}</p>
					<p className="mt-1 text-xs font-black text-slate-600">{label}</p>
					<p className="mt-1 text-xs font-semibold text-emerald-700">{detail}</p>
				</div>
			))}
		</div>
	</section>
);

export default AcademicDashboard;
