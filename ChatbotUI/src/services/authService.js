import client from "./apiClient.js";

export const login = ({ email, password }) =>
	client.post("/users/login", {
		email,
		password,
	});

export const register = ({
	firstName,
	lastName,
	email,
	phoneNumber,
	password,
}) =>
	client.post("/users", {
		first_name: firstName,
		last_name: lastName,
		email,
		phone_number: phoneNumber,
		password,
	});

export default client;
