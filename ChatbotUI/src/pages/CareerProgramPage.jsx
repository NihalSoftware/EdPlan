import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { save as saveStorage } from "../utils/storage.js";
import { getCareers } from "../services/catalogService.js";
import { listPrograms } from "../services/educationPlanService.js";

const CAREER_CATALOG_URL = "/assets/career_program_data.json";
const CAREER_EMPLOYERS_URL = "/assets/career_employers.json";

const fetchJson = async (url) => {
	const response = await fetch(url);
	if (!response.ok) {
		throw new Error(`Unable to load ${url}`);
	}
	return response.json();
};

const loadStaticCareerCatalog = async () => {
	const [catalog, employers] = await Promise.all([
		fetchJson(CAREER_CATALOG_URL),
		fetchJson(CAREER_EMPLOYERS_URL).catch(() => ({})),
	]);

	if (!catalog || !Array.isArray(catalog.degrees)) {
		throw new Error("Unexpected career catalog response");
	}

	return {
		data: {
			degrees: catalog.degrees,
			competencies: catalog.competencies || {},
		},
		employers: employers || {},
	};
};

const normalizeDegreeName = (value = "") => {
	const normalized = String(value).trim().toLowerCase();
	if (normalized.includes("certificate")) return "Certificate";
	if (normalized.includes("associate")) return "Associate";
	if (normalized.includes("bachelor")) return "Bachelors";
	if (normalized.includes("master")) return "Masters";
	return value || "Unspecified";
};

const salaryLabel = (value) =>
	value || value === 0 ? `$${Number(value).toLocaleString()}` : "N/A";

const buildCareerProgramData = (programs = [], careers = []) => {
	const careersForDisplay = careers.map((career) => ({
		title: career.career_name,
		salary: salaryLabel(career.average_salary),
		competencies: career.career_description
			? [
					{
						topic: career.industry,
						description: career.career_description,
					},
			  ]
			: [],
	}));
	const degreeMap = new Map();
	programs.forEach((program) => {
		const degreeName = normalizeDegreeName(program.degree);
		if (!degreeMap.has(degreeName)) {
			degreeMap.set(degreeName, { name: degreeName, programs: [] });
		}
		degreeMap.get(degreeName).programs.push({
			name: program.program,
			description:
				program.description || `${program.program} at ${program.university}`,
			careers: careersForDisplay,
		});
	});
	return {
		degrees: Array.from(degreeMap.values()).map((degree) => ({
			...degree,
			programs: Array.from(
				new Map(degree.programs.map((program) => [program.name, program])).values()
			),
		})),
		competencies: {},
	};
};

