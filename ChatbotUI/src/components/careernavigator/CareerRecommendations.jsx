import { FaBrain, FaCloud, FaDatabase, FaShieldHalved } from "react-icons/fa6";

const careers = [
	["Machine Learning Engineer", "95%", "$135,000/year", "High", FaBrain, "text-indigo-600"],
	["Data Engineer", "90%", "$125,000/year", "High", FaDatabase, "text-emerald-600"],
	["Cybersecurity Engineer", "87%", "$120,000/year", "High", FaShieldHalved, "text-orange-600"],
	["Cloud Solutions Engineer", "84%", "$122,000/year", "Growing", FaCloud, "text-violet-600"],
];

const CareerRecommendations = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<h2 className="text-2xl font-black text-slate-950">
			Career Recommendations For You
		</h2>
		<p className="mt-2 text-sm font-semibold text-slate-600">
			Based on a Computer Science student interested in Artificial Intelligence.
		</p>
		<div className="mt-7 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
			{careers.map(([title, match, salary, demand, Icon, color]) => (
				<article
					key={title}
					className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
				>
					<div className="flex items-start justify-between gap-4">
						<div className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-50 text-xl ${color}`}>
							<Icon />
						</div>
						<span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-black text-cyan-700">
							{match}
						</span>
					</div>
					<h3 className="mt-5 text-base font-black leading-6 text-slate-950">
						{title}
					</h3>
					<div className="mt-5 space-y-3 text-sm">
						<div>
							<p className="text-xs font-black uppercase tracking-wide text-slate-400">
								Average Salary
							</p>
							<p className="mt-1 font-black text-slate-900">{salary}</p>
						</div>
						<div className="flex items-center justify-between gap-3">
							<span className="text-xs font-black uppercase tracking-wide text-slate-400">
								Demand
							</span>
							<span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-black text-emerald-700">
								{demand}
							</span>
						</div>
					</div>
				</article>
			))}
		</div>
	</section>
);

export default CareerRecommendations;
