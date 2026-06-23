import clsx from "clsx";

const formatDate = (value) => {
	if (!value) return "Not saved";
	const date = new Date(value);
	return Number.isNaN(date.getTime())
		? "Not saved"
		: date.toLocaleString([], {
				month: "short",
				day: "numeric",
				year: "numeric",
				hour: "numeric",
				minute: "2-digit",
		  });
};

const ScheduleCard = ({
	activating,
	onActivate,
	onSelect,
	schedule,
	selected,
}) => (
	<div
		role="button"
		tabIndex={0}
		onClick={() => onSelect(schedule)}
		onKeyDown={(event) => {
			if (event.key === "Enter" || event.key === " ") {
				event.preventDefault();
				onSelect(schedule);
			}
		}}
		className={clsx(
			"w-full cursor-pointer text-left rounded-lg border bg-white p-4 transition",
			selected
				? "border-[#016ce6] shadow-md ring-2 ring-[#016ce6]/15"
				: "border-slate-200 hover:border-slate-300 hover:shadow-sm"
		)}
	>
		<div className="flex items-start justify-between gap-3">
			<div>
				<p className="text-sm font-semibold text-slate-900">
					{schedule.sections?.length || 0} sections
				</p>
				<p className="mt-1 text-xs text-slate-500">
					Generated {formatDate(schedule.generated_at)}
				</p>
			</div>
			<span
				className={clsx(
					"rounded-full px-2.5 py-1 text-xs font-semibold",
					schedule.status === "Active"
						? "bg-blue-100 text-blue-700"
						: schedule.conflict_count
						? "bg-rose-100 text-rose-700"
						: "bg-emerald-100 text-emerald-700"
				)}
			>
				{schedule.status === "Active"
					? "Active"
					: `${schedule.conflict_count || 0} conflicts`}
			</span>
		</div>

		<div className="mt-4 grid grid-cols-2 gap-3 text-sm">
			<div>
				<p className="text-xs uppercase text-slate-500">Credits</p>
				<p className="font-semibold text-slate-900">{schedule.total_credits}</p>
			</div>
			<div>
				<p className="text-xs uppercase text-slate-500">Meeting Hours</p>
				<p className="font-semibold text-slate-900">
					{schedule.total_meeting_hours ?? 0}
				</p>
			</div>
		</div>
		<button
			type="button"
			onClick={(event) => {
				event.stopPropagation();
				onActivate(schedule);
			}}
			disabled={activating || schedule.status === "Active"}
			className={clsx(
				"mt-4 min-h-10 w-full rounded-md px-3 text-sm font-semibold transition",
				schedule.status === "Active"
					? "cursor-default bg-blue-100 text-blue-700"
					: "bg-slate-900 text-white hover:bg-slate-700",
				activating && "cursor-wait opacity-70"
			)}
		>
			{schedule.status === "Active"
				? "Active Schedule"
				: activating
				? "Activating..."
				: "Use This Schedule"}
		</button>
	</div>
);

export default ScheduleCard;
