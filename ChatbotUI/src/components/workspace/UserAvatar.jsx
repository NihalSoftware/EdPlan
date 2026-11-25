import { useMemo } from "react";
import { FaUser } from "react-icons/fa6";
import { load } from "../../utils/storage.js";

const firstString = (...values) =>
	values.find((value) => typeof value === "string" && value.trim())?.trim() || "";

const getUserIdentity = () => {
	const isAuthenticated = Boolean(load("AuthToken"));
	if (!isAuthenticated) {
		return {
			isAuthenticated: false,
			displayName: "",
			initial: "",
			imageUrl: "",
		};
	}

	const profile = load("UserProfile") || {};
	const firstName = firstString(profile.first_name, profile.firstName);
	const lastName = firstString(profile.last_name, profile.lastName);
	const displayName = firstString(
		profile.name,
		profile.full_name,
		profile.fullName,
		[firstName, lastName].filter(Boolean).join(" ")
	);
	const imageUrl = firstString(
		profile.profile_picture,
		profile.profilePicture,
		profile.avatar_url,
		profile.avatarUrl,
		profile.photo_url,
		profile.photoUrl,
		profile.picture,
		profile.image_url,
		profile.imageUrl
	);

	return {
		isAuthenticated: true,
		displayName,
		initial: displayName.charAt(0).toUpperCase(),
		imageUrl,
	};
};

const UserAvatar = () => {
	const user = useMemo(getUserIdentity, []);
	const label = user.displayName ? `${user.displayName} avatar` : "User avatar";

	if (user.imageUrl) {
		return (
			<img
				src={user.imageUrl}
				alt={label}
				className="mt-1 h-9 w-9 shrink-0 rounded-full object-cover shadow-lg shadow-indigo-100 ring-2 ring-white"
			/>
		);
	}

	if (user.initial) {
		return (
			<div
				aria-label={label}
				className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-sm font-black text-white shadow-lg shadow-indigo-200"
			>
				{user.initial}
			</div>
		);
	}

	return (
		<div
			aria-label={label}
			className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100 text-sm text-slate-500 shadow-sm ring-1 ring-slate-200"
		>
			<FaUser />
		</div>
	);
};

export default UserAvatar;
