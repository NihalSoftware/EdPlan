import { Link } from "react-router-dom";
import { FaArrowLeft } from "react-icons/fa6";
import CareerNavigatorFeatures from "../components/careernavigator/CareerNavigatorFeatures.jsx";
import CareerNavigatorHero from "../components/careernavigator/CareerNavigatorHero.jsx";
import CareerPathDetails from "../components/careernavigator/CareerPathDetails.jsx";
import CareerReadiness from "../components/careernavigator/CareerReadiness.jsx";
import CareerRecommendations from "../components/careernavigator/CareerRecommendations.jsx";

const CareerNavigatorTopBar = () => (
	<header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 px-5 py-4 backdrop-blur-xl sm:px-8 lg:px-12">
		<div className="flex items-center justify-between gap-4">
			<Link
				to="/edplan-nexus"
				className="inline-flex items-center gap-3 text-sm font-black text-slate-800 transition hover:text-cyan-600"
			>
				<FaArrowLeft className="text-xs" />
				Back to <span className="text-cyan-600">EdPlan Nexus</span>
			</Link>
			<div className="h-10" />
		</div>
	</header>
);

const CareerNavigatorPage = () => (
	<section className="min-h-screen bg-[radial-gradient(circle_at_80%_8%,rgba(6,182,212,0.13),transparent_28%),linear-gradient(135deg,#f8fbff_0%,#ffffff_46%,#f2fdff_100%)] text-slate-950">
		<CareerNavigatorTopBar />
		<div className="mx-auto max-w-[1560px] space-y-8 px-5 py-8 sm:px-8 lg:px-12">
			<CareerNavigatorHero />
			<CareerNavigatorFeatures />
			<CareerRecommendations />
			<CareerPathDetails />
			<CareerReadiness />
		</div>
	</section>
);

export default CareerNavigatorPage;
