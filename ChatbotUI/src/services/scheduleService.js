import client from "./authService.js";

const unwrapData = (response) => response.data?.data || [];

export const getGeneratedSchedules = async (planId) => {
	const response = await client.get(`/plans/${planId}/generated-schedules`);
	return unwrapData(response);
};

export const getGeneratedSchedule = async (planId, scheduleId) => {
	const response = await client.get(
		`/plans/${planId}/generated-schedules/${scheduleId}`
	);
	return response.data?.data || null;
};

export const activateGeneratedSchedule = async (planId, scheduleId) => {
	const response = await client.post(
		`/plans/${planId}/generated-schedules/${scheduleId}/activate`
	);
	return response.data?.data || null;
};

export default {
	activateGeneratedSchedule,
	getGeneratedSchedules,
	getGeneratedSchedule,
};
