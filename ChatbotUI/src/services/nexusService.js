import apiClient from "./apiClient.js";

export const sendMessage = async ({
	message,
	conversationId,
	studentId,
	context = {},
}) => {
	const response = await apiClient.post("/nexus/chat", {
		message,
		conversation_id: conversationId,
		student_id: studentId,
		context,
	});

	return response.data;
};
