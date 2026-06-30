import { useMemo, useRef, useState } from "react";
import { sendMessage } from "../services/nexusService.js";
import { load } from "../utils/storage.js";
import { generateId } from "../utils/id.js";
import {
	createMessage,
	MESSAGE_ROLES,
	MESSAGE_STATUS,
} from "../types/nexusChatTypes.js";

const defaultTelemetry = {
	activatedModules: [],
	executionTime: null,
	currentIntent: null,
	confidence: null,
	workflow: [],
	finalStatus: null,
};

const formatError = (error) =>
	error?.response?.data?.detail ||
	error?.response?.data?.message ||
	error?.message ||
	"EdPlan Orchestrator could not complete the request.";

const formatTime = (date) =>
	new Intl.DateTimeFormat("en", {
		hour: "numeric",
		minute: "2-digit",
	}).format(date);

const getStudentId = () => {
	const profile = load("UserProfile") || {};
	return profile.student_id || profile.studentId || profile.id || "1";
};

const getPlanId = () => {
	const saved =
		load("ActivePlanId") ||
		load("SelectedPlanId") ||
		load("CurrentPlanId");
	return saved || null;
};

export const useNexusChat = () => {
	const [conversationId, setConversationId] = useState(() => generateId());
	const [messages, setMessages] = useState([]);
	const [inputValue, setInputValue] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState(null);
	const [telemetry, setTelemetry] = useState(defaultTelemetry);
	const lastUserMessageRef = useRef("");

	const context = useMemo(() => {
		const planId = getPlanId();
		return planId ? { plan_id: planId } : {};
	}, []);

	const submitMessage = async (messageText = inputValue) => {
		const trimmed = messageText.trim();
		if (!trimmed || isLoading) return;

		const userMessage = createMessage({
			id: generateId(),
			role: MESSAGE_ROLES.USER,
			content: trimmed,
			createdAt: new Date(),
		});
		const loadingMessage = createMessage({
			id: generateId(),
			role: MESSAGE_ROLES.ASSISTANT,
			content: "",
			status: MESSAGE_STATUS.LOADING,
			createdAt: new Date(),
			workflow: [{ status: "Thinking..." }],
		});

		lastUserMessageRef.current = trimmed;
		setMessages((current) => [...current, userMessage, loadingMessage]);
		setInputValue("");
		setIsLoading(true);
		setError(null);
		setTelemetry((current) => ({
			...current,
			workflow: [{ status: "Thinking..." }],
		}));

		try {
			const result = await sendMessage({
				message: trimmed,
				conversationId,
				studentId: getStudentId(),
				context,
			});
			if (result.conversation_id && result.conversation_id !== conversationId) {
				setConversationId(result.conversation_id);
			}
			const assistantMessage = createMessage({
				id: generateId(),
				role: MESSAGE_ROLES.ASSISTANT,
				content: result.response || "",
				createdAt: new Date(),
				workflow: result.workflow || [],
				metadata: {
					activatedModules: result.activated_agents || result.activated_modules || [],
					executionTime: result.execution_time,
					currentIntent: result.intent || result.current_intent,
					confidence: result.confidence,
					finalStatus: result.status || result.final_status,
					warnings: result.warnings || [],
				},
			});
			setMessages((current) => [
				...current.filter((message) => message.id !== loadingMessage.id),
				assistantMessage,
			]);
			setTelemetry({
				activatedModules: result.activated_agents || result.activated_modules || [],
				executionTime: result.execution_time ?? null,
				currentIntent: result.intent || result.current_intent || null,
				confidence: result.confidence ?? null,
				workflow: result.workflow || [],
				finalStatus: result.status || result.final_status || null,
			});
		} catch (requestError) {
			const message = formatError(requestError);
			setError(message);
			setMessages((current) => [
				...current.filter((item) => item.id !== loadingMessage.id),
				createMessage({
					id: generateId(),
					role: MESSAGE_ROLES.ASSISTANT,
					content: message,
					status: MESSAGE_STATUS.ERROR,
					createdAt: new Date(),
					workflow: [{ status: "Error" }],
				}),
			]);
			setTelemetry((current) => ({
				...current,
				workflow: [{ status: "Error", detail: message }],
			}));
		} finally {
			setIsLoading(false);
		}
	};

	const retryLastMessage = () => {
		if (lastUserMessageRef.current) {
			submitMessage(lastUserMessageRef.current);
		}
	};

	return {
		conversationId,
		messages,
		inputValue,
		setInputValue,
		isLoading,
		error,
		telemetry,
		submitMessage,
		retryLastMessage,
		formatMessageTime: formatTime,
	};
};
