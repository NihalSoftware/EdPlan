import { useState } from "react";
import { Link } from "react-router-dom";
import {
	FaArrowLeft,
	FaArrowUpRightFromSquare,
	FaBell,
	FaBriefcase,
	FaBuildingColumns,
	FaBullseye,
	FaCheck,
	FaClipboardList,
	FaGraduationCap,
	FaLightbulb,
	FaMagnifyingGlass,
	FaPaperPlane,
	FaRobot,
	FaShieldHalved,
	FaWandMagicSparkles,
} from "react-icons/fa6";
import { FaDollarSign } from "react-icons/fa";

const mockMessages = [
	{
		id: "assistant-intro",
		role: "assistant",
		time: "10:30 AM",
		content:
			"Hello! I'm EdPlan Orchestrator, your AI education assistant.\nI can help you with everything from academic planning to university selection, financial guidance, and much more. What would you like to explore today?",
	},
	{
		id: "student-query",
		role: "user",
		time: "10:31 AM",
		content:
			"I want to study Data Science. Suggest some universities and help me plan my path.",
	},
];

const suggestedPrompts = [
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

const workflowSteps = [
	{
		title: "Understand Your Goals",
		description:
			"We analyze your query to understand your academic and career objectives.",
		icon: FaBullseye,
		accent: "from-violet-100 to-indigo-100 text-indigo-600",
	},
	{
		title: "Activate Specialized Agents",
		description: "Our orchestrator assigns the right agents to handle your request.",
		icon: FaRobot,
		accent: "from-emerald-100 to-cyan-100 text-emerald-600",
	},
	{
		title: "Gather & Analyze Information",
		description: "Agents collect and analyze data from trusted sources in real-time.",
		icon: FaMagnifyingGlass,
		accent: "from-blue-100 to-indigo-100 text-blue-600",
	},
	{
		title: "Generate Personalized Insights",
		description: "We create tailored recommendations and actionable plans for you.",
		icon: FaLightbulb,
		accent: "from-amber-100 to-orange-100 text-orange-500",
	},
	{
		title: "Deliver Actionable Results",
		description: "You get a clear, concise response with next steps and resources.",
		icon: FaCheck,
		accent: "from-violet-100 to-purple-100 text-violet-600",
	},
];

const futureIntegrationPoints = {
	orchestratorEndpoint: null,
	messageTransport: null,
	agentTelemetry: null,
};

const toneClasses = {
	violet: "bg-violet-50 text-violet-700 ring-violet-100",
	cyan: "bg-cyan-50 text-cyan-700 ring-cyan-100",
	amber: "bg-amber-50 text-amber-600 ring-amber-100",
	indigo: "bg-indigo-50 text-indigo-700 ring-indigo-100",
	purple: "bg-purple-50 text-purple-700 ring-purple-100",
};

const RobotAvatar = ({ size = "md", className = "" }) => {
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

const ChatBubble = ({ message }) => {
	const isUser = message.role === "user";

	return (
		<div className={`flex items-start gap-4 ${isUser ? "justify-end" : ""}`}>
			{!isUser && <RobotAvatar size="sm" className="mt-2 shrink-0" />}
			<div
				className={
					isUser
						? "max-w-[30rem] rounded-3xl border border-indigo-200 bg-gradient-to-br from-indigo-50 to-violet-50 px-6 py-5 text-indigo-950 shadow-sm"
						: "max-w-[36rem] rounded-3xl border border-slate-200 bg-white/95 px-6 py-5 text-slate-950 shadow-sm"
				}
			>
				<p className="whitespace-pre-line text-sm font-medium leading-7 md:text-base">
					{message.content}
				</p>
				<p className="mt-4 text-xs font-semibold text-slate-500">{message.time}</p>
			</div>
			{isUser && (
				<div className="mt-2 flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 font-black text-white shadow-lg shadow-indigo-200">
					V
				</div>
			)}
		</div>
	);
};

const TypingIndicator = () => (
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

const ConversationArea = ({ inputValue, onInputChange }) => (
	<div className="rounded-3xl border border-slate-200 bg-white/70 p-5 shadow-sm backdrop-blur-xl sm:p-6">
		<div className="min-h-[27rem] space-y-7">
			{mockMessages.map((message) => (
				<ChatBubble key={message.id} message={message} />
			))}
			<TypingIndicator />
		</div>
		<MessageInput value={inputValue} onChange={onInputChange} />
	</div>
);

const MessageInput = ({ value, onChange }) => (
	<div className="mt-8 flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-5 py-3 shadow-sm transition focus-within:border-indigo-300 focus-within:shadow-lg focus-within:shadow-indigo-100">
		<input
			type="text"
			value={value}
			onChange={(event) => onChange(event.target.value)}
			placeholder="Type your message here..."
			className="min-h-12 flex-1 bg-transparent text-sm font-semibold text-slate-800 outline-none placeholder:text-slate-400 md:text-base"
		/>
		<button
			type="button"
			aria-label="Send message"
			className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-xl shadow-indigo-200 transition hover:-translate-y-0.5 hover:shadow-indigo-300"
		>
			<FaPaperPlane />
		</button>
	</div>
);

const SuggestedPromptCard = ({ prompt, onSelect }) => {
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

const WorkflowStep = ({ step, isLast }) => {
	const Icon = step.icon;

	return (
		<div className="group relative flex gap-5">
			<div className="flex flex-col items-center">
				<div
					className={`z-10 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br ${step.accent} text-xl shadow-lg transition duration-300 group-hover:scale-105`}
				>
					<Icon />
				</div>
				{!isLast && <div className="h-12 w-px bg-indigo-100" />}
			</div>
			<div className="pb-5">
				<h3 className="text-base font-black text-slate-950">{step.title}</h3>
				<p className="mt-2 text-sm font-medium leading-6 text-slate-600">
					{step.description}
				</p>
			</div>
		</div>
	);
};

const WorkflowTimeline = () => (
	<aside className="space-y-5">
		<div className="rounded-3xl border border-slate-200 bg-white/75 p-7 shadow-sm backdrop-blur-xl">
			<h2 className="mb-7 text-xl font-black text-slate-950">
				How EdPlan Orchestrator Works
			</h2>
			<div>
				{workflowSteps.map((step, index) => (
					<WorkflowStep
						key={step.title}
						step={step}
						isLast={index === workflowSteps.length - 1}
					/>
				))}
			</div>
		</div>
		<div className="flex items-center gap-4 rounded-2xl border border-indigo-100 bg-indigo-50/70 p-5 text-sm font-semibold leading-6 text-slate-700 shadow-sm">
			<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white text-indigo-600">
				<FaShieldHalved />
			</div>
			<p>Powered by specialized agents working together to provide you the best guidance.</p>
		</div>
	</aside>
);

const SuggestedPrompts = ({ onSelect }) => (
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

const SecurityBanner = () => (
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
						EdPlan Nexus never stores your conversations. Everything is encrypted
						and handled with care.
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

const MasterAgentWorkspace = () => {
	const [inputValue, setInputValue] = useState("");

	const handlePromptSelect = (prompt) => {
		setInputValue(prompt);
	};

	void futureIntegrationPoints;

	return (
		<section className="min-h-screen bg-[radial-gradient(circle_at_78%_8%,rgba(99,102,241,0.14),transparent_28%),radial-gradient(circle_at_55%_22%,rgba(167,139,250,0.10),transparent_22%),linear-gradient(135deg,#f8fbff_0%,#ffffff_46%,#f7f5ff_100%)] text-slate-950">
			<WorkspaceTopBar />
			<div className="mx-auto max-w-[1560px] px-5 py-8 sm:px-8 lg:px-12">
				<WorkspaceHeader />
				<div className="mt-9 grid gap-7 xl:grid-cols-[minmax(0,1fr)_20rem] 2xl:grid-cols-[minmax(0,1fr)_22rem]">
					<div>
						<ConversationArea
							inputValue={inputValue}
							onInputChange={setInputValue}
						/>
						<SuggestedPrompts onSelect={handlePromptSelect} />
					</div>
					<WorkflowTimeline />
				</div>
				<SecurityBanner />
			</div>
		</section>
	);
};

export default MasterAgentWorkspace;
