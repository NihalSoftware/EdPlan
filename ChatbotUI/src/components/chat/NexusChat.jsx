import { useEffect, useRef } from "react";
import {
	FaArrowUpRightFromSquare,
	FaBriefcase,
	FaBuildingColumns,
	FaClipboardList,
	FaGraduationCap,
	FaPaperPlane,
	FaRobot,
	FaShieldHalved,
	FaTriangleExclamation,
} from "react-icons/fa6";
import { FaDollarSign } from "react-icons/fa";
import { MESSAGE_ROLES, MESSAGE_STATUS } from "../../types/nexusChatTypes.js";

export const suggestedPrompts = [
	{
		icon: FaGraduationCap,
		text: "Help me create a 4-year academic plan for Computer Science.",
		tone: "violet",
	},
	{
		icon: FaBuildingColumns,
		text: "Compare top universities for Data Science in the USA.",
		tone: "cyan",
	},
	{
		icon: FaDollarSign,
		text: "Estimate the cost of studying abroad and scholarship options.",
		tone: "amber",
	},
	{
		icon: FaBriefcase,
		text: "What are the career opportunities after graduation?",
		tone: "indigo",
	},
	{
		icon: FaClipboardList,
		text: "Help me find courses that match my interests.",
		tone: "purple",
	},
];

const toneClasses = {
	violet: "bg-violet-50 text-violet-700 ring-violet-100",
	cyan: "bg-cyan-50 text-cyan-700 ring-cyan-100",
	amber: "bg-amber-50 text-amber-600 ring-amber-100",
	indigo: "bg-indigo-50 text-indigo-700 ring-indigo-100",
	purple: "bg-purple-50 text-purple-700 ring-purple-100",
};

const emptyValue = "Pending";

export const RobotAvatar = ({ size = "md", className = "" }) => {
	const sizeClasses = {
		sm: "h-10 w-10 rounded-2xl",
		md: "h-16 w-16 rounded-[1.5rem]",
		lg: "h-24 w-24 rounded-[2rem]",
	};

	return (
		<div
			className={`edplan-nexus-glow relative flex ${sizeClasses[size]} items-center justify-center bg-gradient-to-br from-indigo-50 to-violet-100 shadow-xl shadow-indigo-200 ${className}`}
		>
			<div className="absolute -top-3 h-4 w-2 rounded-full bg-indigo-500">
				<span className="absolute -top-1.5 left-1/2 h-2.5 w-2.5 -translate-x-1/2 rounded-full bg-indigo-500" />
			</div>
			<div className="absolute -left-1.5 h-7 w-2.5 rounded-full bg-indigo-500/80" />
			<div className="absolute -right-1.5 h-7 w-2.5 rounded-full bg-indigo-500/80" />
			<div className="flex h-8 w-12 items-center justify-center rounded-2xl bg-gradient-to-b from-indigo-600 to-indigo-800 shadow-inner sm:h-9 sm:w-14">
				<div className="flex items-center gap-2.5">
					<span className="h-1.5 w-1.5 rounded-full bg-sky-100" />
					<span className="h-1.5 w-1.5 rounded-full bg-sky-100" />
				</div>
			</div>
		</div>
	);
};

export const StatusChip = ({ workflow = [], status }) => {
	const latest = workflow[workflow.length - 1]?.status || status;
	if (!latest) return null;

	return (
		<div className="mb-3 inline-flex rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-xs font-black text-indigo-700">
			{latest}
		</div>
	);
};

export const TypingIndicator = () => (
	<div className="flex items-start gap-4">
		<RobotAvatar size="sm" className="mt-2 shrink-0" />
		<div className="rounded-2xl border border-slate-200 bg-white px-7 py-4 shadow-sm">
			<div className="edplan-nexus-typing flex items-center gap-3">
				<span />
				<span />
				<span />
			</div>
		</div>
	</div>
);

