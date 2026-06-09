const WEEKDAYS = [
	{ value: 1, label: "Monday" },
	{ value: 2, label: "Tuesday" },
	{ value: 3, label: "Wednesday" },
	{ value: 4, label: "Thursday" },
	{ value: 5, label: "Friday" },
];

const COLORS = [
	"bg-sky-100 border-sky-300 text-sky-950",
	"bg-emerald-100 border-emerald-300 text-emerald-950",
	"bg-violet-100 border-violet-300 text-violet-950",
	"bg-amber-100 border-amber-300 text-amber-950",
	"bg-rose-100 border-rose-300 text-rose-950",
	"bg-cyan-100 border-cyan-300 text-cyan-950",
];

const minutesFromTime = (value) => {
	if (!value) return null;
	const [hours, minutes] = String(value).split(":").map(Number);
	if (!Number.isFinite(hours) || !Number.isFinite(minutes)) return null;
	return hours * 60 + minutes;
};

const formatTime = (value) => {
	const minutes = minutesFromTime(value);
	if (minutes === null) return "";
	const date = new Date(2026, 0, 1, Math.floor(minutes / 60), minutes % 60);
	return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
};

const courseLabel = (section) => {
	const course = section.offering?.course;
	if (!course) return "Course";
	return course.course_code
		? `${course.course_code} ${course.course_name}`
		: course.course_name;
};

const buildEvents = (sections = []) =>
	sections.flatMap((section, sectionIndex) =>
		(section.meetings || [])
			.filter((meeting) => {
				const weekday = Number(meeting.weekday);
				return (
					weekday >= 1 &&
					weekday <= 5 &&
					minutesFromTime(meeting.start_time) !== null &&
					minutesFromTime(meeting.end_time) !== null
				);
			})
			.map((meeting) => ({
				id: `${section.section_id}-${meeting.meeting_id}`,
				section,
				meeting,
				color: COLORS[sectionIndex % COLORS.length],
				start: minutesFromTime(meeting.start_time),
				end: minutesFromTime(meeting.end_time),
			}))
	);

const getBounds = (events) => {
	if (!events.length) return { start: 8 * 60, end: 17 * 60 };
	const earliest = Math.min(...events.map((event) => event.start));
	const latest = Math.max(...events.map((event) => event.end));
	const start = Math.max(0, Math.floor(earliest / 60) * 60);
	const end = Math.min(24 * 60, Math.ceil(latest / 60) * 60);
	return { start, end: Math.max(end, start + 60) };
};

const WeeklyCalendar = ({ schedule }) => {
	const events = buildEvents(schedule?.sections || []);
	const { start, end } = getBounds(events);
	const slotCount = Math.max(1, (end - start) / 60);
	const hourSlots = Array.from({ length: slotCount + 1 }, (_, index) => start + index * 60);
	const totalMinutes = end - start;
	const calendarHeight = Math.max(520, slotCount * 72);

	return (
		<section className="rounded-lg border border-slate-200 bg-white">
			<div className="border-b border-slate-200 px-5 py-4">
				<h2 className="text-lg font-semibold text-slate-900">Weekly Calendar</h2>
				<p className="mt-1 text-sm text-slate-500">
					Monday-Friday view of selected section meetings.
				</p>
			</div>

			{!events.length ? (
				<div className="p-6 text-sm text-slate-600">
					This schedule has no weekday meeting times to display.
				</div>
			) : (
				<div className="overflow-x-auto">
					<div className="min-w-[860px]">
						<div className="grid grid-cols-[72px_repeat(5,minmax(140px,1fr))] border-b border-slate-200 bg-slate-50">
							<div className="px-3 py-3 text-xs font-semibold uppercase text-slate-500">
								Time
							</div>
							{WEEKDAYS.map((day) => (
								<div
									key={day.value}
									className="border-l border-slate-200 px-3 py-3 text-sm font-semibold text-slate-700"
								>
									{day.label}
								</div>
							))}
						</div>

						<div
							className="relative grid grid-cols-[72px_repeat(5,minmax(140px,1fr))]"
							style={{ height: calendarHeight }}
						>
							<div className="relative border-r border-slate-200 bg-slate-50">
								{hourSlots.map((slot) => (
									<div
										key={slot}
										className="absolute left-0 right-0 -translate-y-2 px-3 text-xs text-slate-500"
										style={{ top: `${((slot - start) / totalMinutes) * 100}%` }}
									>
										{formatTime(`${Math.floor(slot / 60)}:${slot % 60}`)}
									</div>
								))}
							</div>

							{WEEKDAYS.map((day) => (
								<div key={day.value} className="relative border-l border-slate-200">
									{hourSlots.map((slot) => (
										<div
											key={slot}
											className="absolute left-0 right-0 border-t border-slate-100"
											style={{ top: `${((slot - start) / totalMinutes) * 100}%` }}
										/>
									))}

									{events
										.filter((event) => Number(event.meeting.weekday) === day.value)
										.map((event) => {
											const top = ((event.start - start) / totalMinutes) * 100;
											const height = ((event.end - event.start) / totalMinutes) * 100;
											const room = [event.meeting.building, event.meeting.room]
												.filter(Boolean)
												.join(" ");
											return (
												<div
													key={event.id}
													className={`absolute left-2 right-2 overflow-hidden rounded-md border px-2 py-2 text-xs shadow-sm ${event.color}`}
													style={{
														top: `${top}%`,
														height: `${Math.max(height, 7)}%`,
													}}
													title={`${courseLabel(event.section)} ${formatTime(
														event.meeting.start_time
													)}-${formatTime(event.meeting.end_time)}`}
												>
													<p className="truncate font-semibold">
														{courseLabel(event.section)}
													</p>
													<p className="truncate">
														{formatTime(event.meeting.start_time)} -{" "}
														{formatTime(event.meeting.end_time)}
													</p>
													<p className="truncate">
														{event.section.instructor || "Instructor TBA"}
													</p>
													<p className="truncate">{room || "Room TBA"}</p>
												</div>
											);
										})}
								</div>
							))}
						</div>
					</div>
				</div>
			)}
		</section>
	);
};

export default WeeklyCalendar;
