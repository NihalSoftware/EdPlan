import { useEffect, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import {
	FaArrowLeft,
	FaBell,
	FaWandMagicSparkles,
} from "react-icons/fa6";
import {
	ConversationArea,
	OrchestratorStatusPanel,
	RobotAvatar,
	SecurityBanner,
	SuggestedPrompts,
} from "../components/chat/NexusChat.jsx";
import { useNexusChat } from "../hooks/useNexusChat.js";

const WorkspaceTopBar = () => (
	<header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 px-5 py-4 backdrop-blur-xl sm:px-8 lg:px-12">
		<div className="flex items-center justify-between gap-4">
			<Link
				to="/edplan-nexus"
				className="inline-flex items-center gap-3 text-sm font-black text-slate-800 transition hover:text-indigo-600"
			>
				<FaArrowLeft className="text-xs" />
				Back to <span className="text-indigo-600">EdPlan Nexus</span>
			</Link>
			<div className="flex items-center gap-5">
				<button
					type="button"
					className="relative flex h-10 w-10 items-center justify-center rounded-full text-slate-700 transition hover:bg-slate-100"
					aria-label="Notifications"
				>
					<FaBell />
					<span className="absolute right-2 top-2 h-2.5 w-2.5 rounded-full bg-indigo-600 ring-2 ring-white" />
				</button>
				<button
					type="button"
					className="flex items-center gap-3 rounded-full border border-slate-200 bg-white py-2 pl-2 pr-4 text-sm font-bold text-slate-800 shadow-sm transition hover:border-indigo-200 hover:shadow-md"
				>
					<span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
						V
					</span>
					Verify it&apos;s you
				</button>
			</div>
		</div>
	</header>
);

const WorkspaceHeader = () => (
	<div className="flex flex-col gap-5 sm:flex-row sm:items-center">
		<RobotAvatar size="lg" />
		<div>
			<h1 className="flex flex-wrap items-center gap-3 text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
				Welcome to EdPlan <span className="text-indigo-600">Nexus</span>
				<FaWandMagicSparkles className="text-2xl text-indigo-500" />
			</h1>
			<p className="mt-3 text-base font-medium text-slate-700 md:text-lg">
				Chat with EdPlan Orchestrator, your AI command center.
			</p>
			<p className="mt-2 text-sm font-semibold text-slate-600 md:text-base">
				How can I help you plan your educational journey today?
			</p>
		</div>
	</div>
);

const MasterAgentWorkspace = () => {
	const location = useLocation();
	const initialPromptHandledRef = useRef(false);
	const {
		messages,
		inputValue,
		setInputValue,
		isLoading,
		telemetry,
		submitMessage,
		retryLastMessage,
		formatMessageTime,
	} = useNexusChat();
	const initialPrompt = location.state?.initialPrompt;

	useEffect(() => {
		if (
			initialPromptHandledRef.current ||
			typeof initialPrompt !== "string" ||
			!initialPrompt.trim()
		) {
			return;
		}
		initialPromptHandledRef.current = true;
		setInputValue(initialPrompt);
		submitMessage(initialPrompt);
	}, [initialPrompt, setInputValue, submitMessage]);

	return (
		<section className="min-h-screen bg-[radial-gradient(circle_at_78%_8%,rgba(99,102,241,0.14),transparent_28%),radial-gradient(circle_at_55%_22%,rgba(167,139,250,0.10),transparent_22%),linear-gradient(135deg,#f8fbff_0%,#ffffff_46%,#f7f5ff_100%)] text-slate-950">
			<WorkspaceTopBar />
			<div className="mx-auto max-w-[1560px] px-5 py-8 sm:px-8 lg:px-12">
				<WorkspaceHeader />
				<div className="mt-9 grid gap-7 xl:grid-cols-[minmax(0,1fr)_20rem] 2xl:grid-cols-[minmax(0,1fr)_22rem]">
					<div>
						<ConversationArea
							messages={messages}
							inputValue={inputValue}
							onInputChange={setInputValue}
							onSubmit={submitMessage}
							isLoading={isLoading}
							formatMessageTime={formatMessageTime}
							onRetry={retryLastMessage}
						/>
						<SuggestedPrompts onSelect={setInputValue} />
					</div>
					<OrchestratorStatusPanel telemetry={telemetry} />
				</div>
				<SecurityBanner />
			</div>
		</section>
	);
};

export default MasterAgentWorkspace;
