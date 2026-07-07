import client from "./apiClient.js";

const unwrapData = (response) => response.data?.data || [];

export const getCatalogUniversities = async () => {
	const response = await client.get("/universities", {
		params: { per_page: 100 },
	});
	return unwrapData(response);
};

export const getCatalogPrograms = async (universityId) => {
	const response = await client.get("/programs", {
		params: {
			university_id: universityId || undefined,
		},
	});
	return unwrapData(response);
};

export const getCatalogCourses = async (programId) => {
	const response = await client.get(`/programs/${programId}/courses`);
	return unwrapData(response);
};

export const getCareers = async () => {
	const response = await client.get("/careers");
	return unwrapData(response);
};

export default {
	getCatalogUniversities,
	getCatalogPrograms,
	getCatalogCourses,
	getCareers,
};

