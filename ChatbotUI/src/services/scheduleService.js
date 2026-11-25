import client from "./apiClient.js";
import { load } from "../utils/storage.js";

const unwrapData = (response) => response.data?.data || [];

const getStudentId = () => {
	const profile = load("UserProfile") || {};
	return profile.student_id || profile.studentId || profile.id || "1";
};

export const getGeneratedSchedules = async (planId) => {
	const response = await client.get(`/schedulepilot/plans/${planId}/schedules`, {
		params: { user_id: getStudentId() },
	});
	return unwrapData(response);
};

export const getGeneratedSchedule = async (planId, scheduleId) => {
	const response = await client.get(`/schedulepilot/schedules/${scheduleId}`, {
		params: { user_id: getStudentId(), plan_id: planId },
	});
	return response.data?.data || null;
};

export const activateGeneratedSchedule = async (planId, scheduleId) => {
	const response = await client.post(
		`/schedulepilot/schedules/${scheduleId}/activate`,
		{
			user_id: getStudentId(),
			plan_id: planId,
			confirmed: true,
		}
	);
	return response.data?.data || null;
};

export default {
	activateGeneratedSchedule,
	getGeneratedSchedules,
	getGeneratedSchedule,
};
