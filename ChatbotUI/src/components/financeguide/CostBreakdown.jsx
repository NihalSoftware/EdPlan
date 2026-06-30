import {
	FaBookOpen,
	FaBus,
	FaHouse,
	FaReceipt,
	FaUtensils,
} from "react-icons/fa6";
import { FaDollarSign } from "react-icons/fa";

const summary = [
	["$2,250", "Annual Tuition", FaDollarSign],
	["$7,200", "Living Expenses", FaHouse],
	["$900", "Books & Supplies", FaBookOpen],
	["$1,000", "Transportation", FaBus],
	["$1,200", "Miscellaneous", FaReceipt],
	["$12,550", "Estimated Total Annual Cost", FaUtensils],
];

const rows = [
	["Tuition", "$2,250"],
	["Housing", "$7,200"],
	["Food", "$3,000"],
	["Books", "$900"],
	["Transportation", "$1,000"],
	["Personal Expenses", "$1,200"],
];

const CostBreakdown = () => (
	<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
		<div>
			<h2 className="text-2xl font-black text-slate-950">Estimated Cost of Attendance</h2>
			<p className="mt-2 text-sm font-semibold text-slate-600">
				Sample estimation for Northern New Mexico College - B.S. Computer Science
			</p>
		</div>
		<div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
			{summary.map(([value, label, Icon]) => (
				<div key={label} className="rounded-2xl bg-orange-50/70 p-4">
					<div className="flex items-center gap-3">
						<div className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-orange-600">
							<Icon />
						</div>
						<div>
							<p className="text-lg font-black text-slate-950">{value}</p>
							<p className="text-xs font-bold text-slate-500">{label}</p>
						</div>
					</div>
				</div>
			))}
		</div>
		<div className="mt-6 overflow-hidden rounded-2xl border border-slate-200">
			<table className="w-full text-sm">
				<thead className="bg-slate-50 text-left">
					<tr>
						<th className="px-5 py-4 font-black text-slate-700">Category</th>
						<th className="px-5 py-4 text-right font-black text-slate-700">
							Estimated Annual Cost
						</th>
					</tr>
				</thead>
				<tbody>
					{rows.map(([label, value], index) => (
						<tr key={label} className={index % 2 ? "bg-white" : "bg-slate-50/50"}>
							<td className="border-t border-slate-100 px-5 py-4 font-semibold text-slate-700">
								{label}
							</td>
							<td className="border-t border-slate-100 px-5 py-4 text-right font-black text-slate-900">
								{value}
							</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	</section>
);

export default CostBreakdown;
