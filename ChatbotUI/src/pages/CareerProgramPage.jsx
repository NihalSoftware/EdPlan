import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { save as saveStorage } from "../utils/storage.js";
import { getCareers } from "../services/catalogService.js";
import { listPrograms } from "../services/educationPlanService.js";
import { LuArrowRight, LuChevronRight, LuCar, LuWrench, LuGraduationCap, LuBriefcaseBusiness, LuBadgeDollarSign, LuLightbulb, LuBookOpen, LuSettings2, LuMapPin, LuCheck } from "react-icons/lu";
import "./CareerProgramPage.css";

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
	const [selectedDegree, setSelectedDegree] = useState("Associate");
	const [selectedProgram, setSelectedProgram] = useState("Automotive Technology");
	const [careerIndex, setCareerIndex] = useState(0);
	const [showAllCareers, setShowAllCareers] = useState(false);
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
		if (loading || !selectedDegree) return;
		const isValid = degreeOptionsForProgram.some(
			(degree) => degree.name === selectedDegree
		);
		if (!isValid) {
			setSelectedDegree("");
		}
	}, [loading, selectedDegree, degreeOptionsForProgram]);

	const selectedProgramObj =
		selectedProgram && selectedDegree
			? programsForDegree.find((program) => program.name === selectedProgram) || null
			: null;

	const careers = selectedProgramObj?.careers || [];
	const activeCareer = careers[careerIndex] || careers[0];
	const visibleCareers = showAllCareers ? careers : careers.slice(0, 5);
	const activeEmployers = employers?.[selectedDegree]?.[activeCareer?.title] || [];
	const competencies = (activeCareer?.competencies || []).map((item) =>
		typeof item === "string"
			? { topic: item, description: data?.competencies?.[item] || "" }
			: { topic: item.topic || item.name, description: item.description || "" }
	);
	const resetCareer = () => { setCareerIndex(0); setShowAllCareers(false); };

	return (
		<div className="career-explorer">
			<header className="career-hero">
				<div className="career-hero-copy">
					<span className="career-eyebrow">YOUR NEXT CHAPTER STARTS HERE</span>
					<h1>Explore Careers<br />and Programs that Fit You</h1>
					<p>Your interests + our insights = a brighter future.</p>
				</div>
			</header>
			<div className="career-content">
				<section className="career-selection-bar" aria-label="Choose your program and degree">
					<div className="career-field">
						<span className="career-field-icon"><LuSettings2 aria-hidden="true" /></span>
						<div><label htmlFor="career-program">Program</label>
						<select id="career-program" value={selectedProgram} disabled={loading} onChange={(event) => { setSelectedProgram(event.target.value); resetCareer(); }}>
							<option value="">Choose your program</option>
							{allPrograms.map((program) => <option key={program.name} value={program.name}>{program.name}</option>)}
						</select></div>
					</div>
					<div className="career-field">
						<span className="career-field-icon"><LuGraduationCap aria-hidden="true" /></span>
						<div><label htmlFor="career-degree">Degree</label>
						<select id="career-degree" value={selectedDegree} disabled={loading} onChange={(event) => { setSelectedDegree(event.target.value); resetCareer(); }}>
							<option value="">Choose your degree</option>
							{degreeOptionsForProgram.map((degree) => <option key={degree.name} value={degree.name}>{degree.name}</option>)}
						</select></div>
					</div>
					<Link to="/intake" className="career-next" onClick={() => {
						if (selectedProgram) saveStorage("SelectedProgram", selectedProgram);
						if (selectedDegree) saveStorage("SelectedDegreeLevel", selectedDegree);
					}}>Continue <LuArrowRight aria-hidden="true" /></Link>
				</section>

				{loading ? <div className="career-message" role="status">Loading your career possibilities…</div>
					: error ? <div className="career-message career-error" role="alert">{error}</div>
					: !selectedProgramObj ? <div className="career-message">Choose a program and degree to explore your career possibilities.</div>
					: <>
						<div className="career-main-grid">
							<section className="career-options" aria-labelledby="career-options-heading">
								<div className="career-section-heading"><div><h2 id="career-options-heading">Career Options</h2><p>Find the possibilities your program can open for you.</p></div><span>{careers.length} careers</span></div>
								<ul className="career-option-list">
									{visibleCareers.map((career, index) => <li key={career.title + index}>
										<button type="button" className={activeCareer === career ? "career-option is-selected" : "career-option"} aria-pressed={activeCareer === career} onClick={() => setCareerIndex(index)}>
											<span className={"career-option-icon tone-" + index % 4}>{/automotive|tire|vehicle|body/i.test(career.title) ? <LuCar aria-hidden="true" /> : <LuBriefcaseBusiness aria-hidden="true" />}</span>
											<span className="career-option-copy"><strong>{career.title}</strong>{activeCareer === career && <span className="career-selected-salary"><LuBadgeDollarSign aria-hidden="true" /><span><b>{career.salary}</b><small>Salary range</small></span></span>}</span>
											{activeCareer !== career && <span className="career-salary">{career.salary}</span>}
											<LuChevronRight className="career-row-arrow" aria-hidden="true" />
										</button>
									</li>)}
								</ul>
								{careers.length > 5 && <button type="button" className="career-show-all" onClick={() => setShowAllCareers(!showAllCareers)}>{showAllCareers ? "Show fewer careers" : "View all " + careers.length + " careers"}<LuArrowRight aria-hidden="true" /></button>}
								{!careers.length && <p className="career-message">Career details for this program are coming soon.</p>}
							</section>

							<aside className="career-snapshot" aria-labelledby="snapshot-heading">
								<h2 id="snapshot-heading"><span className="career-small-icon"><LuBookOpen aria-hidden="true" /></span>Program Snapshot</h2>
								<dl>
									<div><span className="career-small-icon"><LuWrench aria-hidden="true" /></span><div><dt>Program</dt><dd>{selectedProgram}</dd></div></div>
									<div><span className="career-small-icon"><LuGraduationCap aria-hidden="true" /></span><div><dt>Degree level</dt><dd>{selectedDegree}</dd></div></div>
									{activeCareer && <div><span className="career-small-icon"><LuBadgeDollarSign aria-hidden="true" /></span><div><dt>Salary range</dt><dd>{activeCareer.salary}</dd></div></div>}
									<div><span className="career-small-icon"><LuBriefcaseBusiness aria-hidden="true" /></span><div><dt>About this program</dt><dd className="career-summary">{selectedProgramObj.description}</dd></div></div>
								</dl>
								<div className="career-inspiration"><LuLightbulb aria-hidden="true" /><span>Dream It. Plan It. Do It.</span></div>
							</aside>
						</div>

						<div className="career-detail-grid" aria-live="polite">
							<section className="career-employers" aria-labelledby="employers-heading">
								<h2 id="employers-heading">Top Employers</h2><p>Explore employers connected to this career.</p>
								{activeEmployers.length ? <ul>{activeEmployers.map((employer) => <li key={employer}><LuBriefcaseBusiness aria-hidden="true" /><span>{employer}</span></li>)}</ul> : <p className="career-no-details">Employer information is not available for this career yet.</p>}
							</section>
							<section className="career-competencies" aria-labelledby="competencies-heading">
								<div className="career-section-heading"><h2 id="competencies-heading">Key Competencies</h2><span><LuMapPin aria-hidden="true" />New Mexico</span></div>
								<p>Skills you’ll build for {activeCareer?.title || selectedProgram}.</p>
								{competencies.length ? <ul>{competencies.map((competency, index) => <li key={competency.topic + index}><span><LuCheck aria-hidden="true" />{competency.topic}</span>{competency.description && <p>{competency.description}</p>}</li>)}</ul> : <p className="career-no-details">Competency information is not available for this career yet.</p>}
							</section>
						</div>
					</>}
			</div>
		</div>
	);
};

export default CareerProgramPage;
