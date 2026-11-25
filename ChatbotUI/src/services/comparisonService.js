import apiClient from "./apiClient.js";

const unwrapData = (response) => response.data?.data || {};

export const searchUniversitiesForComparison = async ({
	state,
	city,
	name,
	limit = 10,
} = {}) => {
	const response = await apiClient.post("/comparison/universities/search", {
		state: state || undefined,
		city: city || undefined,
		name: name || undefined,
		limit,
	});
	return unwrapData(response);
};

export const compareUniversities = async (universityIds) => {
	const response = await apiClient.post("/comparison/universities/compare", {
		university_ids: universityIds,
	});
	return unwrapData(response);
};

export const searchProgramsForComparison = async ({
	universityId,
	degree,
	name,
	limit = 20,
} = {}) => {
	const response = await apiClient.post("/comparison/programs/search", {
		university_id: universityId || undefined,
		degree: degree || undefined,
		name: name || undefined,
		limit,
	});
	return unwrapData(response);
};

export const comparePrograms = async (programIds) => {
	const response = await apiClient.post("/comparison/programs/compare", {
		program_ids: programIds,
	});
	return unwrapData(response);
};

export const compareCareerPaths = async (programIds) => {
	const response = await apiClient.post("/comparison/careers/compare", {
		program_ids: programIds,
	});
	return unwrapData(response);
};

export default {
	searchUniversitiesForComparison,
	compareUniversities,
	searchProgramsForComparison,
	comparePrograms,
	compareCareerPaths,
};
