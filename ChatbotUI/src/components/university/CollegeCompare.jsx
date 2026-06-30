import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { compareUniversitiesByIds } from "../../services/universityService.js";
import { load as loadStorage, save as saveStorage } from "../../utils/storage.js";

const dataNotAvailable = "N/A";

const formatPercent = (value) =>
	value || value === 0 ? `${(value * 100).toFixed(1).replace(/\.0$/, "")} %` : "N/A";
const formatCurrency = (value) =>
	value || value === 0 ? `$ ${Number(value).toLocaleString()}` : "N/A";
const formatNumber = (value) =>
	value || value === 0 ? Number(value).toLocaleString() : "N/A";
const formatRatio = (value) =>
	value || value === 0 ? `${Number(value).toFixed(0)} : 1` : "N/A";
const formatWebsite = (value) =>
	value ? (
		<a
			href={value.startsWith("http") ? value : `https://${value}`}
			target="_blank"
			rel="noreferrer"
			className="text-indigo-600 hover:text-indigo-500"
		>
			Visit Website
		</a>
	) : (
		"N/A"
	);
const hasValue = (value) => value || value === 0;
const formatSatRange = (school) => {
	if (!school) return "N/A";
	const low = school.sat_reading_25th;
	const high = school.sat_reading_75th;

	if (hasValue(low) && hasValue(high)) {
		return `${formatNumber(low)} - ${formatNumber(high)}`;
	}
	if (hasValue(low)) {
		return `>= ${formatNumber(low)}`;
	}
	if (hasValue(high)) {
		return `<= ${formatNumber(high)}`;
	}
	return "Open Admission Policy";
};
const formatActRange = (school) => {
	if (!school) return "Open Admission Policy";
	const low = school.act_score_25th;
	const high = school.act_score_75th;

	if (hasValue(low) && hasValue(high)) {
		return `${formatNumber(low)} - ${formatNumber(high)}`;
	}
	if (hasValue(low)) {
		return `>= ${formatNumber(low)}`;
	}
	if (hasValue(high)) {
		return `<= ${formatNumber(high)}`;
	}
	return "Open Admission Policy";
};

const overviewMetrics = [
	{ key: "city", label: "City" },
	{ key: "state", label: "State" },
	{ key: "organization_type", label: "Institution Type" },
	{ key: "location_type", label: "Campus Setting" },
	{
		key: "campus_size_acres",
		label: "Campus Area (acres)",
		accessor: (s) => s.campus_size_acres || s.campus_acres || s.acres || s.campus?.acres,
		format: formatNumber,
	},
	{ key: "size", label: "Total Student Enrollment", format: formatNumber },
	{
		key: "rank",
		label: "University Ranking",
		accessor: (s) => s.rank || s.national_rank || s.world_rank,
		format: (v) => (v || v === 0 ? v : "N/A"),
	},
	{ key: "website", label: "Official Website", format: formatWebsite },
];

const institutionMetrics = [
	{
		key: "faculty_count",
		label: "Total Faculty",
		accessor: (s) => s.faculty_count || s.number_of_faculty || s.faculty?.total,
		format: formatNumber,
	},
	{
		key: "faculty_phd_count",
		label: "Faculty with Doctoral Degrees",
		accessor: (s) =>
			s.faculty_phd_count || s.faculty_with_phd_count ||
			(s.faculty_with_phd && s.faculty_count ? Math.round(Number(s.faculty_with_phd) * Number(s.faculty_count)) : undefined) ||
			s.faculty_with_phd,
		format: formatNumber,
	},
	{ key: "student_faculty_ratio", label: "Student-to-Faculty Ratio", format: formatRatio },
];

const researchMetrics = [
	{
		key: "program_accreditations",
		label: "Accredited Programs",
		accessor: (s) => s.program_accreditations || s.accreditations_count || s.accreditation_count,
		format: formatNumber,
	},
	{
		key: "centres_of_excellence",
		label: "Centers of Excellence",
		accessor: (s) => s.centres_of_excellence || s.centers_of_excellence || s.centres_count,
		format: formatNumber,
	},
	{
		key: "patent_grants",
		label: "Patents Awarded",
		accessor: (s) => s.patents_count || s.patent_grants || s.patent_count,
		format: formatNumber,
	},
	{
		key: "research_funding",
		label: "Annual Research Funding",
		accessor: (s) => s.research_funding || s.research_expenditure || s.research_grants,
		format: formatCurrency,
	},
];

