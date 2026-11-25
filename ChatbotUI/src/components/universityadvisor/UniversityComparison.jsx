import { useEffect, useMemo, useState } from "react";
import { FaCheck, FaWandMagicSparkles } from "react-icons/fa6";
import {
	compareUniversities,
	searchUniversitiesForComparison,
} from "../../services/comparisonService.js";

const formatValue = (value) =>
	value === undefined || value === null || value === "" ? "N/A" : value;

const UniversityComparison = () => {
	const [universities, setUniversities] = useState([]);
	const [metadata, setMetadata] = useState({});
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	useEffect(() => {
		let cancelled = false;
		const loadComparison = async () => {
			setLoading(true);
			setError("");
			try {
				const search = await searchUniversitiesForComparison({
					state: "New Mexico",
					limit: 5,
				});
				const selected = (search.results || [])
					.filter((item) => item.university_id)
					.slice(0, 2);
				if (selected.length < 2) {
					throw new Error("At least two universities are required.");
				}
				const comparison = await compareUniversities(
					selected.map((item) => item.university_id)
				);
				if (!cancelled) {
					setUniversities(comparison.universities || []);
					setMetadata(comparison.metadata || {});
				}
			} catch (err) {
				console.error(err);
				if (!cancelled) {
					setError("Unable to load university comparison data.");
				}
			} finally {
				if (!cancelled) setLoading(false);
			}
		};
		loadComparison();
		return () => {
			cancelled = true;
		};
	}, []);

	const rows = useMemo(() => {
		const [first, second] = universities;
		return [
			["Location", [first?.city, first?.state].filter(Boolean).join(", "), [second?.city, second?.state].filter(Boolean).join(", ")],
			["Institution Type", first?.public_private, second?.public_private],
			["Website", first?.website, second?.website],
			["Programs in Catalog", first?.program_count, second?.program_count],
			["Tuition", null, null],
			["Transfer Agreements", null, null],
		];
	}, [universities]);

	const recommendations = universities.map((item, index) => ({
		name: item.university_name || item.name || "University",
		location: [item.city, item.state].filter(Boolean).join(", ") || "Location unavailable",
		highlight:
			index === 0
				? "Available in the EdPlan comparison database"
				: "Comparable catalog data available",
	}));

	return (
		<section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-xl lg:p-8">
			<div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
				<div>
					<h2 className="text-2xl font-black text-slate-950">
						University Comparison
					</h2>
					<p className="mt-2 text-sm font-semibold text-slate-600">
						Loaded from the EdPlan comparison backend
					</p>
				</div>
			</div>

			{loading && (
				<div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm font-semibold text-slate-600">
					Loading comparison data...
				</div>
			)}

			{error && (
				<div className="mt-6 rounded-2xl border border-rose-100 bg-rose-50 p-5 text-sm font-semibold text-rose-700">
					{error}
				</div>
			)}

			{!loading && !error && universities.length >= 2 && (
				<>
					<div className="mt-6 overflow-x-auto rounded-2xl border border-slate-200">
						<table className="min-w-[760px] w-full border-collapse text-sm">
							<thead>
								<tr className="bg-slate-50 text-left">
									<th className="w-1/3 px-5 py-4 font-black text-slate-700">Factor</th>
									{universities.slice(0, 2).map((university, index) => (
										<th
											key={university.university_id}
											className={`px-5 py-4 font-black ${index === 0 ? "text-emerald-700" : "text-indigo-700"}`}
										>
											{university.university_name || university.name}
										</th>
									))}
								</tr>
							</thead>
							<tbody>
								{rows.map(([label, first, second], index) => (
									<tr key={label} className={index % 2 ? "bg-white" : "bg-slate-50/50"}>
										<td className="border-t border-slate-100 px-5 py-4 font-black text-slate-800">
											{label}
										</td>
										<td className="border-t border-slate-100 px-5 py-4 font-semibold text-slate-700">
											<CellValue value={formatValue(first)} />
										</td>
										<td className="border-t border-slate-100 px-5 py-4 font-semibold text-slate-700">
											<CellValue value={formatValue(second)} />
										</td>
									</tr>
								))}
							</tbody>
						</table>
					</div>

					<div className="mt-6 rounded-2xl border border-emerald-100 bg-gradient-to-r from-emerald-50 to-indigo-50 p-5">
						<div className="flex gap-4">
							<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white text-emerald-600 shadow-sm">
								<FaWandMagicSparkles />
							</div>
							<div>
								<h3 className="font-black text-slate-950">Advisor Note</h3>
								<p className="mt-2 max-w-4xl text-sm font-semibold leading-6 text-slate-700">
									Comparison data is limited to fields available in the EdPlan database.
									{metadata.unavailable_fields?.length
										? ` Unavailable fields: ${metadata.unavailable_fields.join(", ")}.`
										: ""}
								</p>
							</div>
						</div>
					</div>

					<div className="mt-8">
						<h3 className="text-xl font-black text-slate-950">
							Compared Universities
						</h3>
						<div className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
							{recommendations.map((item) => (
								<article key={item.name} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
									<div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
										<FaCheck />
									</div>
									<h4 className="mt-4 font-black text-slate-950">{item.name}</h4>
									<p className="mt-1 text-xs font-bold text-slate-500">{item.location}</p>
									<p className="mt-3 text-sm font-semibold leading-6 text-slate-600">
										{item.highlight}
									</p>
								</article>
							))}
						</div>
					</div>
				</>
			)}
		</section>
	);
};

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
