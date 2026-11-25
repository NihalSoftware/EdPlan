import {
	FaBalanceScale,
	FaBriefcase,
	FaClock,
	FaCompass,
	FaExchangeAlt,
	FaLayerGroup,
	FaRoute,
	FaShieldAlt,
} from "react-icons/fa";

const benefits = [
	["Graduate on time", FaClock],
	["Reduce scheduling conflicts", FaShieldAlt],
	["Never miss prerequisites", FaRoute],
	["Balance semester workload", FaBalanceScale],
	["Optimize graduation timeline", FaCompass],
	["Support transfer students", FaExchangeAlt],
	["Career-focused planning", FaBriefcase],
	["Adaptive recommendations", FaLayerGroup],
];

const BenefitGrid = () => (
	<section>
		<h2 className="text-2xl font-black text-slate-950">Benefits</h2>
		<div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
			{benefits.map(([label, Icon]) => (
				<div
					key={label}
					className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white/85 p-5 shadow-sm transition hover:-translate-y-1 hover:border-indigo-100 hover:shadow-xl hover:shadow-indigo-100/70"
				>
					<div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
						<Icon />
					</div>
					<p className="font-black text-slate-900">{label}</p>
				</div>
			))}
		</div>
	</section>
);

export default BenefitGrid;
