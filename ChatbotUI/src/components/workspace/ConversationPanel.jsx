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

const AcademicPlanPreview = ({ plan }) => {
	if (!plan?.semesters?.length) return null;

	const warnings = plan.validation?.warnings || [];
	const recommendations = plan.recommendations || [];

	return (
		<div className="mt-4 space-y-3 rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
			<div className="flex flex-wrap items-center justify-between gap-3">
				<div>
					<p className="text-sm font-black text-slate-950">Academic Plan</p>
					<p className="mt-1 text-xs font-semibold text-slate-500">
						{plan.graduation_estimate || plan.summary?.graduation_estimate}
					</p>
				</div>
				<span className="rounded-full bg-white px-3 py-1 text-xs font-black text-indigo-700">
					{plan.remaining_credits ?? plan.summary?.remaining_credits ?? 0} credits left
				</span>
			</div>
			<div className="grid gap-2 sm:grid-cols-2">
				{plan.semesters.slice(0, 6).map((semester) => (
					<div
						key={semester.semester_number || semester.label}
						className="rounded-xl border border-white bg-white p-3 shadow-sm"
					>
						<div className="mb-2 flex items-center justify-between gap-2">
							<p className="text-xs font-black text-slate-900">{semester.label}</p>
							<p className="text-xs font-black text-slate-500">
								{semester.credits} cr
							</p>
						</div>
						<div className="flex flex-wrap gap-1.5">
							{(semester.courses || []).map((course) => (
								<span
									key={course.course_id || course.course_code}
									className="rounded-lg bg-indigo-50 px-2 py-1 text-[11px] font-black text-indigo-700"
								>
									{course.course_code}
								</span>
							))}
						</div>
					</div>
				))}
			</div>
			{warnings.length > 0 && (
				<div className="rounded-xl border border-amber-200 bg-amber-50 p-3">
					<p className="text-xs font-black uppercase text-amber-700">Warnings</p>
					<ul className="mt-2 space-y-1 text-xs font-semibold leading-5 text-amber-900">
						{warnings.slice(0, 3).map((warning, index) => (
							<li key={`${warning.code || "warning"}-${index}`}>
								{warning.message || warning}
							</li>
						))}
					</ul>
				</div>
			)}
			{recommendations.length > 0 && (
				<div className="rounded-xl border border-emerald-100 bg-emerald-50 p-3">
					<p className="text-xs font-black uppercase text-emerald-700">
						Recommendations
					</p>
					<ul className="mt-2 space-y-1 text-xs font-semibold leading-5 text-emerald-950">
						{recommendations.slice(0, 3).map((recommendation, index) => (
							<li key={`${recommendation}-${index}`}>{recommendation}</li>
						))}
					</ul>
				</div>
			)}
		</div>
	);
};

const SchedulePlanPreview = ({ plan }) => {
	if (!plan?.recommended_schedule) return null;

	const summary = plan.summary || {};
	const timetable = plan.weekly_timetable || [];
	const warnings = plan.warnings || [];
	const recommendations = plan.recommendations || [];

	return (
		<div className="mt-4 space-y-3 rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
			<div className="flex flex-wrap items-center justify-between gap-3">
				<div>
					<p className="text-sm font-black text-slate-950">Recommended Schedule</p>
					<p className="mt-1 text-xs font-semibold text-slate-500">
						{summary.term_name || "Selected term"}
					</p>
				</div>
				<span className="rounded-full bg-white px-3 py-1 text-xs font-black text-indigo-700">
					{summary.recommended_credits || 0} credits
				</span>
			</div>
			<div className="grid gap-2">
				{timetable.slice(0, 8).map((meeting, index) => (
					<div
						key={`${meeting.section_id || "section"}-${index}`}
						className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-white bg-white p-3 text-xs shadow-sm"
					>
						<div>
							<p className="font-black text-slate-900">
								{meeting.day || "Async"} {meeting.start_time || ""}
								{meeting.end_time ? `-${meeting.end_time}` : ""}
							</p>
							<p className="mt-1 font-semibold text-slate-500">
								Section {meeting.section_number || meeting.section_id}
							</p>
						</div>
						<p className="font-bold text-slate-500">
							{meeting.instructor || meeting.room || meeting.meeting_type}
						</p>
					</div>
				))}
			</div>
			{warnings.length > 0 && (
				<div className="rounded-xl border border-amber-200 bg-amber-50 p-3">
					<p className="text-xs font-black uppercase text-amber-700">Warnings</p>
					<ul className="mt-2 space-y-1 text-xs font-semibold leading-5 text-amber-900">
						{warnings.slice(0, 3).map((warning, index) => (
							<li key={`${warning}-${index}`}>{warning}</li>
						))}
					</ul>
				</div>
			)}
			{recommendations.length > 0 && (
				<div className="rounded-xl border border-emerald-100 bg-emerald-50 p-3">
					<p className="text-xs font-black uppercase text-emerald-700">
						Recommendations
					</p>
					<ul className="mt-2 space-y-1 text-xs font-semibold leading-5 text-emerald-950">
						{recommendations.slice(0, 3).map((recommendation, index) => (
							<li key={`${recommendation}-${index}`}>{recommendation}</li>
						))}
					</ul>
				</div>
			)}
		</div>
	);
};

