export const MESSAGE_ROLES = {
	USER: "user",
	ASSISTANT: "assistant",
	SYSTEM: "system",
	TOOL: "tool",
};

export const MESSAGE_STATUS = {
	READY: "ready",
	LOADING: "loading",
	ERROR: "error",
};

export const createMessage = ({
	id,
	role,
	content,
	status = MESSAGE_STATUS.READY,
	createdAt = new Date(),
	workflow = [],
	metadata = {},
}) => ({
	id,
	role,
	content,
	status,
	createdAt,
	workflow,
	metadata,
	citations: metadata.citations || [],
	toolCalls: metadata.toolCalls || [],
});
