const metrics = [
	["Programming", 90, "bg-emerald-500"],
	["Mathematics", 82, "bg-blue-500"],
	["AI Skills", 45, "bg-orange-500"],
	["Projects", 70, "bg-violet-500"],
	["Communication", 80, "bg-cyan-500"],
	["Internship Experience", 40, "bg-rose-500"],
];

const CareerReadiness = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<h2 className="text-2xl font-black text-slate-950">Career Readiness Score</h2>
		<div className="mt-6 grid gap-7 lg:grid-cols-[16rem_minmax(0,1fr)] lg:items-center">
			<div className="rounded-3xl bg-gradient-to-br from-cyan-50 to-indigo-50 p-7 text-center">
				<div className="mx-auto flex h-36 w-36 items-center justify-center rounded-full border-[14px] border-cyan-200 bg-white shadow-inner">
					<div>
						<p className="text-4xl font-black text-slate-950">78%</p>
						<p className="mt-1 text-xs font-black uppercase tracking-wide text-cyan-700">
							Overall Readiness
						</p>
					</div>
				</div>
				<p className="mt-5 text-sm font-semibold leading-6 text-slate-600">
					You are well-positioned to pursue Machine Learning roles.
				</p>
			</div>
			<div className="grid gap-5 md:grid-cols-2">
				{metrics.map(([label, value, color]) => (
					<div key={label}>
						<div className="mb-2 flex items-center justify-between gap-3">
							<p className="text-sm font-black text-slate-800">{label}</p>
							<p className="text-sm font-black text-slate-600">{value}%</p>
						</div>
						<div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
							<div className={`h-full rounded-full ${color}`} style={{ width: `${value}%` }} />
						</div>
					</div>
				))}
			</div>
		</div>
	</section>
);

export default CareerReadiness;
