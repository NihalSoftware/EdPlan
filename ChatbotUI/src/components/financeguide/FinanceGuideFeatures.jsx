import {
	FaBuildingColumns,
	FaChartPie,
	FaGift,
	FaHouse,
	FaLandmark,
	FaScaleBalanced,
} from "react-icons/fa6";
import { FaDollarSign } from "react-icons/fa";

const features = [
	["Tuition Estimator", "Estimate tuition based on university and program.", FaDollarSign],
	["Cost of Living", "Estimate housing, food, transportation, and essentials.", FaHouse],
	["Scholarship Finder", "Discover scholarships and aid opportunities.", FaGift],
	["Budget Planner", "Estimate semester-wise and monthly expenses.", FaChartPie],
	["Loan Planning", "Understand estimated education loan needs.", FaLandmark],
	["Financial Comparison", "Compare total costs across universities.", FaScaleBalanced],
];

const FinanceGuideFeatures = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<h2 className="text-2xl font-black text-slate-950">How FinanceGuide Helps You</h2>
		<div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
			{features.map(([title, description, Icon]) => (
				<article key={title} className="rounded-2xl bg-slate-50/80 p-4">
					<div className="flex h-11 w-11 items-center justify-center rounded-full bg-orange-50 text-lg text-orange-600">
						<Icon />
					</div>
					<h3 className="mt-4 text-sm font-black text-slate-950">{title}</h3>
					<p className="mt-2 text-xs font-semibold leading-5 text-slate-600">
						{description}
					</p>
				</article>
			))}
		</div>
		<div className="mt-6 flex items-center gap-3 rounded-2xl bg-orange-50/70 p-4 text-sm font-black text-orange-700">
			<FaBuildingColumns />
			Plan education costs with tuition, living expenses, aid, and school comparisons in one view.
		</div>
	</section>
);

export default FinanceGuideFeatures;
