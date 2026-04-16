import { Link, useNavigate} from "react-router-dom";
import { load } from "../utils/storage.js";


const HomePage = () => {
	const profile = load("UserProfile");
	const firstName =
		typeof profile?.first_name === "string"
			? profile.first_name
			: typeof profile?.firstName === "string"
			? profile.firstName
			: "";
	const navigate = useNavigate();
	return (
		<section className="w-full h-full flex flex-col items-center justify-center py-12 px-6 bg-gradient-to-br from-indigo-50 via-white to-purple-50">
			<div className="container mx-auto px-4 sm:px-6 lg:px-8">
				<div className="max-w-4xl mx-auto text-center space-y-8">
					{/* Main Heading */}
					<img
						src="/assets/logo.jpeg"
						alt="EdPlan.ai"
						className="w-28 h-28 object-contain mx-auto rounded-full shadow-md"
					/>
					<h1 className="font-heading text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-foreground">
						Find Your Perfect <span className="text-[#0069e0]">College</span>
					</h1>

					<h2 className="text-4xl font-bold text-slate-900">
						Plan your educational path.
					</h2>

					<p className="text-lg text-slate-600">
						Discover and compare colleges, explore programs, and create
						personalized education plans. Make informed decisions about your
						future with comprehensive data and expert guidance.
					</p>
<p  className="text-slate-600">
    If you have already chosen your college,{" "}
    <span
      onClick={() => navigate("/uni")}
        className="underline cursor-pointer hover:text-[#0069e0] transition text-slate-600"
    >
        click me
    </span>
</p>
				</div>
			</div>

			<div className="max-w-3xl text-center space-y-6">
				<div className="flex flex-wrap items-center justify-center gap-4 mt-5">
					{firstName ? (
						<div className="px-6 py-3 rounded-lg border border-slate-300 text-slate-700 font-semibold">
							Hi {firstName}
						</div>
					) : (
						<Link
							to="/login"
							className="px-6 py-3 rounded-lg border border-slate-300 text-slate-700 font-semibold hover:border-slate-500"
						>
							Login
						</Link>
					)}
					<Link
						to="/career"
						className="px-6 py-3 rounded-lg bg-[#0069e0] hover:bg-[#1977e3] text-white font-semibold shadow"
					>
						Start Now
					</Link>
				</div>

				<div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-600">
					<div className="bg-white rounded-lg shadow p-4">
						Help me find the best education plan tailored to my goals.
					</div>
					<div className="bg-white rounded-lg shadow p-4">
						Estimate the total tuition and living expenses by university.
					</div>
					<div className="bg-white rounded-lg shadow p-4">
						Learn how to apply for scholarships and financial aid.
					</div>
				</div>
			</div>
		</section>
	);
};

export default HomePage;
