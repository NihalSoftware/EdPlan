const testimonials = [
	[
		"PathCrafter helped me understand my entire degree before I even registered for classes.",
		"Priya M.",
		"Computer Science Student",
	],
	[
		"I finally saw which prerequisites mattered and how my transfer credits changed the timeline.",
		"Jordan T.",
		"Transfer Student",
	],
	[
		"The semester roadmap made advising conversations faster, clearer, and much less stressful.",
		"Elena R.",
		"Academic Advisor",
	],
];

const Testimonials = () => (
	<section>
		<h2 className="text-2xl font-black text-slate-950">What students say</h2>
		<div className="mt-5 grid gap-5 lg:grid-cols-3">
			{testimonials.map(([quote, name, title]) => (
				<article key={name} className="rounded-2xl border border-slate-200 bg-white/85 p-6 shadow-sm">
					<p className="text-4xl font-black text-indigo-200">&ldquo;</p>
					<p className="mt-2 text-sm font-semibold leading-7 text-slate-700">
						{quote}
					</p>
					<p className="mt-5 font-black text-slate-950">{name}</p>
					<p className="text-xs font-bold text-slate-500">{title}</p>
				</article>
			))}
		</div>
	</section>
);

export default Testimonials;
