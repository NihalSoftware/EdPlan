import { Link } from "react-router-dom";
import { load } from "../utils/storage.js";
import { INSTITUTION } from "../config/institution.js";

const HomePage = () => {
	const profile = load("UserProfile");
	const firstName =
		typeof profile?.first_name === "string"
			? profile.first_name
			: typeof profile?.firstName === "string"
			? profile.firstName
			: "";

	return (
		<section className="w-full min-h-screen flex flex-col items-center justify-center py-12 px-6 bg-gradient-to-br from-sky-50 via-white to-amber-50">
			<div className="container mx-auto px-4 sm:px-6 lg:px-8">
				<div className="max-w-4xl mx-auto text-center space-y-8">
					<img
						src={INSTITUTION.logoUrl}
						alt="Northern New Mexico College"
						className="h-24 w-auto object-contain mx-auto"
					/>
					<h1 className="font-heading text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-foreground">
						Find Your Future <span className="text-[#0069e0]">@Northern</span>
					</h1>

					<h2 className="text-4xl font-bold text-slate-900">
						Small community. Great opportunity.
					</h2>

					<p className="text-lg text-slate-600">
						Explore Northern New Mexico College programs, connect them to career
						goals, and build a personalized path toward graduation.
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
						Explore NNMC Programs
					</Link>
				</div>

				<div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-600">
					<div className="bg-white rounded-lg shadow p-4">
						Build an NNMC degree plan tailored to your goals.
					</div>
					<div className="bg-white rounded-lg shadow p-4">
						Review official NNMC cost and financial-aid information.
					</div>
					<div className="bg-white rounded-lg shadow p-4">
						Connect programs with career paths and practical next steps.
					</div>
				</div>
			</div>
		</section>
	);
};

export default HomePage;
