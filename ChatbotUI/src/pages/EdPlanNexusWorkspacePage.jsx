import { useEffect, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import { FaArrowLeft } from "react-icons/fa6";
import ConversationPanel from "../components/workspace/ConversationPanel.jsx";
import WorkspaceHero from "../components/workspace/WorkspaceHero.jsx";
import WorkspaceSidebar from "../components/workspace/WorkspaceSidebar.jsx";
import { useNexusChat } from "../hooks/useNexusChat.js";

const WorkspaceTopBar = () => (
	<header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 px-5 py-3 backdrop-blur-xl sm:px-7 lg:px-10">
		<div className="flex items-center justify-between gap-4">
			<Link
				to="/edplan-nexus"
				className="inline-flex items-center gap-3 text-sm font-black text-slate-800 transition hover:text-indigo-600"
			>
				<FaArrowLeft className="text-xs" />
				Back to <span className="text-indigo-600">EdPlan Nexus</span>
			</Link>
			<div className="h-9" />
		</div>
	</header>
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
			<div className="mx-auto max-w-[1680px] px-5 py-8 sm:px-7 lg:px-10">
				<div className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_19rem] 2xl:grid-cols-[minmax(0,1fr)_20rem]">
					<main className="min-w-0 space-y-7">
						<WorkspaceHero />
						<ConversationPanel
							messages={messages}
							inputValue={inputValue}
							onInputChange={setInputValue}
							onSubmit={submitMessage}
							isLoading={isLoading}
							formatMessageTime={formatMessageTime}
							onRetry={retryLastMessage}
						/>
					</main>
					<WorkspaceSidebar telemetry={telemetry} isLoading={isLoading} />
				</div>
			</div>
		</section>
	);
};

export default MasterAgentWorkspace;
