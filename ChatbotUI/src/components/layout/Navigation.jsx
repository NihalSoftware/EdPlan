import { useState, useEffect } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { FiLogOut } from "react-icons/fi";
import clsx from "clsx";
import { load, remove } from "../../utils/storage.js";

// Added onClick prop so the menu closes when a link is clicked on mobile
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

const Navigation = () => {
    const location = useLocation();
    const navigate = useNavigate();
    
    // State to handle mobile menu toggle
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    // ✅ NEW STATE for logout popup
    const [showLogoutModal, setShowLogoutModal] = useState(false);

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
            setShowLogoutModal(true); // ✅ show popup instead of direct logout
            return;
        }
        navigate(location.pathname === "/login" ? "/signup" : "/login");
        setIsMenuOpen(false);
    };

    const closeMenu = () => setIsMenuOpen(false);

    // Prevent body scrolling when the mobile menu is open
    useEffect(() => {
        if (isMenuOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "auto";
        }
    }, [isMenuOpen]);

    return (
        <>
            {/* Mobile & Tablet Header */}
            <div className="lg:hidden flex items-center justify-between p-4 bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm">
                <h1 className="text-2xl font-semibold text-slate-900">EdPlan.ai</h1>
                <button
                    onClick={() => setIsMenuOpen(true)}
                    className="p-2 text-slate-600 hover:bg-slate-100 rounded-md focus:outline-none"
                    aria-label="Open menu"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v.01M12 12v.01M12 18v.01" />
                    </svg>
                </button>
            </div>

            {/* Overlay */}
            {isMenuOpen && (
                <div
                    className="fixed inset-0 bg-slate-900/50 z-40 lg:hidden transition-opacity"
                    onClick={closeMenu}
                />
            )}

            {/* Sidebar */}
            <aside
                className={clsx(
                    "fixed top-0 left-0 z-50 h-screen w-72 bg-white border-r border-slate-200 shadow-sm p-6 flex flex-col gap-6 overflow-y-auto transition-transform duration-300 ease-in-out lg:translate-x-0",
                    isMenuOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                <header className="flex flex-col gap-4">
                    <div className="flex items-center justify-between lg:block">
                        <h1 className="text-3xl font-semibold text-slate-900">
                            EdPlan.ai
                        </h1>
                        <button
                            onClick={closeMenu}
                            className="lg:hidden p-2 text-slate-500 hover:bg-slate-100 rounded-md"
                            aria-label="Close menu"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <div className="flex items-center justify-between border-b border-slate-100 pb-4 lg:border-none lg:pb-0">
                        {isAuthenticated && firstName ? (
                            <span className="text-md font-medium text-slate-600 truncate mr-2">
                                {firstName}
                            </span>
                        ) : (
                            <span />
                        )}
                        {!isAuthenticated && (
                            <button
                                type="button"
                                onClick={handleAuthClick}
                                className="font-medium text-lg text-indigo-600 hover:text-indigo-500 whitespace-nowrap"
                            >
                                {buttonLabel}
                            </button>
                        )}
                    </div>
                </header>

                <div className="flex-1 flex flex-col overflow-y-auto">
                    <nav className="flex flex-col gap-2 mt-2">
                    <NavItem to="/home" label="Home" onClick={closeMenu} />
                    <NavItem to="/career" label="Career & Program" onClick={closeMenu} />
                    <NavItem to="/intake" label="Onboarding Form" onClick={closeMenu} />
                    <NavItem to="/uni" label="Find University" onClick={closeMenu} />
                    <NavItem to="/educationplan" label="Create Education Plan" onClick={closeMenu} />
                    <NavItem to="/view" label="Saved Plans" onClick={closeMenu} />
                </nav>
                </div>

                {isAuthenticated && (
                    <div className="mt-auto pt-4">
                        <button
                            type="button"
                            onClick={handleAuthClick}
                            className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-transparent border border-[#ef4444] text-[#ef4444] font-medium rounded-lg transition hover:bg-[#fde8e8]"
                        >
                            <FiLogOut className="w-5 h-5" />
                            Sign Out
                        </button>
                    </div>
                )}
            </aside>

            {/* ✅ LOGOUT MODAL */}
            {showLogoutModal && (
                <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-[100]">
                    <div className="bg-white rounded-xl shadow-lg p-6 w-[320px]">
                        <h2 className="text-lg font-semibold text-slate-800 mb-3">
                            Confirm Logout
                        </h2>
                        <p className="text-sm text-slate-500 mb-5">
                            Are you sure you want to logout?
                        </p>

                        <div className="flex justify-end gap-3">
                            <button
                                onClick={() => setShowLogoutModal(false)}
                                className="px-4 py-2 text-sm bg-slate-100 rounded-md"
                            >
                                Cancel
                            </button>

                            <button
                                onClick={() => {
                                    remove("AuthToken");
                                    remove("UserEmail");
                                    remove("UserProfile");
                                    setShowLogoutModal(false);
                                    navigate("/login");
                                    setIsMenuOpen(false);
                                }}
                                className="px-4 py-2 text-sm bg-[#ef4444] text-white rounded-md hover:bg-[#dc2626]"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default Navigation;