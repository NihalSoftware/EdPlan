import apiClient from "./apiClient.js";

const unwrapData = (response) => response.data?.data;

export const listPlans = async ({ userId, isActive } = {}) => {
	const response = await apiClient.get("/plans", {
		params: {
			user_id: userId || undefined,
			is_active: isActive,
		},
	});
	return unwrapData(response) || [];
};

export const createPlan = async ({
	userId,
	universityId,
	programId,
	planName,
	description,
	isActive = true,
}) => {
	const response = await apiClient.post("/plans", {
		user_id: Number(userId),
		university_id: universityId,
		program_id: programId,
		plan_name: planName,
		description,
		is_active: isActive,
	});
	return unwrapData(response);
};

export const updatePlan = async (planId, payload) => {
	const response = await apiClient.patch(`/plans/${planId}`, payload);
	return unwrapData(response);
};

export const deletePlan = async (planId) => {
	const response = await apiClient.delete(`/plans/${planId}`);
	return unwrapData(response);
};

export const getPlan = async (planId) => {
	const response = await apiClient.get(`/plans/${planId}`);
	return unwrapData(response);
};

export const listPlanCourses = async (planId) => {
	const response = await apiClient.get(`/plans/${planId}/courses`);
	return unwrapData(response) || [];
};

export const addCourseToPlan = async (planId, { courseId, plannedTermId, status = "Planned", notes }) => {
	const response = await apiClient.post(`/plans/${planId}/courses`, {
		course_id: courseId,
		planned_term_id: plannedTermId || null,
		status,
		notes,
	});
	return unwrapData(response);
};

export const moveCourseInPlan = async (planId, courseId, { plannedTermId, status, notes }) => {
	const response = await apiClient.patch(`/plans/${planId}/courses/${courseId}`, {
		planned_term_id: plannedTermId || null,
		status,
		notes,
	});
	return unwrapData(response);
};

export const removeCourseFromPlan = async (planId, courseId) => {
	const response = await apiClient.delete(`/plans/${planId}/courses/${courseId}`);
	return response.data;
};

export const validatePlan = async (planId, payload = {}) => {
	const response = await apiClient.post(`/plans/${planId}/validate`, payload);
	return unwrapData(response);
};

export const validatePlanCourse = async (planId, payload) => {
	const response = await apiClient.post(`/plans/${planId}/validate-course`, payload);
	return unwrapData(response);
};

export const getGraduationAudit = async (planId) => {
	const response = await apiClient.get(`/plans/${planId}/audit`);
	return response.data;
};

export default {
	listPlans,
	createPlan,
	updatePlan,
	deletePlan,
	getPlan,
	listPlanCourses,
	addCourseToPlan,
	moveCourseInPlan,
	removeCourseFromPlan,
	validatePlan,
	validatePlanCourse,
	getGraduationAudit,
};
