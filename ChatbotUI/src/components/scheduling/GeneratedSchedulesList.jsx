import ScheduleCard from "./ScheduleCard.jsx";

const GeneratedSchedulesList = ({
	activatingScheduleId,
	error,
	loading,
	onActivateSchedule,
	onRetry,
	onSelectSchedule,
	schedules,
	selectedScheduleId,
}) => {
	if (loading) {
		return (
			<div className="space-y-3">
				{[0, 1, 2].map((item) => (
					<div
						key={item}
						className="h-32 animate-pulse rounded-lg border border-slate-200 bg-white"
					/>
				))}
			</div>
		);
	}

	if (error) {
		return (
			<div className="rounded-lg border border-rose-100 bg-rose-50 p-4 text-sm text-rose-700">
				<p>{error}</p>
				{onRetry && (
					<button
						type="button"
						onClick={onRetry}
						className="mt-3 rounded-md bg-rose-600 px-3 py-2 text-sm font-semibold text-white hover:bg-rose-700"
					>
						Retry
					</button>
				)}
			</div>
		);
	}

	if (!schedules.length) {
		return (
			<div className="rounded-lg border border-slate-200 bg-white p-5 text-sm text-slate-600">
				No generated schedules were found for this plan.
			</div>
		);
	}

	return (
		<div className="space-y-3">
			{schedules.map((schedule) => (
				<ScheduleCard
					key={schedule.schedule_id}
					schedule={schedule}
					activating={schedule.schedule_id === activatingScheduleId}
					selected={schedule.schedule_id === selectedScheduleId}
					onActivate={onActivateSchedule}
					onSelect={onSelectSchedule}
				/>
			))}
		</div>
	);
};

export default GeneratedSchedulesList;
