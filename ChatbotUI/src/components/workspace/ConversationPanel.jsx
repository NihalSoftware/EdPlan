import { useEffect, useRef } from "react";
import { FaTriangleExclamation } from "react-icons/fa6";
import { MESSAGE_ROLES, MESSAGE_STATUS } from "../../types/nexusChatTypes.js";
import MessageComposer from "./MessageComposer.jsx";
import PromptChips from "./PromptChips.jsx";
import UserAvatar from "./UserAvatar.jsx";
import { OrchestratorAvatar } from "./WorkspaceHero.jsx";

const InitialAssistantMessage = ({ formatMessageTime }) => (
	<div className="flex items-start gap-4">
		<OrchestratorAvatar size="sm" className="mt-1 shrink-0" />
		<div className="max-w-[75%] rounded-3xl border border-slate-200 bg-white px-5 py-4 shadow-sm max-lg:max-w-[86%]">
			<div className="mb-2 flex flex-wrap items-center gap-2">
				<p className="font-black text-slate-950">EdPlan Orchestrator</p>
				<span className="rounded-full bg-indigo-100 px-2.5 py-1 text-[10px] font-black uppercase tracking-wide text-indigo-700">
					AI
				</span>
			</div>
			<p className="whitespace-pre-line text-sm font-semibold leading-7 text-slate-700">
				Hello! I&apos;m your EdPlan Orchestrator.
				{"\n\n"}I can help you with academic planning, university comparisons,
				education costs, scholarships, scheduling, career planning, and much more.
				{"\n\n"}What would you like to work on today?
			</p>
			<p className="mt-3 text-xs font-semibold text-slate-400">
				{formatMessageTime(new Date())}
			</p>
		</div>
	</div>
);

const TypingIndicator = () => (
	<div className="flex items-start gap-4">
		<OrchestratorAvatar size="sm" className="mt-1 shrink-0" />
		<div className="rounded-3xl border border-slate-200 bg-white px-5 py-3.5 shadow-sm">
			<div className="edplan-nexus-typing flex items-center gap-3">
				<span />
				<span />
				<span />
			</div>
		</div>
	</div>
);

const WorkflowBadge = ({ workflow = [], status }) => {
	const latest = workflow[workflow.length - 1]?.status || status;
	if (!latest || status === MESSAGE_STATUS.ERROR) return null;

	return (
		<span className="mb-2 inline-flex rounded-full bg-indigo-50 px-3 py-1 text-xs font-black text-indigo-700">
			{latest}
		</span>
	);
};

const ChatBubble = ({ message, formatMessageTime, onRetry }) => {
	const isUser = message.role === MESSAGE_ROLES.USER;
	const isError = message.status === MESSAGE_STATUS.ERROR;
	const isLoading = message.status === MESSAGE_STATUS.LOADING;

	if (isLoading) return <TypingIndicator />;

	return (
		<div className={`flex items-start gap-4 ${isUser ? "justify-end" : ""}`}>
			{!isUser && <OrchestratorAvatar size="sm" className="mt-1 shrink-0" />}
			<div className={isUser ? "flex max-w-[74%] flex-col items-end max-lg:max-w-[86%]" : "max-w-[75%] max-lg:max-w-[86%]"}>
				{!isUser && <WorkflowBadge workflow={message.workflow} status={message.status} />}
				<div
					className={
						isUser
							? "rounded-3xl border border-indigo-200 bg-gradient-to-br from-indigo-50 to-violet-50 px-6 py-5 text-indigo-950 shadow-sm"
							: isError
							? "rounded-3xl border border-rose-200 bg-rose-50 px-5 py-4 text-rose-950 shadow-sm"
							: "rounded-3xl border border-slate-200 bg-white px-5 py-4 text-slate-950 shadow-sm"
					}
				>
					{isError && (
						<div className="mb-3 flex items-center gap-2 text-sm font-black text-rose-700">
							<FaTriangleExclamation />
							Request failed
						</div>
					)}
					<p className="whitespace-pre-line text-sm font-semibold leading-7">
						{message.content}
					</p>
					<div className="mt-3 flex items-center justify-between gap-4">
						<p className="text-xs font-semibold text-slate-400">
							{formatMessageTime(message.createdAt)}
						</p>
						{isError && (
							<button
								type="button"
								onClick={onRetry}
								className="text-xs font-black text-rose-700 transition hover:text-rose-600"
							>
								Retry
							</button>
						)}
					</div>
				</div>
			</div>
			{isUser && <UserAvatar />}
		</div>
	);
};

const ConversationPanel = ({
	messages,
	inputValue,
	onInputChange,
	onSubmit,
	isLoading,
	formatMessageTime,
	onRetry,
}) => {
	const bottomRef = useRef(null);

	useEffect(() => {
		bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
	}, [messages, isLoading]);

	return (
		<section className="flex h-[clamp(34rem,70vh,46rem)] min-h-0 flex-col gap-4 rounded-[2rem] border border-slate-200 bg-white/70 p-4 shadow-sm backdrop-blur-xl lg:p-5">
			<div className="min-h-0 flex-1 space-y-5 overflow-y-auto scroll-smooth rounded-[1.5rem] border border-slate-100 bg-white/45 p-4 pr-3 lg:p-5 lg:pr-4">
				{messages.length === 0 ? (
					<>
						<div className="flex justify-center">
							<span className="rounded-full bg-slate-100 px-4 py-1.5 text-xs font-black text-slate-600">
								Today
							</span>
						</div>
						<InitialAssistantMessage formatMessageTime={formatMessageTime} />
						<PromptChips onSelect={onInputChange} />
					</>
				) : (
					messages.map((message) => (
						<ChatBubble
							key={message.id}
							message={message}
							formatMessageTime={formatMessageTime}
							onRetry={onRetry}
						/>
					))
				)}
				<div ref={bottomRef} />
			</div>
			<MessageComposer
				value={inputValue}
				onChange={onInputChange}
				onSubmit={onSubmit}
				isLoading={isLoading}
			/>
			<p className="text-center text-xs font-semibold text-slate-400">
				EdPlan Orchestrator may use specialized agents to answer your questions.
			</p>
		</section>
	);
};

export default ConversationPanel;