export const ChatBubble = ({ message, formatMessageTime, onRetry }) => {
	const isUser = message.role === MESSAGE_ROLES.USER;
	const isError = message.status === MESSAGE_STATUS.ERROR;
	const isLoading = message.status === MESSAGE_STATUS.LOADING;

	if (isLoading) {
		return <TypingIndicator />;
	}

	return (
		<div className={`flex items-start gap-4 ${isUser ? "justify-end" : ""}`}>
			{!isUser && <RobotAvatar size="sm" className="mt-2 shrink-0" />}
			<div>
				{!isUser && <StatusChip workflow={message.workflow} status={message.status} />}
				<div
					className={
						isUser
							? "max-w-[30rem] rounded-3xl border border-indigo-200 bg-gradient-to-br from-indigo-50 to-violet-50 px-6 py-5 text-indigo-950 shadow-sm"
							: isError
							? "max-w-[36rem] rounded-3xl border border-rose-200 bg-rose-50 px-6 py-5 text-rose-950 shadow-sm"
							: "max-w-[36rem] rounded-3xl border border-slate-200 bg-white/95 px-6 py-5 text-slate-950 shadow-sm"
					}
				>
					{isError && (
						<div className="mb-3 flex items-center gap-2 text-sm font-black text-rose-700">
							<FaTriangleExclamation />
							Request failed
						</div>
					)}
					<p className="whitespace-pre-line text-sm font-medium leading-7 md:text-base">
						{message.content}
					</p>
					<div className="mt-4 flex items-center justify-between gap-4">
						<p className="text-xs font-semibold text-slate-500">
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
			{isUser && (
				<div className="mt-2 flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 font-black text-white shadow-lg shadow-indigo-200">
					V
				</div>
			)}
		</div>
	);
};

export const MessageInput = ({
	value,
	onChange,
	onSubmit,
	isLoading,
}) => {
	const canSend = value.trim().length > 0 && !isLoading;

	const handleKeyDown = (event) => {
		if (event.key === "Enter" && !event.shiftKey) {
			event.preventDefault();
			onSubmit();
		}
	};

	return (
		<div className="mt-8 flex items-end gap-3 rounded-2xl border border-slate-200 bg-white px-5 py-3 shadow-sm transition focus-within:border-indigo-300 focus-within:shadow-lg focus-within:shadow-indigo-100">
			<textarea
				value={value}
				onChange={(event) => onChange(event.target.value)}
				onKeyDown={handleKeyDown}
				placeholder="Type your message here..."
				rows={1}
				className="max-h-36 min-h-12 flex-1 resize-none bg-transparent py-3 text-sm font-semibold text-slate-800 outline-none placeholder:text-slate-400 md:text-base"
			/>
			<button
				type="button"
				aria-label="Send message"
				disabled={!canSend}
				onClick={onSubmit}
				className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-xl shadow-indigo-200 transition hover:-translate-y-0.5 hover:shadow-indigo-300 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0"
			>
				<FaPaperPlane />
			</button>
		</div>
	);
};

