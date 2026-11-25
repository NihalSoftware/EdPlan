export const OrchestratorAvatar = ({ size = "md", className = "" }) => {
	const sizeClasses = {
		sm: "h-10 w-10 rounded-2xl",
		md: "h-14 w-14 rounded-[1.25rem]",
		lg: "h-20 w-20 rounded-[1.75rem]",
	};
	const faceClasses = {
		sm: "h-6 w-8 rounded-xl gap-1.5",
		md: "h-8 w-11 rounded-2xl gap-2",
		lg: "h-10 w-14 rounded-[1.35rem] gap-2.5",
	};
	const dotClasses = size === "lg" ? "h-2 w-2" : "h-1.5 w-1.5";

	return (
		<div
			className={`edplan-nexus-glow relative flex ${sizeClasses[size]} items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-violet-100 shadow-xl shadow-indigo-200 ${className}`}
		>
			<div className="absolute -top-3 h-4 w-2 rounded-full bg-indigo-500">
				<span className="absolute -top-1.5 left-1/2 h-2.5 w-2.5 -translate-x-1/2 rounded-full bg-indigo-500" />
			</div>
			<div className="absolute -left-1.5 h-7 w-2.5 rounded-full bg-indigo-500/80" />
			<div className="absolute -right-1.5 h-7 w-2.5 rounded-full bg-indigo-500/80" />
			<div
				className={`flex ${faceClasses[size]} items-center justify-center bg-gradient-to-b from-indigo-600 to-indigo-800 shadow-inner`}
			>
				<span className={`${dotClasses} rounded-full bg-sky-100`} />
				<span className={`${dotClasses} rounded-full bg-sky-100`} />
			</div>
		</div>
	);
};

const WorkspaceHero = () => (
	<section className="relative overflow-hidden rounded-[2rem] border border-indigo-100 bg-white/80 px-6 py-7 shadow-[0_24px_70px_rgba(79,70,229,0.10)] backdrop-blur-xl sm:px-8">
		<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_28%,rgba(99,102,241,0.13),transparent_25%),radial-gradient(circle_at_86%_10%,rgba(167,139,250,0.12),transparent_26%)]" />
		<div className="relative flex min-w-0 flex-col gap-5 sm:flex-row sm:items-center">
			<OrchestratorAvatar size="lg" className="shrink-0" />
			<div className="min-w-0">
				<h1 className="max-w-[36rem] text-[clamp(1.9rem,2.2vw,2.65rem)] font-black leading-[1.12] tracking-tight text-slate-950">
					Welcome to EdPlan <span className="text-indigo-600">Nexus</span>
				</h1>
				<p className="mt-3 max-w-3xl text-sm font-bold leading-7 text-slate-700 md:text-base">
					Chat with EdPlan Orchestrator, your AI academic planning command center.
				</p>
				<p className="mt-1.5 text-sm font-semibold leading-6 text-slate-500">
					How can I help you plan your educational journey today?
				</p>
			</div>
		</div>
	</section>
);

export default WorkspaceHero;
