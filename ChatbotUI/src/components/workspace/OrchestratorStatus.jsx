import {
	FaBolt,
	FaBullseye,
	FaChartSimple,
	FaCircleCheck,
	FaClock,
} from "react-icons/fa6";

const emptyValue = "-";

const formatConfidence = (value) => {
	if (typeof value !== "number") return emptyValue;
	return value <= 1 ? `${Math.round(value * 100)}%` : `${Math.round(value)}%`;
};

const formatExecutionTime = (value) => {
	if (typeof value !== "number") return emptyValue;
	return `${value.toFixed(value < 1 ? 2 : 1)} seconds`;
};

const StatusItem = ({ icon: Icon, label, value }) => (
	<div className="rounded-2xl border border-slate-100 bg-white/80 p-3.5">
		<div className="flex items-center gap-3">
			<div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-sm text-indigo-600">
				<Icon />
			</div>
			<div className="min-w-0">
				<p className="text-[11px] font-black uppercase tracking-wide text-slate-400">
					{label}
				</p>
				<p className="mt-1 break-words text-[13px] font-black text-slate-900">{value}</p>
			</div>
		</div>
	</div>
);

const OrchestratorStatus = ({ telemetry, isLoading }) => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-4 shadow-sm backdrop-blur-xl">
		<div className="mb-4 flex items-center justify-between gap-3">
			<h2 className="text-base font-black text-slate-950">Orchestrator Status</h2>
			<span
				className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-black ${
					isLoading ? "bg-amber-50 text-amber-700" : "bg-emerald-50 text-emerald-700"
				}`}
			>
				<FaBolt />
				{isLoading ? "Running" : "Live"}
			</span>
		</div>
		<div className="space-y-3">
			<StatusItem
				icon={FaBullseye}
				label="Current Intent"
				value={telemetry.currentIntent || emptyValue}
			/>
			<StatusItem
				icon={FaChartSimple}
				label="Confidence"
				value={formatConfidence(telemetry.confidence)}
			/>
			<StatusItem
				icon={FaClock}
				label="Execution Time"
				value={formatExecutionTime(telemetry.executionTime)}
			/>
			{telemetry.finalStatus && (
				<StatusItem
					icon={FaCircleCheck}
					label="Final Status"
					value={telemetry.finalStatus}
				/>
			)}
		</div>
	</section>
);

export default OrchestratorStatus;
