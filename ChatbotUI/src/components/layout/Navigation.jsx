import { NavLink, useLocation, useNavigate } from "react-router-dom";
import clsx from "clsx";
import { clearUserData, load } from "../../utils/storage.js";
import {
	FaBookOpen,
	FaBuildingColumns,
	FaClipboardList,
	FaHouse,
	FaRegBookmark,
	FaRegCompass,
	FaRightFromBracket,
	FaWandMagicSparkles,
} from "react-icons/fa6";
import "./navigation.css";

const NavItem = ({ to, label, icon: Icon, badge, onClick }) => (
	<NavLink
		to={to}
		onClick={onClick}
		className={({ isActive }) =>
			clsx(
				"site-navigation-link group flex min-w-0 w-full items-center rounded-xl text-left font-semibold transition",
				isActive
					? "bg-indigo-50 text-indigo-600 shadow-sm ring-1 ring-indigo-100"
					: "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
			)
		}
	>
		{Icon && <Icon className="h-5 w-5 shrink-0" />}
		<span className="site-navigation-label min-w-0 flex-1">{label}</span>
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
			clearUserData();
			navigate("/login", { replace: true });
			return;
		}
		navigate(location.pathname === "/login" ? "/signup" : "/login");
	};

	return (
		<aside
			className={clsx(
				"site-navigation fixed inset-y-0 left-0 w-72 max-w-full flex-col border-r border-slate-200 bg-white shadow-sm",
				open ? "z-50 flex" : "hidden",
				"lg:flex"
			)}
		>
			<header className="site-navigation-header flex items-center border-b border-slate-100">
				<div className="flex w-full min-w-0 items-center gap-3">
					<button
						type="button"
						onClick={closeMenu}
						className="shrink-0 rounded-md px-3 py-1 hover:bg-slate-100 lg:hidden"
						aria-label="Close menu"
					>
						<span className="text-xl text-slate-700">x</span>
					</button>

					<img
						src="/assets/edplan-ai-logo.jpg"
						alt="EdPlan AI — Choose. Compare. Plan."
						width="1599"
						height="1066"
						className="site-navigation-logo block w-full min-w-0 h-auto aspect-[2.5] object-cover object-[center_53%]"
					/>
				</div>
			</header>

			<nav className="site-navigation-links grid" aria-label="Main navigation">
				<NavItem to="/home" label="Home" icon={FaHouse} onClick={closeMenu} />
				<NavItem to="/career" label="Career & Program" icon={FaRegCompass} onClick={closeMenu} />
				<NavItem to="/intake" label="Onboarding Form" icon={FaClipboardList} onClick={closeMenu} />
				<NavItem to="/uni" label="Find University" icon={FaBuildingColumns} onClick={closeMenu} />
				<NavItem to="/educationplan" label="Create Education Plan" icon={FaBookOpen} onClick={closeMenu} />
				{/* <NavItem to="/schedule-generator" label="Schedule Generator" icon={FaCalendarAlt} onClick={closeMenu} /> */}
				<NavItem to="/view" label="Saved Plans" icon={FaRegBookmark} onClick={closeMenu} />
				<NavItem to="/financial-aid" label="Financial Aid" icon={FaBookOpen} onClick={closeMenu} />
				<NavItem to="/what-if-analysis" label="What If Analysis" icon={FaWandMagicSparkles} onClick={closeMenu} />
				<NavItem to="/mesa" label="MESA AI" icon={FaWandMagicSparkles} onClick={closeMenu} />
			</nav>
			<footer className="site-navigation-footer border-t border-slate-50">
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
