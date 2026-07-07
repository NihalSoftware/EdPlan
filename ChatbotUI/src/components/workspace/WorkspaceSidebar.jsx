import { FaShieldHalved, FaWandMagicSparkles } from "react-icons/fa6";
import ActivatedAgents from "./ActivatedAgents.jsx";
import OrchestratorStatus from "./OrchestratorStatus.jsx";
import RecentActivity from "./RecentActivity.jsx";

const WorkspaceSidebar = ({ telemetry, isLoading }) => (
	<aside className="space-y-4">
		<OrchestratorStatus telemetry={telemetry} isLoading={isLoading} />
		<ActivatedAgents telemetry={telemetry} isLoading={isLoading} />
		<RecentActivity telemetry={telemetry} />
		<div className="rounded-2xl border border-indigo-100 bg-gradient-to-br from-indigo-50 to-violet-50 p-4 shadow-sm">
			<div className="flex gap-3">
				<div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white text-indigo-600 shadow-sm">
					<FaWandMagicSparkles />
				</div>
				<div>
					<h3 className="text-sm font-black text-indigo-950">
						Powered by EdPlan Orchestrator
					</h3>
					<p className="mt-2 text-xs font-semibold leading-5 text-slate-600">
						Coordinating specialized agents to deliver accurate, personalized guidance.
					</p>
				</div>
			</div>
			<div className="mt-3 flex items-center gap-2 text-xs font-black text-indigo-700">
				<FaShieldHalved />
				Secure workspace
			</div>
		</div>
	</aside>
);

export default WorkspaceSidebar;
