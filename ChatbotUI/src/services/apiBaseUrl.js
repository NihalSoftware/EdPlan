const normalizeBaseUrl = (value) => {
	if (!value) return "";
	let base = String(value).trim();
	base = base.replace(/\/+$/, "");

	return base;
};

export const getApiBaseUrl = () => {
	const fromEnv = import.meta.env?.VITE_API_BASE_URL;
	const origin =
		typeof window !== "undefined" ? window.location.origin : "http://localhost:5173";
	const fallback = import.meta.env?.DEV ? "/api" : `${origin}/api`;
	return normalizeBaseUrl(fromEnv || fallback);
};

export const API_BASE_URL = getApiBaseUrl();
