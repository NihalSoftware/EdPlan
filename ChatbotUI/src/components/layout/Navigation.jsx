import { NavLink, useLocation, useNavigate } from "react-router-dom";
import clsx from "clsx";
import { load, remove } from "../../utils/storage.js";
import {
	FaArrowRight,
	FaBookOpen,
	FaBuildingColumns,
	FaClipboardList,
	FaGraduationCap,
	FaHouse,
	FaRegBookmark,
	FaRegCompass,
	FaRightFromBracket,
	FaWandMagicSparkles,
} from "react-icons/fa6";
import { FaCalendarAlt } from "react-icons/fa";

const NavItem = ({ to, label, icon: Icon, badge, onClick }) => (
	<NavLink
		to={to}
		onClick={onClick}
		className={({ isActive }) =>
			clsx(
				"group flex w-full items-center gap-4 rounded-xl px-4 py-3 text-left font-semibold transition",
				isActive
					? "bg-indigo-50 text-indigo-600 shadow-sm ring-1 ring-indigo-100"
					: "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
			)
		}
	>
		{Icon && <Icon className="h-5 w-5 shrink-0" />}
		<span className="min-w-0 flex-1 truncate">{label}</span>
		{badge && (
			<span className="rounded-md bg-gradient-to-r from-indigo-500 to-violet-600 px-2 py-0.5 text-[10px] font-black uppercase tracking-wide text-white shadow-sm">
				{badge}
			</span>
		)}
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

	const closeMenu = () => setOpen && setOpen(false);

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
				"flex flex-col border-r border-slate-200 bg-white shadow-sm",
				open ? "fixed inset-y-0 left-0 z-50 h-full w-72 overflow-y-auto" : "hidden",
				"lg:fixed lg:left-0 lg:top-0 lg:block lg:h-screen lg:w-72 lg:overflow-y-auto"
			)}
		>
			<header className="flex items-center justify-between gap-4 border-b border-slate-100 p-6">
				<div className="flex items-center gap-3">
					<button
						type="button"
						onClick={closeMenu}
						className="rounded-md p-2 hover:bg-slate-100 lg:hidden"
						aria-label="Close menu"
					>
						<span className="text-xl text-slate-700">x</span>
					</button>

					<div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-200">
						<FaGraduationCap className="h-5 w-5" />
					</div>
					<h1 className="text-3xl font-bold text-slate-950">EdPlan.ai</h1>
				</div>
			</header>

			<nav className="flex flex-col gap-2 px-5 py-7">
				<NavItem to="/home" label="Home" icon={FaHouse} onClick={closeMenu} />
				<NavItem to="/career" label="Career & Program" icon={FaRegCompass} onClick={closeMenu} />
				<NavItem to="/intake" label="Onboarding Form" icon={FaClipboardList} onClick={closeMenu} />
				<NavItem to="/uni" label="Find University" icon={FaBuildingColumns} onClick={closeMenu} />
				<NavItem to="/educationplan" label="Create Education Plan" icon={FaBookOpen} onClick={closeMenu} />
				<NavItem to="/schedule-generator" label="Schedule Generator" icon={FaCalendarAlt} onClick={closeMenu} />
				<NavItem to="/view" label="Saved Plans" icon={FaRegBookmark} onClick={closeMenu} />
				<NavItem to="/edplan-nexus" label="EdPlan Nexus" icon={FaWandMagicSparkles} badge="NEW" onClick={closeMenu} />
			</nav>

			<div className="mx-5 mt-auto rounded-2xl border border-indigo-100 bg-gradient-to-br from-violet-50 via-white to-indigo-50 p-5 shadow-sm">
				<div className="mx-auto mb-4 flex h-20 w-24 items-end justify-center">
					<div className="relative h-14 w-20 rounded-xl bg-gradient-to-br from-indigo-100 to-violet-200 shadow-xl shadow-indigo-100">
						<div className="absolute -top-5 left-4 h-7 w-12 rounded-sm bg-indigo-500 shadow-md shadow-indigo-200 [clip-path:polygon(50%_0,100%_35%,50%_70%,0_35%)]" />
						<div className="absolute left-5 top-3 h-2 w-10 rounded-full bg-white/70" />
						<div className="absolute left-4 top-7 h-2 w-12 rounded-full bg-white/60" />
						<div className="absolute -right-4 bottom-0 h-8 w-3 rounded-full bg-emerald-200" />
						<div className="absolute -right-2 bottom-0 h-12 w-3 rounded-full bg-emerald-300" />
					</div>
				</div>
				<h2 className="text-center text-base font-black leading-6 text-slate-950">
					Your AI-powered education companion
				</h2>
				<p className="mt-3 text-center text-sm font-medium leading-6 text-slate-600">
					Get personalized guidance from our network of specialized agents.
				</p>
				<NavLink
					to="/edplan-nexus"
					onClick={closeMenu}
					className="mt-5 flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-bold text-indigo-600 shadow-sm transition hover:border-indigo-200 hover:shadow-md"
				>
					Start Your Journey
					<FaArrowRight />
				</NavLink>
			</div>

			<footer className="border-t border-slate-50 p-6">
				<div className="flex items-center justify-between gap-3">
					{isAuthenticated && firstName && (
						<span className="text-md font-medium text-slate-600">{firstName}</span>
					)}
					<button
						type="button"
						onClick={handleAuthClick}
						className="inline-flex items-center gap-3 text-lg font-medium text-slate-600 hover:text-indigo-600"
					>
						<FaRightFromBracket />
						{buttonLabel}
					</button>
				</div>
			</footer>
		</aside>
	);
};

export default Navigation;
