import { FaClock, FaCircleCheck } from "react-icons/fa6";

const RecentActivity = ({ telemetry }) => {
	const workflow = telemetry.workflow || [];

	return (
		<section className="rounded-3xl border border-slate-200 bg-white/80 p-4 shadow-sm backdrop-blur-xl">
			<h2 className="mb-4 text-base font-black text-slate-950">Recent Activity</h2>
			{workflow.length ? (
				<div className="space-y-0">
					{workflow.map((event, index) => (
						<div key={`${event.status || "event"}-${index}`} className="flex gap-3">
							<div className="flex flex-col items-center">
								<div className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-50 text-indigo-600">
									<FaCircleCheck className="text-sm" />
								</div>
								{index < workflow.length - 1 && (
									<div className="h-7 w-px bg-indigo-100" />
								)}
							</div>
							<div className="pb-3">
								<p className="text-sm font-black text-slate-900">
									{event.status || event.step || "Workflow step"}
								</p>
								{event.detail && (
									<p className="mt-1 text-xs font-semibold leading-5 text-slate-500">
										{event.detail}
									</p>
								)}
							</div>
						</div>
					))}
				</div>
			) : (
				<div className="flex min-h-24 flex-col items-center justify-center rounded-2xl border border-slate-100 bg-white/70 p-4 text-center">
					<FaClock className="text-2xl text-slate-400" />
					<p className="mt-3 text-sm font-black text-slate-500">No recent activity</p>
					<p className="mt-1 text-xs font-semibold leading-5 text-slate-400">
						Your interactions will appear here.
					</p>
				</div>
			)}
		</section>
	);
};

export default RecentActivity;