const admissionsMetrics = [
	{ key: "acceptance_rate", label: "Acceptance Rate", format: formatPercent },
	{
		key: "test_score",
		label: "SAT Critical Reading Range",
		render: (_, school) => formatSatRange(school),
	},
	{
		key: "act_score",
		label: "ACT Score Range",
		render: (_, school) => formatActRange(school),
	},
	{
		key: "first_year_return_rate",
		label: "First-Year Retention Rate",
		format: formatPercent,
	},
	{ key: "graduation_rate", label: "Graduation Rate", format: formatPercent },
];

const enrollmentMetrics = [
	{ key: "size", label: "Undergraduate Enrollment", format: formatNumber },
	{
		key: "international_students",
		label: "International Students",
		accessor: (s) => s.international_students || s.international_student_count || (s.international_student_share && s.size ? Math.round(Number(s.international_student_share) * Number(s.size)) : undefined),
		format: formatNumber,
	},
	{ key: "full_time_enrollment", label: "Full-time Enrollment", format: formatNumber },
	{ key: "part_time_enrollment", label: "Part-time Enrollment", format: formatNumber },
];

const outcomeMetrics = [
	{
		key: "campus_visits",
		label: "Annual Campus Drives",
		accessor: (s) => s.campus_visits || s.visits_count || s.open_days_count,
		format: formatNumber,
	},
	{
		key: "placement_drive",
		label: "Placement Rate",
		accessor: (s) => s.placement_drive || s.placement_info || s.placement_rate,
		render: (val) => (val === undefined || val === null ? "N/A" : typeof val === "number" ? `${Math.round(val * 100)}%` : String(val)),
	},
];

const financialMetrics = [
	{ key: "average_annual_cost", label: "Average Annual Cost", format: formatCurrency },
	{ key: "median_earnings", label: "Median Graduate Earnings", format: formatCurrency },
	{ key: "median_debt", label: "Median Student Debt After Graduation", format: formatCurrency },
	{
		key: "typical_monthly_payment",
		label: "Estimated Monthly Loan Payment",
		format: formatCurrency,
	},
	{
		key: "federal_loan_rate",
		label: "Students Using Federal Loans",
		format: formatPercent,
	},
	{
		key: "percent_more_than_hs",
		label: "Earnings Advantage Over High School Graduate",
		format: formatPercent,
	},
];

// Helper to get a metric value from the API response only.
const getMetricValue = (metric, school) => {
	if (!school) return undefined;
	if (metric.accessor) {
		try {
			return metric.accessor(school);
		} catch {
			return undefined;
		}
	}
	return metric.key ? school[metric.key] : undefined;
};
const SectionCard = ({ title, children, note }) => (
	<div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 space-y-3">
		<div>
			<h3 className="text-[22px] font-bold text-slate-700">{title}</h3>
			{note && <p className="text-xs text-slate-500">{note}</p>}
		</div>
		{children}
	</div>
);

const ComparisonTable = ({ title, metrics, schools, note }) => (
	<SectionCard title={title} note={note}>
		<div className="overflow-x-auto">
			<table className="min-w-full">
				<thead>
					<tr className="uppercase tracking-wide text-slate-600">
						<th className="text-left px-3 py-2 font-bold w-1/4">Metric</th>
						{schools.map((school) => (
							<th
								key={school.unit_id || school.name}
								className={`text-left px-3 py-2 font-bold w-3/12`}
							>
								{school.name || "Selected college"}
							</th>
						))}
					</tr>
				</thead>
				<tbody>
					{metrics.map((metric) => (
						<tr key={metric.key || metric.label} className="border-t border-slate-100">
							<td className="px-3 py-2 font-medium text-slate-700">{metric.label}</td>
							{schools.map((school) => {
								const rawValue = getMetricValue(metric, school);
								let content;
								if (metric.render) {
									content = metric.render(rawValue, school);
								} else if (metric.format && rawValue !== undefined && rawValue !== null && rawValue !== "") {
									content = metric.format(rawValue, school);
								} else if (rawValue !== undefined && rawValue !== null && rawValue !== "") {
									content = String(rawValue);
								} else {

									content = dataNotAvailable;
								}

								return (
									<td
										key={`${metric.key || metric.label}-${school.unit_id || school.name}`}
										className="px-3 py-2 text-slate-800"
									>
										{content}
									</td>
								);
							})}
						</tr>
					))}
				</tbody>
			</table>
		</div>
	</SectionCard>
);

