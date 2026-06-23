import { useEffect, useMemo, useState } from "react";
import { searchUniversities } from "../../services/universityService.js";
import { listPrograms } from "../../services/educationPlanService.js";
import { load as loadStorage, save as saveStorage } from "../../utils/storage.js";
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

// const stateOptions = [
// 	"",
// 	"AL",
// 	"AK",
// 	"AZ",
// 	"AR",
// 	"CA",
// 	"CO",
// 	"CT",
// 	"DE",
// 	"FL",
// 	"GA",
// 	"HI",
// 	"ID",
// 	"IL",
// 	"IN",
// 	"IA",
// 	"KS",
// 	"KY",
// 	"LA",
// 	"ME",
// 	"MD",
// 	"MA",
// 	"MI",
// 	"MN",
// 	"MS",
// 	"MO",
// 	"MT",
// 	"NE",
// 	"NV",
// 	"NH",
// 	"NJ",
// 	"NM",
// 	"NY",
// 	"NC",
// 	"ND",
// 	"OH",
// 	"OK",
// 	"OR",
// 	"PA",
// 	"RI",
// 	"SC",
// 	"SD",
// 	"TN",
// 	"TX",
// 	"UT",
// 	"VT",
// 	"VA",
// 	"WA",
// 	"WV",
// 	"WI",
// 	"WY",
// ];

const formatPercent = (value) =>
	value || value === 0 ? `${Math.round(value * 100)}%` : "N/A";
const formatCurrency = (value) =>
	value || value === 0 ? `$${Number(value).toLocaleString()}` : "N/A";

const allowedCampuses = [
	"University of New Mexico-Main Campus",
	"New Mexico State University-Main Campus",
	"Santa Fe Community College",
	"Northern New Mexico College",
	"San Juan College",
];
const allowedCampusesLower = new Set(allowedCampuses.map((name) => name.toLowerCase()));
const normalizeDegree = (value = "") => {
	const raw = String(value).trim().toLowerCase();
	const aliases = {
		certificates: "certificate",
		associate: "associate",
		bachelors: "bachelor",
		masters: "master",
	};
	if (aliases[raw]) return aliases[raw];
	if (raw.endsWith("s") && raw.length > 4) return raw.slice(0, -1);
	return raw;
};

