import { FaArrowRight, FaWandMagicSparkles } from "react-icons/fa6";

const rows = [
	["Tuition", "$2,250 / year", "$2,290 / year"],
	["Living Cost", "$7,200 / year", "$8,000 / year"],
	["Total Estimated Cost", "$12,550 / year", "$13,190 / year"],
	["Scholarships Available", "Yes", "Yes"],
	["Average Financial Aid", "$2,600 / year", "$2,100 / year"],
	["Estimated Student Debt", "$15,000", "$17,500"],
];

const CostComparison = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<h2 className="text-2xl font-black text-slate-950">Compare Education Costs</h2>
		<div className="mt-6 overflow-x-auto rounded-2xl border border-slate-200">
			<table className="min-w-[720px] w-full text-sm">
				<thead className="bg-slate-50 text-left">
					<tr>
						<th className="px-5 py-4 font-black text-slate-700">Category</th>
						<th className="px-5 py-4 font-black text-emerald-700">
							Northern New Mexico College
						</th>
						<th className="px-5 py-4 font-black text-indigo-700">
							Santa Fe Community College
						</th>
					</tr>
				</thead>
				<tbody>
					{rows.map(([label, nnmc, sfcc], index) => (
						<tr key={label} className={index % 2 ? "bg-white" : "bg-slate-50/50"}>
							<td className="border-t border-slate-100 px-5 py-4 font-black text-slate-800">
								{label}
							</td>
							<td className="border-t border-slate-100 px-5 py-4 font-semibold text-slate-700">
								{nnmc}
							</td>
							<td className="border-t border-slate-100 px-5 py-4 font-semibold text-slate-700">
								{sfcc}
							</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
		<div className="mt-6 rounded-2xl border border-emerald-100 bg-gradient-to-r from-emerald-50 to-orange-50 p-5">
			<div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
				<div className="flex gap-4">
					<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white text-emerald-600 shadow-sm">
						<FaWandMagicSparkles />
					</div>
					<div>
						<h3 className="font-black text-slate-950">Our Financial Recommendation</h3>
						<p className="mt-2 max-w-4xl text-sm font-semibold leading-6 text-slate-700">
							Based on your selected program and budget, Northern New Mexico College
							offers the lowest overall cost while maintaining strong transfer
							opportunities, making it the most cost-effective option.
						</p>
					</div>
				</div>
				<button
					type="button"
					className="inline-flex items-center gap-2 self-start rounded-xl bg-white px-4 py-3 text-sm font-black text-emerald-700 shadow-sm transition hover:shadow-md md:self-auto"
				>
					View Cost Analysis
					<FaArrowRight className="text-xs" />
				</button>
			</div>
		</div>
	</section>
);

export default CostComparison;