const CareerProgramPage = () => {
	const [data, setData] = useState(null);
	const [selectedDegree, setSelectedDegree] = useState("");
	const [selectedProgram, setSelectedProgram] = useState("");
	const [notAvailable, setNotAvailable] = useState("");
	const [employers, setEmployers] = useState({});
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	useEffect(() => {
		const loadCatalogCareers = async () => {
			setLoading(true);
			setError("");
			try {
				const staticCatalog = await loadStaticCareerCatalog();
				setData(staticCatalog.data);
				setEmployers(staticCatalog.employers);
			} catch (staticError) {
				try {
					const [programs, careers] = await Promise.all([
						listPrograms(),
						getCareers(),
					]);
					setData(buildCareerProgramData(programs, careers));
					setEmployers({});
				} catch (backendError) {
					console.error("Unable to load career catalog", {
						staticError,
						backendError,
					});
					setData({ degrees: [] });
					setEmployers({});
					setError("Unable to load career catalog.");
				}
			} finally {
				setLoading(false);
			}
		};
		loadCatalogCareers();
	}, []);

	const degreeOptions = useMemo(() => {
		if (!data?.degrees) return [];
		return [...data.degrees].sort((a, b) => a.name.localeCompare(b.name));
	}, [data]);

	const degreeOptionsForProgram = useMemo(() => {
		if (!selectedProgram) return degreeOptions;
		return degreeOptions.filter((degree) =>
			(degree.programs || []).some((program) => program.name === selectedProgram)
		);
	}, [degreeOptions, selectedProgram]);

	const allPrograms = useMemo(() => {
		if (!data?.degrees) return [];
		const map = new Map();
		data.degrees.forEach((degree) => {
			(degree.programs || []).forEach((program) => {
				if (!map.has(program.name)) map.set(program.name, program);
			});
		});
		return [...map.values()].sort((a, b) => a.name.localeCompare(b.name));
	}, [data]);

	const programsForDegree = useMemo(() => {
		const degreeObj = degreeOptions.find((degree) => degree.name === selectedDegree);
		return (
			degreeObj?.programs
				?.slice()
				.sort((a, b) => a.name.localeCompare(b.name)) || []
		);
	}, [selectedDegree, degreeOptions]);

	useEffect(() => {
		if (!selectedDegree) return;
		const isValid = degreeOptionsForProgram.some(
			(degree) => degree.name === selectedDegree
		);
		if (!isValid) {
			setSelectedDegree("");
		}
	}, [selectedDegree, degreeOptionsForProgram]);

	useEffect(() => {
		if (!selectedProgram || !selectedDegree) {
			setNotAvailable("");
			return;
		}

		const match = programsForDegree.find((program) => program.name === selectedProgram);

		if (!match) {
			setNotAvailable(`${selectedProgram} is not available in ${selectedDegree}`);
		} else {
			setNotAvailable("");
		}
	}, [selectedProgram, selectedDegree, programsForDegree]);

	useEffect(() => {
		if (notAvailable) {
			toast.error(notAvailable);
		}
	}, [notAvailable]);

	const selectedProgramObj =
		selectedProgram && selectedDegree
			? programsForDegree.find((program) => program.name === selectedProgram) || null
			: null;

	const hasValidData = Boolean(selectedProgramObj);

	const getEmployersForCareer = (careerTitle) => {
		if (!careerTitle || !selectedDegree) return [];
		return employers?.[selectedDegree]?.[careerTitle] || [];
	};

	return (
		<div
			className="p-6 min-h-screen relative"
			style={
				hasValidData
					? {}
					: {
							backgroundImage: "url('/assets/bg.png')",
							backgroundSize: "cover",
							backgroundPosition: "center",
							backgroundAttachment: "fixed",
					  }
			}
		>
			{!hasValidData && (
				<div className="absolute inset-0 bg-white" style={{ opacity: 0.6 }} />
			)}
			<div className="relative z-10">
				<header>
					<h1 className="text-[40px] -mt-2 font-semibold">
						Discover <span className="text-[#0069e0]">Careers</span> and{" "}
						<span className="text-[#0069e0]">Programs</span> that fit you
					</h1>
					<p className="text-[20px] font-medium text-slate-600 mb-5">
						Connect your program to real careers and the competencies you need.
					</p>
				</header>
				{loading && (
					<div className="mb-5 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-700">
						Loading catalog...
					</div>
				)}
				{error && (
					<div className="mb-5 rounded-lg border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">
						{error}
					</div>
				)}

				<div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
					<div>
						<label className="block font-medium mb-1">Program</label>
						<select
							className="w-full border rounded-md p-2"
							value={selectedProgram}
							onChange={(event) => setSelectedProgram(event.target.value)}
						>
							<option value="">Choose Your Program</option>
							{allPrograms.map((program) => (
								<option key={program.name} value={program.name}>
									{program.name}
								</option>
							))}
						</select>
					</div>

					<div>
						<label className="block font-medium mb-1">Degree</label>
						<select
							className="w-full border rounded-md p-2"
							value={selectedDegree}
							onChange={(event) => setSelectedDegree(event.target.value)}
						>
							<option value="">Choose Your Degree</option>
							{degreeOptionsForProgram.map((degree) => (
								<option key={degree.name} value={degree.name}>
									{degree.name}
								</option>
							))}
						</select>
					</div>

					<Link
						to="/intake"
						onClick={() => {
							if (selectedProgram) {
								saveStorage("SelectedProgram", selectedProgram);
							}
							if (selectedDegree) {
								saveStorage("SelectedDegreeLevel", selectedDegree);
							}
						}}
						className="px-4 mt-7 py-2 rounded-lg text-center h-fit bg-[#281ed5] hover:bg-[#1977e3] text-white font-medium md:w-[200px]"
					>
						Continue
					</Link>

					<div className="md:col-span-3">
						{selectedProgramObj && (
							<div className="mt-4">
								<h3 className="text-xl font-medium">Program Summary</h3>
								<p className="text-slate-600 text-lg mb-2">
									{selectedProgramObj.description}
								</p>
							</div>
						)}
					</div>
				</div>

				<section>
					{selectedProgramObj && selectedProgramObj.careers.length > 0 && (
						<div>
							<h3 className="text-xl font-semibold mb-3">Career Options</h3>

							<ul className="space-y-12">
								{selectedProgramObj.careers.map((career, careerIndex) => (
									<li
										key={career.title + careerIndex}
										className="border border-slate-300 rounded-md p-4 hover:shadow-xl transition"
									>
										<div className="flex items-center text-lg gap-14">
											<strong className="text-[#0069e0] w-72">
												{career.title}
											</strong>
											<span className="font-bold text-green-700">
												Salary Range: {career.salary}
											</span>
										</div>

										{getEmployersForCareer(career.title).length > 0 && (
											<div className="mt-3 text-sm">
												<p className="text-base font-semibold text-slate-700">
													Top employers for this career:
												</p>
												<ul className="mt-1 grid grid-cols-1 md:grid-cols-5 gap-2">
													{getEmployersForCareer(career.title).map((employer) => (
														<li
															key={employer}
															className="px-3 py-2 text-base font-medium rounded-2xl border border-slate-200 bg-indigo-50 text-slate-700 hover:shadow-md transition"
														>
															{employer}
														</li>
													))}
												</ul>
											</div>
										)}

										{career.competencies && career.competencies.length > 0 && (
											<div className="mt-8">
												<p className="text-base font-semibold text-slate-700 mb-3">
													Key Competencies acquired by the students upon
													completion of this program:
												</p>

												<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
													{career.competencies.map((competency, competencyIndex) => {
														let topic = "";
														let description = "";

														if (typeof competency === "string") {
															topic = competency;
															description = data.competencies?.[competency] || "";
														} else if (competency && typeof competency === "object") {
															topic = competency.topic || competency.name || "";
															description =
																competency.description ||
																data.competencies?.[topic] ||
																"";
														}

														return (
															<div
																key={topic + competencyIndex}
																className="flex gap-3 text-base p-3 bg-indigo-50 rounded-md border-l-4 border-indigo-400 hover:shadow-md transition"
															>
																<div>
																	<strong className="text-indigo-700">
																		{topic}:
																	</strong>
																	<p className="text-slate-600 mt-1">{description}</p>
																</div>
															</div>
														);
													})}
												</div>
											</div>
										)}
									</li>
								))}
							</ul>
						</div>
					)}
				</section>
			</div>
		</div>
	);
};

export default CareerProgramPage;
