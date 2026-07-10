import { NavLink, useLocation, useNavigate } from "react-router-dom";
import clsx from "clsx";
import { load, remove } from "../../utils/storage.js";

const NavItem = ({ to, label, onClick }) => (
	<NavLink
		to={to}
		onClick={onClick}
		className={({ isActive }) =>
			clsx(
				"w-full px-4 py-3 font-semibold text-left rounded-md transition",
				isActive
					? "bg-[#016ce6] text-white shadow-lg"
					: "text-slate-600 bg-slate-100 hover:bg-slate-200"
			)
		}
	>
		{label}
	</NavLink>
);

const Navigation = ({ open, setOpen }) => {
	const location = useLocation();
	const navigate = useNavigate();
	const isAuthenticated = Boolean(load("AuthToken"));
	const profile = load("UserProfile");
	const firstName =
		typeof profile?.first_name === "string"
			? profile.first_name
			: typeof profile?.firstName === "string"
			? profile.firstName
			: "";

	const buttonLabel = isAuthenticated
		? "Logout"
		: location.pathname === "/login"
		? "Sign up"
		: "Login";

	const handleAuthClick = () => {
		if (isAuthenticated) {
			remove("AuthToken");
			remove("UserEmail");
			remove("UserProfile");
			navigate("/login");
			return;
		}
		navigate(location.pathname === "/login" ? "/signup" : "/login");
	};

	return (
		<aside
			className={clsx(
				"bg-white border-r border-slate-200 shadow-sm flex flex-col",
				// Mobile: show as left-side drawer when open, otherwise hidden. Large screens: always show.
				open ? "fixed inset-y-0 left-0 z-50 w-72 h-full overflow-y-auto" : "hidden",
				"lg:block lg:w-72 lg:fixed lg:h-screen lg:top-0 lg:left-0 lg:overflow-y-auto"
			)}
		>
			<header className="p-6 flex items-center justify-between gap-4">
				<div className="flex items-center gap-3">
					<button
						type="button"
						onClick={() => setOpen && setOpen(false)}
						className="lg:hidden p-2 rounded-md hover:bg-slate-100"
						aria-label="Close menu"
					>
						<span className="text-xl text-slate-700">✕</span>
					</button>

					<h1 className="text-3xl font-semibold text-slate-900">EdPlan.ai</h1>
				</div>
			</header>

			<nav className="flex flex-col gap-2 px-6">
				<NavItem to="/home" label="Home" onClick={() => setOpen && setOpen(false)} />
				<NavItem to="/career" label="Career & Program" onClick={() => setOpen && setOpen(false)} />
				<NavItem to="/intake" label="Onboarding Form" onClick={() => setOpen && setOpen(false)} />
				<NavItem to="/uni" label="Find University" onClick={() => setOpen && setOpen(false)} />
				<NavItem to="/educationplan" label="Create Education Plan" onClick={() => setOpen && setOpen(false)} />
				{/* <NavItem to="/schedule-generator" label="Schedule Generator" onClick={() => setOpen && setOpen(false)} /> */}
				<NavItem to="/view" label="Saved Plans" onClick={() => setOpen && setOpen(false)} />
			</nav>

			<footer className="mt-auto border-t border-slate-50 p-10">
				<div className="flex items-center justify-between gap-3">
					{isAuthenticated && firstName && (
						<span className="text-md font-medium text-slate-600">{firstName}</span>
					)}
					<button
						type="button"
						onClick={handleAuthClick}
						className="font-medium text-lg text-indigo-600 hover:text-indigo-500"
					>
						{buttonLabel}
					</button>
				</div>
			</footer>
		</aside>
	);
};

export default Navigation;