export const ConversationArea = ({
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
		<div className="rounded-3xl border border-slate-200 bg-white/70 p-5 shadow-sm backdrop-blur-xl sm:p-6">
			<div className="min-h-[27rem] space-y-7">
				{messages.length === 0 ? (
					<div className="flex min-h-[22rem] items-center justify-center text-center">
						<div className="max-w-md">
							<div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50 text-2xl text-indigo-600">
								<FaRobot />
							</div>
							<h2 className="text-xl font-black text-slate-950">
								Ask EdPlan Orchestrator anything.
							</h2>
							<p className="mt-3 text-sm font-medium leading-6 text-slate-600">
								Your request will be routed through the existing EdPlan Orchestrator
								and returned here when processing completes.
							</p>
						</div>
					</div>
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
			<MessageInput
				value={inputValue}
				onChange={onInputChange}
				onSubmit={onSubmit}
				isLoading={isLoading}
			/>
		</div>
	);
};

export const SuggestedPromptCard = ({ prompt, onSelect }) => {
	const Icon = prompt.icon;

	return (
		<button
			type="button"
			onClick={() => onSelect(prompt.text)}
			className="group flex min-h-24 items-center gap-4 rounded-2xl border border-slate-200 bg-white/85 p-4 text-left shadow-sm transition duration-300 hover:-translate-y-1 hover:border-indigo-100 hover:shadow-xl hover:shadow-indigo-100/70"
		>
			<span
				className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-full text-xl ring-1 ${toneClasses[prompt.tone]}`}
			>
				<Icon />
			</span>
			<span className="text-sm font-semibold leading-6 text-slate-900">
				{prompt.text}
			</span>
		</button>
	);
};

export const SuggestedPrompts = ({ onSelect }) => (
	<div className="mt-7">
		<h2 className="text-xl font-black text-slate-950">Suggested Prompts</h2>
		<div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
			{suggestedPrompts.map((prompt) => (
				<SuggestedPromptCard
					key={prompt.text}
					prompt={prompt}
					onSelect={onSelect}
				/>
			))}
		</div>
	</div>
);

const formatConfidence = (value) =>
	typeof value === "number" ? `${Math.round(value * 100)}%` : emptyValue;

export const OrchestratorStatusPanel = ({ telemetry }) => (
	<aside className="space-y-5">
		<div className="rounded-3xl border border-slate-200 bg-white/75 p-7 shadow-sm backdrop-blur-xl">
			<h2 className="mb-6 text-xl font-black text-slate-950">
				Orchestrator Status
			</h2>
			<div className="space-y-4">
				<StatusRow label="Current Intent" value={telemetry.currentIntent || emptyValue} />
				<StatusRow label="Confidence" value={formatConfidence(telemetry.confidence)} />
				<StatusRow
					label="Execution Time"
					value={
						typeof telemetry.executionTime === "number"
							? `${telemetry.executionTime}s`
							: emptyValue
					}
				/>
			</div>
			<div className="mt-7">
				<h3 className="text-sm font-black uppercase tracking-wide text-slate-500">
					Activated Agents
				</h3>
				<div className="mt-3 flex flex-wrap gap-2">
					{telemetry.activatedModules.length ? (
						telemetry.activatedModules.map((moduleName) => (
							<span
								key={moduleName}
								className="rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-xs font-black text-indigo-700"
							>
								{moduleName}
							</span>
						))
					) : (
						<span className="text-sm font-semibold text-slate-500">
							No agents activated yet
						</span>
					)}
				</div>
			</div>
			<div className="mt-7">
				<h3 className="text-sm font-black uppercase tracking-wide text-slate-500">
					Workflow
				</h3>
				<div className="mt-4 space-y-3">
					{telemetry.workflow.length ? (
						telemetry.workflow.map((event, index) => (
							<div key={`${event.status}-${index}`} className="flex gap-3">
								<div className="mt-1 h-2.5 w-2.5 rounded-full bg-indigo-500" />
								<div>
									<p className="text-sm font-black text-slate-900">{event.status}</p>
									{event.detail && (
										<p className="mt-1 text-xs font-medium text-slate-500">
											{event.detail}
										</p>
									)}
								</div>
							</div>
						))
					) : (
						<p className="text-sm font-semibold text-slate-500">
							Waiting for your first message
						</p>
					)}
				</div>
			</div>
		</div>
		<div className="flex items-center gap-4 rounded-2xl border border-indigo-100 bg-indigo-50/70 p-5 text-sm font-semibold leading-6 text-slate-700 shadow-sm">
			<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white text-indigo-600">
				<FaShieldHalved />
			</div>
			<p>Powered by the existing EdPlan Orchestrator backend.</p>
		</div>
	</aside>
);

const StatusRow = ({ label, value }) => (
	<div className="rounded-2xl border border-slate-100 bg-white/80 p-4">
		<p className="text-xs font-black uppercase tracking-wide text-slate-500">
			{label}
		</p>
		<p className="mt-2 break-words text-sm font-black text-slate-950">{value}</p>
	</div>
);

export const SecurityBanner = () => (
	<div className="mt-8 rounded-2xl border border-indigo-100 bg-white/75 p-5 shadow-sm backdrop-blur-xl">
		<div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
			<div className="flex items-center gap-5">
				<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-indigo-50 text-xl text-slate-600">
					<FaShieldHalved />
				</div>
				<div>
					<h3 className="font-black text-slate-900">
						Your data is secure and private.
					</h3>
					<p className="mt-1 text-sm font-medium leading-6 text-slate-600">
						EdPlan Nexus sends your request only to the EdPlan Orchestrator.
						No conversation persistence is enabled in this workspace.
					</p>
				</div>
			</div>
			<button
				type="button"
				className="inline-flex items-center gap-2 self-start text-sm font-black text-indigo-600 transition hover:text-indigo-500 md:self-auto"
			>
				Learn more about EdPlan Nexus
				<FaArrowUpRightFromSquare className="text-xs" />
			</button>
		</div>
	</div>
);
