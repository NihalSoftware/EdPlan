import client from "./apiClient.js";

export const searchUniversities = async ({
	search,
	state,
	page = 0,
	perPage = 20,
} = {}) => {
	const response = await client.get("/universities", {
		params: {
			search: search || undefined,
			state: state || undefined,
			page,
			per_page: perPage,
		},
	});
	return response.data;
};

export const getUniversityById = async (unitId) => {
	const response = await client.get(`/universities/${unitId}`);
	return response.data?.data || null;
};

export default {
	searchUniversities,
	getUniversityById,
};