const CollegeCompare = () => {
	const [selected, setSelected] = useState([]);
	const [comparison, setComparison] = useState({});
	const [loadingCompare, setLoadingCompare] = useState(false);
	const [error, setError] = useState("");
	const [initializing, setInitializing] = useState(true);
	const navigate = useNavigate();

	const handleBackToFind = () => {
		const tempProgram = loadStorage("SelectedProgram", "");
		const tempDegree = loadStorage("SelectedDegreeLevel", "");

		// If there is a temporary selection from Career Program page, promote it to persistent storage
		if (tempProgram) {
			saveStorage("Programname", tempProgram);
			saveStorage("Programnameview", tempProgram);
			// Clear the temporary key so FindUniversity uses persistent storage moving forward
			saveStorage("SelectedProgram", "");
		}
		if (tempDegree) {
			saveStorage("ProgramDegree", tempDegree);
			saveStorage("SelectedDegreeLevel", tempDegree);
		}

		navigate("/uni");
	};

	useEffect(() => {
		const stored = loadStorage("CompareQueue", []);
		if (Array.isArray(stored)) {
			const unique = [];
			const seen = new Set();
			stored.forEach((entry) => {
				if (entry?.unit_id && !seen.has(entry.unit_id)) {
					seen.add(entry.unit_id);
					unique.push(entry);
				}
			});
			setSelected(unique.slice(0, 3));
		}
		setInitializing(false);
	}, []);

	useEffect(() => {
		if (initializing) return;
		saveStorage("CompareQueue", selected);
	}, [selected, initializing]);

	const handleRemove = (unitId) => {
		setSelected((prev) => prev.filter((entry) => entry.unit_id !== unitId));
		setComparison((prev) => {
			const next = { ...prev };
			delete next[unitId];
			return next;
		});
	};

	useEffect(() => {
		if (initializing) return;
		if (selected.length === 0) {
			setComparison({});
			return;
		}
		const fetchComparison = async () => {
			setLoadingCompare(true);
			setError("");
			try {
				const detail = await compareUniversitiesByIds(selected.map((entry) => entry.unit_id));
				const mapped = detail.reduce((acc, school) => {
					if (school?.unit_id) {
						acc[school.unit_id] = school;
					}
					return acc;
				}, {});
				setComparison(mapped);
			} catch (err) {
				console.error(err);
				setError("Unable to load comparison data.");
			} finally {
				setLoadingCompare(false);
			}
		};
		fetchComparison();
	}, [selected, initializing]);

	const comparisonOrder = useMemo(
		() => selected.map((entry) => comparison[entry.unit_id] || entry),
		[selected, comparison]
	);
	return (
		<section className="space-y-6">
			<header className="space-y-1">
				<h1 className="text-3xl font-semibold text-slate-900">Compare <span className="text-[#0069e0]">Colleges</span></h1>
				<p className="text-lg text-slate-600">
					<button
						type="button"
						onClick={handleBackToFind}
						className="mt-2 inline-flex items-center gap-2 px-3 py-2 rounded-lg text-indigo-700 hover:bg-slate-200 text-sm font-medium"
					>
						← Go Back
					</button> Use the Find University page to select upto three colleges for comparison.
				</p>

			</header>
			{error && (
				<div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
					{error}
				</div>
			)}

			{selected.length > 0 && (
				<div className="space-y-4">
					<div className="flex flex-wrap gap-2">
						{selected.map((entry) => (
							<span
								key={entry.unit_id}
								className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-700"
							>
								{entry.name}
								<button
									onClick={() => handleRemove(entry.unit_id)}
									className="text-indigo-500 hover:text-indigo-700"
								>
									x
								</button>
							</span>
						))}
					</div>

					{loadingCompare ? (
						<div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 text-sm text-slate-500">
							Loading Data…
						</div>
					) : (
						<div className="space-y-4">
							<ComparisonTable title="College Overview" metrics={overviewMetrics} schools={comparisonOrder} />
							<ComparisonTable title="Academic & Faculty Profile" metrics={institutionMetrics} schools={comparisonOrder} />
							<ComparisonTable title="Research & Innovation" metrics={researchMetrics} schools={comparisonOrder} />
							<ComparisonTable title="Admissions & Student Success" metrics={admissionsMetrics} schools={comparisonOrder} />
							<ComparisonTable title="Enrollment Breakdown" metrics={enrollmentMetrics} schools={comparisonOrder} />
							<ComparisonTable title="Cost & Financial Aid Metrics" metrics={financialMetrics} schools={comparisonOrder} />
							<ComparisonTable title="Placement & Campus Engagement" metrics={outcomeMetrics} schools={comparisonOrder} />
							</div>
					)}
				</div>
			)}
			{!initializing && selected.length === 0 && (
				<div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 text-sm text-slate-600">
					No Colleges/Universities are selected.
				</div>
			)}
		</section>
	);
};

export default CollegeCompare;
