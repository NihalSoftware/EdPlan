import axios from "axios";
import { API_BASE_URL } from "./apiBaseUrl.js";

const client = axios.create({
	baseURL: API_BASE_URL,
});

const unwrapData = (response) => response.data?.data || [];

export const getCatalogUniversities = async () => {
	const response = await client.get("/catalog/universities");
	return unwrapData(response);
};

export const getCatalogPrograms = async (universityId) => {
	const response = await client.get(
		`/catalog/universities/${universityId}/programs`
	);
	return unwrapData(response);
};

export const getCatalogCourses = async (programId) => {
	const response = await client.get(`/catalog/programs/${programId}/courses`);
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