const FindUniversity = ({ onSelectProgram }) => {
	const [universities, setUniversities] = useState([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [searchTerm, setSearchTerm] = useState("");
	const [stateFilter, setStateFilter] = useState("");
	const [costFilter, setCostFilter] = useState(18000);
	const [programOptions, setProgramOptions] = useState([]);
	const [programCatalogLoading, setProgramCatalogLoading] = useState(false);
	const [programCatalogError, setProgramCatalogError] = useState("");
	const [selectedProgram, setSelectedProgram] = useState("");
	const [selectedDegree, setSelectedDegree] = useState("");
	const [programMap, setProgramMap] = useState(new Map());
	const [programDegreeMap, setProgramDegreeMap] = useState(new Map());
	const [programDegreeLabelMap, setProgramDegreeLabelMap] = useState(new Map());
	const [programDegreeByUniversity, setProgramDegreeByUniversity] = useState(
		new Map()
	);
	const [crimeRateMap, setCrimeRateMap] = useState(new Map());
	const [compareSelection, setCompareSelection] = useState([]);
	const navigate = useNavigate();

	const fetchUniversities = async (overrides = {}) => {
		setLoading(true);
		try {
			const payload = await searchUniversities({
				search: overrides.search ?? searchTerm,
				state: overrides.state ?? stateFilter,
				perPage: 16,
			});
			const allowedOnly = (payload.data || []).filter((uni) =>
				allowedCampusesLower.has((uni.name || "").toLowerCase())
			);
			setUniversities(allowedOnly);
			setError("");
		} catch (err) {
			console.error(err);
			setError("Unable to load data from College Scorecard.");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		setProgramCatalogLoading(true);
		setProgramCatalogError("");
		listPrograms()
			.then((items) => {
				const programSet = new Set();
				const map = new Map();
				const degreeLookup = new Map();
				const degreeLabelLookup = new Map();
				const degreeByUniversity = new Map();
				const crimeLookup = new Map();
				items.forEach((entry) => {
					const uniName = entry.university || entry.campus || "";
					if (!allowedCampusesLower.has(uniName.toLowerCase())) return;
					if (entry.program) {
						programSet.add(entry.program);
						if (!map.has(entry.program)) {
							map.set(entry.program, new Set());
						}
						map.get(entry.program).add(uniName);

						const degreeNorm = normalizeDegree(entry.degree);
						if (degreeNorm) {
							if (!degreeLookup.has(entry.program)) {
								degreeLookup.set(entry.program, new Map());
								degreeLabelLookup.set(entry.program, new Map());
							}
							const degreeMapForProgram = degreeLookup.get(entry.program);
							const degreeLabelMapForProgram = degreeLabelLookup.get(
								entry.program
							);
							if (!degreeMapForProgram.has(degreeNorm)) {
								degreeMapForProgram.set(degreeNorm, new Set());
								degreeLabelMapForProgram.set(
									degreeNorm,
									entry.degree || ""
								);
							}
							degreeMapForProgram.get(degreeNorm).add(uniName);
							degreeByUniversity.set(
								`${entry.program}::${uniName}`,
								entry.degree || ""
							);
						}

						const crimeValue = Number(
							entry.college_profile?.crime_rate_overall ??
							entry.crime_rate_overall ??
							entry.crime_rate_per_1000 ??
							entry.crime_rate_value
						);
						if (!Number.isNaN(crimeValue) && !crimeLookup.has(uniName)) {
							crimeLookup.set(uniName, Number(crimeValue));
						}
					}
				});
				setProgramOptions(Array.from(programSet).sort());
				setProgramMap(map);
				setProgramDegreeMap(degreeLookup);
				setProgramDegreeLabelMap(degreeLabelLookup);
				setProgramDegreeByUniversity(degreeByUniversity);
				setCrimeRateMap(crimeLookup);
				setProgramCatalogLoading(false);
			})
			.catch((err) => {
				console.error("Unable to load program list", err);
				setProgramOptions([]);
				setProgramCatalogError("Unable to load academic catalog filters.");
				setProgramCatalogLoading(false);
			});
	}, []);

	useEffect(() => {
		const savedProgram = loadStorage("SelectedProgram", "");
		const persistentProgram = loadStorage("Programname", "");
		const savedDegree =
			loadStorage("SelectedDegreeLevel", "") || loadStorage("ProgramDegree", "");

		if (programOptions.length === 0) {
			const fallbackProgram = savedProgram || persistentProgram || "";
			if (fallbackProgram) {
				setSelectedProgram(fallbackProgram);
				setSelectedDegree(savedDegree || "");
			}
			setStateFilter("NM");
			fetchUniversities({ state: "NM" });
			return;
		}

		if (savedProgram && programOptions.includes(savedProgram)) {
			setSelectedProgram(savedProgram);
			setSelectedDegree(savedDegree || "");
			// Save to Programname for persistence and keep SelectedProgram so selections are preserved when navigating back
			saveStorage("Programname", savedProgram);
		} else if (persistentProgram && programOptions.includes(persistentProgram)) {
			// Use persisted program when available and valid
			setSelectedProgram(persistentProgram);
			setSelectedDegree(savedDegree || "");
		} else {
			// No valid program was provided (neither temporary nor persistent).
			setSelectedProgram("");
			setSelectedDegree("");
		}
		setStateFilter("NM");
		fetchUniversities({ state: "NM" });
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [programOptions]);

	const degreeOptionsForProgram = useMemo(() => {
		if (!programDegreeLabelMap.size) return [];
		if (selectedProgram) {
			const mapForProgram = programDegreeLabelMap.get(selectedProgram);
			if (!mapForProgram) return [];
			return Array.from(mapForProgram.values())
				.filter(Boolean)
				.sort((a, b) => a.localeCompare(b));
		}
		const seen = new Set();
		const all = [];
		programDegreeLabelMap.forEach((map) => {
			map.forEach((label) => {
				if (!label || seen.has(label)) return;
				seen.add(label);
				all.push(label);
			});
		});
		return all.sort((a, b) => a.localeCompare(b));
	}, [programDegreeLabelMap, selectedProgram]);

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
			setCompareSelection([]);
		}
	}, []);

	const filteredUniversities = useMemo(() => {
		const degreeNorm = normalizeDegree(selectedDegree);
		const degreeSetForProgram = selectedProgram
			? programDegreeMap.get(selectedProgram)
			: null;
		if (selectedProgram && degreeNorm && degreeSetForProgram && !degreeSetForProgram.has(degreeNorm)) {
			// Program selected with a degree that isn't offered by any university in the catalog
			return [];
		}

		return universities
			.filter((university) => {
				const matchesProgram =
					!selectedProgram ||
					programMap.get(selectedProgram)?.has(university.name) ||
					false;

				const matchesDegree =
					!selectedProgram ||
					!degreeNorm ||
					(degreeSetForProgram
						?.get(degreeNorm)
						?.has(university.name) ?? false);

				const matchesCost =
					!university.average_annual_cost ||
					Number(university.average_annual_cost || 0) <= Number(costFilter);

				return matchesCost && matchesProgram && matchesDegree;
			})
			.sort((a, b) => {
				const target = "northern new mexico college";

				const aIsTarget = a.name?.toLowerCase() === target;
				const bIsTarget = b.name?.toLowerCase() === target;

				if (aIsTarget && !bIsTarget) return -1;
				if (!aIsTarget && bIsTarget) return 1;
				return 0;
			});
	}, [universities, costFilter, selectedProgram, selectedDegree, programMap, programDegreeMap]);


	const handleSelect = (university) => {
		const programToSave = selectedProgram || university.program || "";
		const degreeKey = `${programToSave}::${university.name}`;
		const degreeValue =
			selectedDegree ||
			programDegreeByUniversity.get(degreeKey) ||
			"";
		saveStorage("University", university.name);
		saveStorage("UniversityUnitId", university.unit_id);
		saveStorage("UniversityState", university.state);
		saveStorage("Programname", programToSave || university.name);
		saveStorage("Programnameview", programToSave || university.name);
		saveStorage("universityview", university.name);
		saveStorage("ProgramDegree", degreeValue);
		saveStorage("SelectedDegreeLevel", degreeValue);
		saveStorage("selectedComponent", "program");
		// Ensure downstream pages know the chosen program/degree pairing
		saveStorage("Programname", programToSave);
		if (onSelectProgram) {
			onSelectProgram(university);
		}
	};

	const handleToggleCompare = (university) => {
		setCompareSelection((prev) => {
			const exists = prev.find((entry) => entry.unit_id === university.unit_id);
			if (exists) {
				const next = prev.filter((entry) => entry.unit_id !== university.unit_id);
				saveStorage("CompareQueue", next);
				toast.success("Removed from the Comparison list!");
				return next;
			}
			if (prev.length >= 3) {
				toast.error("You can only compare upto 3 universities at a time.");
				return prev;
			}
			const next = [...prev, university];
			saveStorage("CompareQueue", next);
			toast.success("Added to the Comparison list!");
			return next;
		});
	};

	const handleCompareNow = () => {
		const latestQueue = loadStorage("CompareQueue", compareSelection);
		const queue = Array.isArray(latestQueue) ? latestQueue : compareSelection;
		if (queue.length === 0) return;
		saveStorage("CompareQueue", queue.slice(0, 3));
		navigate("/compare");
	};

	const handleSearch = (event) => {
		event.preventDefault();
		fetchUniversities({ search: searchTerm, state: stateFilter });
	};

	const handleViewDetails = (university) => {
		if (!university?.unit_id) {
			toast.error("College details unavailable for this entry.");
			return;
		}
		saveStorage("LastCollegeDetail", university);
		navigate(`/college/${university.unit_id}`, { state: { college: university } });
	};

	return (
		<section className="space-y-4">
			<header className="flex flex-col gap-4">
			    <h1 className="text-3xl font-semibold text-slate-900">Explore <span className="text-[#0069e0]">Colleges</span> & <span className="text-[#0069e0]">Universities</span></h1>
				<form
					onSubmit={handleSearch}
					className="flex flex-col md:flex-row gap-3"
				>
					<input
						value={searchTerm}
						onChange={(event) => setSearchTerm(event.target.value)}
						className="px-4 py-2 rounded-lg border border-slate-200 md:w-[500px] text-center"
						placeholder="Search by University Name"
					/>
					{/* <select
						value={stateFilter}
						onChange={(event) => setStateFilter(event.target.value)}
						className="px-3 py-2 rounded-lg border border-slate-200 md:w-[400px]"
					>
						{stateOptions.map((state) => (
							<option key={state || "all"} value={state}>
								{state ? state : "All states"}
							</option>
						))}
					</select> */}
					<select
						value={selectedProgram}
						onChange={(event) => {
							const nextProgram = event.target.value;
							setSelectedProgram(nextProgram);
							saveStorage("Programname", nextProgram);
							// Preserve degree only if the new program offers it; otherwise clear.
							const degreeNorm = normalizeDegree(selectedDegree);
							const degreeSet = programDegreeMap.get(nextProgram);
							const canKeep =
								degreeNorm && degreeSet && degreeSet.has(degreeNorm);
							if (!canKeep) {
								setSelectedDegree("");
								saveStorage("ProgramDegree", "");
								saveStorage("SelectedDegreeLevel", "");
							}
						}}
						className="px-3 py-2 rounded-lg border border-slate-200 md:w-[400px]"
					>
						<option value="">All programs</option>
						{programOptions.map((program) => (
							<option key={program} value={program}>
								{program}
							</option>
						))}
					</select>
					<select
						value={selectedDegree}
						onChange={(event) => {
							const nextDegree = event.target.value;
							setSelectedDegree(nextDegree);
							saveStorage("ProgramDegree", nextDegree);
							saveStorage("SelectedDegreeLevel", nextDegree);
						}}
						className="px-3 py-2 rounded-lg border border-slate-200 md:w-[400px]"
					>
						<option value="">All degrees</option>
						{degreeOptionsForProgram.map((degree) => (
							<option key={degree} value={degree}>
								{degree}
							</option>
						))}
					</select>
					<button
						type="button"
						onClick={handleCompareNow}
						className={`px-4 py-2 rounded-lg font-medium md:w-[300px]
							${
								compareSelection.length < 2
								? "bg-gray-400 text-gray-700 cursor-not-allowed opacity-60"
								: "bg-[#016ce6] hover:bg-[#1977e3] text-white"
							}
  						`}
						disabled={compareSelection.length < 2}
					>
						Compare Now
					</button>
				</form>
			</header>

			<div className="flex items-center gap-6 w-full flex-nowrap">
				<label className="flex flex-col gap-1 w-44 text-sm text-slate-600 font-semibold">
					Max. Annual Cost
					<input
						type="range"
						min="1000"
						max="30000"
						step="1000"
						value={costFilter}
						onChange={(event) => setCostFilter(Number(event.target.value))}
						className="accent-indigo-600"
					/>
					<span className="text-xs text-slate-500">
						${costFilter.toLocaleString()}
					</span>
				</label>

				<div className="flex items-center gap-2 flex-nowrap">
					{compareSelection.length > 0 &&
						compareSelection.map((entry) => (
							<span
								key={entry.unit_id}
								className="inline-flex items-center gap-3 px-3 py-1 rounded-full bg-indigo-100 text-indigo-700"
							>
								{entry.name}
								<button
									onClick={() => handleToggleCompare(entry)}
									className="text-indigo-500 hover:text-indigo-700"
								>
									x
								</button>
							</span>
						))
					}
				</div>
			</div>

			{error && (
				<div className="bg-rose-50 text-rose-700 border border-rose-100 rounded-lg px-4 py-3">
					{error}
				</div>
			)}
			{programCatalogLoading && (
				<div className="bg-blue-50 text-blue-700 border border-blue-100 rounded-lg px-4 py-3">
					Loading academic catalog filters...
				</div>
			)}
			{programCatalogError && (
				<div className="bg-amber-50 text-amber-700 border border-amber-100 rounded-lg px-4 py-3">
					{programCatalogError}
				</div>
			)}

			{loading ? (
				<div className="text-center font-semibold text-slate-500">Loading Colleges…</div>
			) : (
				<div className="grid gap-4 md:grid-cols-2">
					{filteredUniversities.map((university) => {
						const websiteUrl = university.website
							? university.website.startsWith("http")
								? university.website
								: `https://${university.website}`
							: null;
						const crimeRateValue =
							crimeRateMap.get(university.name) ??
							university.college_profile?.crime_rate_overall ??
							university.crime_rate_overall ??
							university.crime_rate ??
							2.5;
						return (
							<article
								key={university.unit_id}
								className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 flex flex-col gap-3 hover:shadow-lg transition"
							>
								<div className="flex items-start justify-between gap-3">
									<div>
										<h3 className="text-xl font-semibold text-slate-900">
											{university.name}
										</h3>
										<p className="text-sm text-slate-500">
											{university.city}, {university.state} ·{" "}
											{university.organization_type}
										</p>
									</div>
									<span className="text-xs font-medium text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">
										{university.location_type}
									</span>
								</div>
								<ul className="text-sm text-slate-600 space-y-2">
									<li>
										<span className="font-semibold">Size:{" "}</span>
										{university.size ? university.size.toLocaleString() : "N/A"}{" "}
										students
									</li>
									<li>
										<span className="font-semibold">Graduation Rate:{" "}</span>
										{university.graduation_rate
											? `${Math.round(university.graduation_rate * 100)}%`
											: "N/A"}
									</li>
									<li>
										<span className="font-semibold">Acceptance Rate:{" "}</span>
										{university.acceptance_rate ? formatPercent(university.acceptance_rate): "100%"}
									</li>
									<li>
										<span className="font-semibold">Average Annual Cost:{" "}</span>
										{university.average_annual_cost
											? `$${Number(
													university.average_annual_cost
											  ).toLocaleString()}`
											: "N/A"}
									</li>
									<li>
										<span className="font-semibold">Median Earnings After Graduation: </span>
										{formatCurrency(university.typical_earnings)}
									</li>
									<li>
										<span className="font-semibold">Median Total Debt of Student After Graduation:{" "}</span>
										{formatCurrency(university.financial_aid_debt) ||
										"Data unavailable"}
									</li>
									<li>
										<span className="font-semibold">Crime Rate:{" "}</span>
										{crimeRateValue
											? `About ${Number(crimeRateValue).toFixed(1)} incidents per 1,000 students`
											: "About 2.5 incidents per 1,000 students"}
									</li>
								</ul>
								{websiteUrl && (
									<a
										href={websiteUrl}
										target="_blank"
										rel="noreferrer"
										className="text-sm text-indigo-600 hover:text-indigo-500"
									>
										Visit Website
									</a>
								)}
								<div className="flex gap-4">
									<button
										type="button"
										onClick={() => {
											handleSelect(university);
											navigate("/educationplan");
										}}
										className="self-start px-4 py-2 rounded-lg bg-[#281ed5] hover:bg-[#1977e3] text-white text-sm font-medium"
									>
										Create Education Plan
									</button>
									<button
										type="button"
										onClick={() => handleViewDetails(university)}
										className="text-sm font-medium text-indigo-700 hover:text-indigo-600 bg-indigo-100 hover:opacity-90 px-3 py-1 rounded-lg"
									>
										View Details
									</button>
									<button
										type="button"
										onClick={() => handleToggleCompare(university)}
										className="text-sm font-medium text-indigo-700 hover:text-indigo-600 bg-indigo-100 hover:opacity-90 px-3 py-1 rounded-lg"
									>
										{compareSelection.some((entry) => entry.unit_id === university.unit_id)
											? "Remove"
											: "Add to Compare"}
									</button>
								</div>
							</article>
						);
					})}
					{filteredUniversities.length === 0 && (
						<div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 text-sm text-slate-500">
							No Colleges/Universities found for the selected Program and Degree.
						</div>
					)}
				</div>
			)}
		</section>
	);
};

export default FindUniversity;
