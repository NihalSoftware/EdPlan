import { FaAward, FaBookOpen, FaBus, FaHouse, FaUtensils, FaWifi } from "react-icons/fa6";

const scholarships = [
	["STEM Excellence Scholarship", "$2,500", "For students pursuing STEM programs.", "May 1, 2026"],
	["New Mexico Opportunity Scholarship", "$1,500", "For NM residents with financial need.", "June 15, 2026"],
	["Academic Merit Scholarship", "$1,000", "Based on GPA and academic performance.", "May 30, 2026"],
	["Community Leadership Grant", "$750", "For students with community service.", "April 20, 2026"],
];

const budget = [
	["Rent / Housing", "$600", 75, FaHouse, "bg-indigo-500"],
	["Food", "$250", 62, FaUtensils, "bg-emerald-500"],
	["Transportation", "$80", 35, FaBus, "bg-sky-500"],
	["Internet & Phone", "$60", 30, FaWifi, "bg-orange-500"],
	["Books & Supplies", "$75", 45, FaBookOpen, "bg-violet-500"],
	["Personal Expenses", "$120", 55, FaAward, "bg-pink-500"],
];

const ScholarshipsAndBudget = () => (
	<div className="grid gap-8 lg:grid-cols-2">
		<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
			<h2 className="text-2xl font-black text-slate-950">
				Scholarships You May Qualify For
			</h2>
			<div className="mt-6 grid gap-4 sm:grid-cols-2">
				{scholarships.map(([name, amount, eligibility, deadline]) => (
					<article key={name} className="rounded-2xl border border-orange-100 bg-orange-50/50 p-5">
						<div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-orange-600">
							<FaAward />
						</div>
						<h3 className="mt-4 font-black text-slate-950">{name}</h3>
						<p className="mt-1 text-sm font-black text-orange-600">{amount}</p>
						<p className="mt-2 text-xs font-semibold leading-5 text-slate-600">
							{eligibility}
						</p>
						<p className="mt-3 text-xs font-black text-slate-500">Deadline: {deadline}</p>
					</article>
				))}
			</div>
			<button
				type="button"
				className="mt-5 rounded-xl border border-orange-100 bg-white px-4 py-3 text-sm font-black text-orange-700 shadow-sm transition hover:shadow-md"
			>
				View All Scholarships
			</button>
		</section>

		<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
			<h2 className="text-2xl font-black text-slate-950">Monthly Budget Example</h2>
			<div className="mt-6 space-y-5">
				{budget.map(([label, amount, percent, Icon, color]) => (
					<div key={label}>
						<div className="mb-2 flex items-center justify-between gap-4">
							<div className="flex items-center gap-3">
								<div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-50 text-slate-600">
									<Icon />
								</div>
								<span className="text-sm font-black text-slate-800">{label}</span>
							</div>
							<span className="text-sm font-black text-slate-700">{amount}</span>
						</div>
						<div className="h-2 overflow-hidden rounded-full bg-slate-100">
							<div className={`h-full rounded-full ${color}`} style={{ width: `${percent}%` }} />
						</div>
					</div>
				))}
			</div>
			<div className="mt-7 rounded-2xl bg-indigo-50/70 p-4 text-sm font-black text-indigo-700">
				Total monthly estimate: $1,185 / $1,800
			</div>
		</section>
	</div>
);

export default ScholarshipsAndBudget;
