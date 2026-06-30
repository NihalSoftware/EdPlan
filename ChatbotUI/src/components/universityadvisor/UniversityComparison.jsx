import { FaCheck, FaWandMagicSparkles } from "react-icons/fa6";

const rows = [
	["Location", "Espanola, New Mexico", "Santa Fe, New Mexico"],
	["Institution Type", "Community College", "Community College"],
	["Tuition (In-State)", "$2,520 / year", "$2,290 / year"],
	["Program Credits", "60 Credits", "60 Credits"],
	["Average Class Size", "18", "20"],
	["Student-Faculty Ratio", "15:1", "16:1"],
	["Transfer Opportunities", "High transfer agreements with NM universities", "High articulation with NM universities"],
	["Online Course Availability", "Yes", "Yes"],
	["Campus Support", "Strong", "Strong"],
	["Best For", "Affordable path with close-knit support", "Flexible option with wider program choices"],
];

const recommendations = [
	["Northern New Mexico College", "Espanola, NM", "Best for affordability", "90%"],
	["Santa Fe Community College", "Santa Fe, NM", "Flexible programs", "92%"],
	["University of New Mexico", "Albuquerque, NM", "Top research university", "87%"],
	["New Mexico State University", "Las Cruces, NM", "Strong engineering programs", "85%"],
];

const UniversityComparison = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
			<div>
				<h2 className="text-2xl font-black text-slate-950">
					University Comparison Example
				</h2>
				<p className="mt-2 text-sm font-semibold text-slate-600">
					Comparison based on B.S. in Computer Science
				</p>
			</div>
			<button
				type="button"
				className="self-start rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-black text-slate-700 shadow-sm transition hover:border-emerald-200 hover:text-emerald-600 lg:self-auto"
			>
				Customize Comparison
			</button>
		</div>

		<div className="mt-6 overflow-x-auto rounded-2xl border border-slate-200">
			<table className="min-w-[760px] w-full border-collapse text-sm">
				<thead>
					<tr className="bg-slate-50 text-left">
						<th className="w-1/3 px-5 py-4 font-black text-slate-700">Factor</th>
						<th className="px-5 py-4 font-black text-emerald-700">
							Northern New Mexico College (NNMC)
						</th>
						<th className="px-5 py-4 font-black text-indigo-700">
							Santa Fe Community College (SFCC)
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
								<CellValue value={nnmc} />
							</td>
							<td className="border-t border-slate-100 px-5 py-4 font-semibold text-slate-700">
								<CellValue value={sfcc} />
							</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>

		<div className="mt-6 rounded-2xl border border-emerald-100 bg-gradient-to-r from-emerald-50 to-indigo-50 p-5">
			<div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
				<div className="flex gap-4">
					<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white text-emerald-600 shadow-sm">
						<FaWandMagicSparkles />
					</div>
					<div>
						<h3 className="font-black text-slate-950">Our AI Suggestion</h3>
						<p className="mt-2 max-w-4xl text-sm font-semibold leading-6 text-slate-700">
							Based on your interest in Computer Science and your goal of transferring
							to a four-year university, <strong>Northern New Mexico College (NNMC)</strong>
							{" "}may be the better choice because of its strong transfer agreements
							and affordable tuition.
						</p>
					</div>
				</div>
				<button
					type="button"
					className="self-start rounded-xl bg-white px-4 py-3 text-sm font-black text-emerald-700 shadow-sm transition hover:shadow-md md:self-auto"
				>
					View Reasons
				</button>
			</div>
		</div>

		<div className="mt-8">
			<h3 className="text-xl font-black text-slate-950">
				Top Recommended Universities for You
			</h3>
			<div className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
				{recommendations.map(([name, location, highlight, match]) => (
					<article key={name} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
						<div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
							<FaCheck />
						</div>
						<h4 className="mt-4 font-black text-slate-950">{name}</h4>
						<p className="mt-1 text-xs font-bold text-slate-500">{location}</p>
						<p className="mt-3 text-sm font-semibold leading-6 text-slate-600">
							{highlight}
						</p>
						<p className="mt-4 text-sm font-black text-emerald-600">{match} Match</p>
					</article>
				))}
			</div>
		</div>
	</section>
);

const CellValue = ({ value }) => {
	if (value === "Yes" || value === "Strong") {
		return (
			<span className="inline-flex items-center gap-2">
				<span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-100 text-[10px] text-emerald-700">
					<FaCheck />
				</span>
				{value}
			</span>
		);
	}
	return value;
};

export default UniversityComparison;
