import axios from "axios";
import { load } from "../utils/storage.js";
import { API_BASE_URL } from "./apiBaseUrl.js";

const apiClient = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
});

apiClient.interceptors.request.use((config) => {
	const token = load("AuthToken");
	if (token) {
		config.headers = config.headers ?? {};
		if (!config.headers.Authorization) {
			config.headers.Authorization = `Bearer ${token}`;
		}
	}
	return config;
});

export default apiClient;