const ComparisonPlanPreview = ({ plan }) => {
	if (!plan?.comparison_table?.length) return null;

	const summary = plan.summary || {};
	const table = plan.comparison_table || [];
	const ranked = plan.ranked_recommendations || [];
	const warnings = plan.warnings || [];
	const recommendations = plan.recommendations || [];
	const recommended =
		summary.recommended_university ||
		plan.recommended_university?.university_name ||
		"No recommendation yet";

	return (
		<div className="mt-4 space-y-3 rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
			<div className="flex flex-wrap items-center justify-between gap-3">
				<div>
					<p className="text-sm font-black text-slate-950">University Comparison</p>
					<p className="mt-1 text-xs font-semibold text-slate-500">
						{summary.program_focus || "General comparison"}
					</p>
				</div>
				<span className="rounded-full bg-white px-3 py-1 text-xs font-black text-indigo-700">
					{recommended}
				</span>
			</div>
			<div className="grid gap-2">
				{table.slice(0, 4).map((row) => (
					<div
						key={row.university_id}
						className="rounded-xl border border-white bg-white p-3 text-xs shadow-sm"
					>
						<div className="flex flex-wrap items-start justify-between gap-2">
							<div>
								<p className="font-black text-slate-900">
									{row.university_name}
								</p>
								<p className="mt-1 font-semibold text-slate-500">
									{[row.city, row.state].filter(Boolean).join(", ") ||
										"Location unavailable"}
								</p>
							</div>
							<p className="font-black text-indigo-700">
								{row.lowest_matching_credits
									? `${row.lowest_matching_credits} cr`
									: "Credits unavailable"}
							</p>
						</div>
						<div className="mt-2 flex flex-wrap gap-1.5">
							{(row.matching_programs || []).slice(0, 3).map((program) => (
								<span
									key={program.program_id}
									className="rounded-lg bg-indigo-50 px-2 py-1 text-[11px] font-black text-indigo-700"
								>
									{program.program_name}
								</span>
							))}
						</div>
					</div>
				))}
			</div>
			{ranked.length > 0 && (
				<div className="rounded-xl border border-white bg-white p-3">
					<p className="text-xs font-black uppercase text-slate-500">Ranking</p>
					<div className="mt-2 space-y-1.5">
						{ranked.slice(0, 3).map((item) => (
							<div
								key={item.university_id}
								className="flex items-center justify-between gap-3 text-xs font-semibold text-slate-600"
							>
								<span>
									#{item.rank} {item.university_name}
								</span>
								<span className="font-black text-slate-900">{item.score}</span>
							</div>
						))}
					</div>
				</div>
			)}
			{warnings.length > 0 && (
				<div className="rounded-xl border border-amber-200 bg-amber-50 p-3">
					<p className="text-xs font-black uppercase text-amber-700">Warnings</p>
					<ul className="mt-2 space-y-1 text-xs font-semibold leading-5 text-amber-900">
						{warnings.slice(0, 3).map((warning, index) => (
							<li key={`${warning}-${index}`}>{warning}</li>
						))}
					</ul>
				</div>
			)}
			{recommendations.length > 0 && (
				<div className="rounded-xl border border-emerald-100 bg-emerald-50 p-3">
					<p className="text-xs font-black uppercase text-emerald-700">
						Recommendations
					</p>
					<ul className="mt-2 space-y-1 text-xs font-semibold leading-5 text-emerald-950">
						{recommendations.slice(0, 3).map((recommendation, index) => (
							<li key={`${recommendation}-${index}`}>{recommendation}</li>
						))}
					</ul>
				</div>
			)}
		</div>
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
					{!isUser && <AcademicPlanPreview plan={message.metadata?.academicPlan} />}
					{!isUser && <SchedulePlanPreview plan={message.metadata?.schedulePlan} />}
					{!isUser && <ComparisonPlanPreview plan={message.metadata?.comparisonPlan} />}
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
