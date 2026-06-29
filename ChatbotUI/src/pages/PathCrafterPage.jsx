import { Link } from "react-router-dom";
import { FaArrowLeft, FaBell } from "react-icons/fa6";
import BenefitGrid from "../components/pathcrafter/BenefitGrid.jsx";
import CTASection from "../components/pathcrafter/CTASection.jsx";
import DemoAcademicPlan from "../components/pathcrafter/DemoAcademicPlan.jsx";
import FeatureGrid from "../components/pathcrafter/FeatureGrid.jsx";
import Overview from "../components/pathcrafter/Overview.jsx";
import PathCrafterHero from "../components/pathcrafter/PathCrafterHero.jsx";
import Testimonials from "../components/pathcrafter/Testimonials.jsx";
import WorkflowTimeline from "../components/pathcrafter/WorkflowTimeline.jsx";

const PathCrafterTopBar = () => (
	<header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 px-5 py-4 backdrop-blur-xl sm:px-8 lg:px-12">
		<div className="flex items-center justify-between gap-4">
			<Link
				to="/edplan-nexus"
				className="inline-flex items-center gap-3 text-sm font-black text-slate-800 transition hover:text-indigo-600"
			>
				<FaArrowLeft className="text-xs" />
				Back to <span className="text-indigo-600">EdPlan Nexus</span>
			</Link>
			<div className="flex items-center gap-5">
				<button
					type="button"
					className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 shadow-sm transition hover:bg-slate-100"
					aria-label="Notifications"
				>
					<FaBell />
				</button>
				<button
					type="button"
					className="flex items-center gap-3 rounded-full border border-slate-200 bg-white py-2 pl-2 pr-4 text-sm font-bold text-slate-800 shadow-sm transition hover:border-indigo-200 hover:shadow-md"
				>
					<span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
						V
					</span>
					Verify it&apos;s you
				</button>
			</div>
		</div>
	</header>
);

const PathCrafterPage = () => (
	<section className="min-h-screen bg-[radial-gradient(circle_at_80%_8%,rgba(99,102,241,0.13),transparent_28%),linear-gradient(135deg,#f8fbff_0%,#ffffff_46%,#f7f5ff_100%)] text-slate-950">
		<PathCrafterTopBar />
		<div className="mx-auto max-w-[1560px] space-y-8 px-5 py-8 sm:px-8 lg:px-12">
			<PathCrafterHero />
			<div className="grid gap-8 xl:grid-cols-[0.75fr_1.25fr]">
				<Overview />
				<DemoAcademicPlan />
			</div>
			<FeatureGrid />
			<WorkflowTimeline />
			<BenefitGrid />
			<Testimonials />
			<CTASection />
		</div>
	</section>
);

export default PathCrafterPage;
