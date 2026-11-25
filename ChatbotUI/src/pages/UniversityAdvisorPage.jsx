import { Link } from "react-router-dom";
import { FaArrowLeft } from "react-icons/fa6";
import UniversityAdvisorFeatures from "../components/universityadvisor/UniversityAdvisorFeatures.jsx";
import UniversityAdvisorHero from "../components/universityadvisor/UniversityAdvisorHero.jsx";
import UniversityComparison from "../components/universityadvisor/UniversityComparison.jsx";

const UniversityAdvisorTopBar = () => (
	<header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 px-5 py-4 backdrop-blur-xl sm:px-8 lg:px-12">
		<div className="flex items-center justify-between gap-4">
			<Link
				to="/edplan-nexus"
				className="inline-flex items-center gap-3 text-sm font-black text-slate-800 transition hover:text-emerald-600"
			>
				<FaArrowLeft className="text-xs" />
				Back to <span className="text-emerald-600">EdPlan Nexus</span>
			</Link>
			<div className="h-10" />
		</div>
	</header>
);

const UniversityAdvisorPage = () => (
	<section className="min-h-screen bg-[radial-gradient(circle_at_80%_8%,rgba(16,185,129,0.13),transparent_28%),linear-gradient(135deg,#f8fbff_0%,#ffffff_46%,#f5fff9_100%)] text-slate-950">
		<UniversityAdvisorTopBar />
		<div className="mx-auto max-w-[1560px] space-y-8 px-5 py-8 sm:px-8 lg:px-12">
			<UniversityAdvisorHero />
			<UniversityAdvisorFeatures />
			<UniversityComparison />
		</div>
	</section>
);

export default UniversityAdvisorPage;
