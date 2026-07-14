import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
	FaChevronDown,
	FaChevronUp,
	FaPlus,
	FaTrash,
} from "react-icons/fa";
import { addEducationPlan } from "../../services/authService.js";
import {
	getProgramWithCourses,
	listPrograms,
} from "../../services/educationPlanService.js";
import {
	load as loadStorage,
	save as saveStorage,
} from "../../utils/storage.js";
import toast from "react-hot-toast";

const LOCAL_PLAN_KEY = "LocalSavedPlans";
const MIN_SEMESTER_CREDITS = 6;
const MAX_SEMESTER_CREDITS = 20;
const MAX_SEMESTERS = 10;
const normalizeRequirement = (value) => (value || "").trim();
const normalizeDegree = (value = "") => {
	const raw = String(value || "").trim().toLowerCase();
	if (!raw) return "";
	if (raw.includes("certificate")) return "certificate";
	if (raw.includes("associate")) return "associate";
	if (raw.includes("bachelor")) return "bachelor";
	if (raw.includes("master")) return "master";
	return raw;
};
const hasMeaningfulRequirement = (value) => {
	const normalized = normalizeRequirement(value).toLowerCase();
	return normalized && normalized !== "none" && normalized !== "n/a";
};
const dedupeCourses = (list = []) =>
	Array.from(new Map((list || []).map((c) => [c.code, c])).values());
const YEAR_ORDER = [
	"First Year",
	"Second Year",
	"Third Year",
	"Fourth Year",
	"Fifth Year",
	"Sixth Year",
	"Seventh Year",
	"Eighth Year",
];
const SEMESTER_ORDER = ["Fall", "Spring", "Summer", "Winter"];
const UNIVERSITY_ALIASES = {
	"new mexico state university-main campus": "New Mexico State University",
	"university of new mexico-main campus": "University of New Mexico",
};

const normalizeUniversityName = (value = "") => {
	const cleaned = String(value || "").trim();
	return UNIVERSITY_ALIASES[cleaned.toLowerCase()] || cleaned;
};

const getYearRank = (year) => {
	if (!year) return Number.MAX_SAFE_INTEGER;
	const idx = YEAR_ORDER.findIndex(
		(label) => label.toLowerCase() === String(year).toLowerCase()
	);
	if (idx >= 0) return idx + 1;
	const parsed = parseInt(String(year).replace(/\D+/g, ""), 10);
	return Number.isFinite(parsed) ? parsed : Number.MAX_SAFE_INTEGER;
};

const getSemesterRank = (semester) => {
	if (!semester) return Number.MAX_SAFE_INTEGER;
	const idx = SEMESTER_ORDER.findIndex(
		(label) => label.toLowerCase() === String(semester).toLowerCase()
	);
	return idx >= 0 ? idx + 1 : Number.MAX_SAFE_INTEGER;
};

const isSameTerm = (a, b) =>
	normalizeRequirement(a.year) === normalizeRequirement(b.year) &&
	normalizeRequirement(a.semester) === normalizeRequirement(b.semester);

const isBefore = (a, b) => {
	const yearDiff = getYearRank(a.year) - getYearRank(b.year);
	if (yearDiff !== 0) return yearDiff < 0;
	return getSemesterRank(a.semester) < getSemesterRank(b.semester);
};

const buildCodeSet = (courses = []) =>
	new Set(
		(courses || [])
			.map((course) => course.code)
			.filter(Boolean)
			.map((code) => String(code).toUpperCase())
	);

const extractDependencyCodes = (text, knownCodes) => {
	if (!text || !knownCodes || knownCodes.size === 0) return [];
	const upper = String(text).toUpperCase();
	return Array.from(knownCodes).filter((code) => upper.includes(code));
};

const getDependencies = (course, knownCodes) => {
	const codeSet = knownCodes || new Set();
	return {
		prereqCodes: extractDependencyCodes(course.prerequisite, codeSet),
		coreqCodes: extractDependencyCodes(course.corequisite, codeSet),
	};
};

const formatSchedule = (schedule) => {
	if (!schedule) return "";
	if (typeof schedule === "string") return schedule;
	if (Array.isArray(schedule)) return schedule.filter(Boolean).join(" | ");
	if (typeof schedule === "object") {
		return Object.values(schedule).filter(Boolean).join(" | ");
	}
	return "";
};

const getCourseCredits = (course) => {
	const value = Number(course?.credits);
	return Number.isFinite(value) ? value : 0;
};

const validatePlan = (planCourses, knownCodes) => {
	const issues = [];
	(planCourses || []).forEach((course) => {
		const { prereqCodes, coreqCodes } = getDependencies(course, knownCodes);

		prereqCodes.forEach((code) => {
			const prereqCourse = planCourses.find((item) => item.code === code);
			if (!prereqCourse) {
				issues.push({
					courseCode: course.code,
					type: "prereq-missing",
					relatedCode: code,
					message: `${course.courseName} requires ${code} in a prior term.`,
					blocking: true,
				});
				return;
			}
			if (!isBefore(prereqCourse, course)) {
				issues.push({
					courseCode: course.code,
					type: "prereq-order",
					relatedCode: code,
					message: `${code} must be scheduled before ${course.courseName}.`,
					blocking: true,
				});
			}
		});

		coreqCodes.forEach((code) => {
			const coreqCourse = planCourses.find((item) => item.code === code);
			if (!coreqCourse) {
				issues.push({
					courseCode: course.code,
					type: "coreq-missing",
					relatedCode: code,
					message: `${course.courseName} requires co-requisite ${code} in the same term.`,
					blocking: true,
				});
				return;
			}
			if (!isSameTerm(coreqCourse, course)) {
				issues.push({
					courseCode: course.code,
					type: "coreq-term",
					relatedCode: code,
					message: `${code} must be taken in the same term as ${course.courseName}.`,
					blocking: true,
				});
			}
		});
	});
	return issues;
};

const EducationPlanEditor = () => {
	const [programs, setPrograms] = useState([]);
	const [selectedProgram, setSelectedProgram] = useState("");
	const selectedUniversity = normalizeUniversityName(loadStorage("University") || "");
	const [selectedDegree, setSelectedDegree] = useState("");
	const [courses, setCourses] = useState([]);
	const [availableCourses, setAvailableCourses] = useState([]);
	const [defaultPlan, setDefaultPlan] = useState([]);
	const [editingPlan, setEditingPlan] = useState(null);
	const [editApplied, setEditApplied] = useState(false);
	const [error, setError] = useState("");
	const [yearFilter, setYearFilter] = useState("");
	const [semesterFilter, setSemesterFilter] = useState("");
	const [dependencyIssues, setDependencyIssues] = useState([]);
	const [creditLimitModal, setCreditLimitModal] = useState(null);
	const [expandedTerms, setExpandedTerms] = useState({});
	const [planTerms, setPlanTerms] = useState([]);
	const [activeTermKey, setActiveTermKey] = useState("");
	const userEmail = loadStorage("UserEmail");
	const profile = loadStorage("UserProfile") || {};
	const navigate = useNavigate();

	useEffect(() => {
		listPrograms()
			.then((items) => setPrograms(items))
			.catch((err) => {
				console.error(err);
				setError("Unable to load program catalog.");
			});
		// Load program from storage on mount (keep university even if program is missing)
		const savedProgram = loadStorage("Programname", "");
		setSelectedProgram(savedProgram || "");
		const savedDegree =
			loadStorage("ProgramDegree", "") || loadStorage("SelectedDegreeLevel", "");
		if (savedDegree) {
			setSelectedDegree(savedDegree);
		}
		const storedEditingPlan = loadStorage("EditingPlan", null);
		const editingActive = loadStorage("EditingPlanActive", false);
		if (editingActive && storedEditingPlan) {
			setEditingPlan(storedEditingPlan);
		}
	}, []);

	// When no program is selected, clear available courses
	useEffect(() => {
		if (!selectedProgram) {
			setAvailableCourses([]);
		}
	}, [selectedProgram]);

	// Update availableCourses when a program + university is selected.
	useEffect(() => {
		let cancelled = false;

		const resetSelectedProgramData = () => {
			setAvailableCourses([]);
			setCourses([]);
			setDefaultPlan([]);
			setPlanTerms([]);
			setActiveTermKey("");
		};

		const loadSelectedProgramCourses = async () => {
			if (!selectedProgram || !selectedUniversity) {
				resetSelectedProgramData();
				return;
			}

			const selectedDegreeNorm = normalizeDegree(selectedDegree);
			let match = null;
			if (selectedDegreeNorm) {
				match = programs.find(
					(program) =>
						program.program === selectedProgram &&
						program.university === selectedUniversity &&
						normalizeDegree(program.degree) === selectedDegreeNorm
				);
			}
			if (!match) {
				match = programs.find(
					(program) =>
						program.program === selectedProgram &&
						program.university === selectedUniversity
				);
			}
			if (!match) {
				resetSelectedProgramData();
				return;
			}

			let hydratedMatch = match;
			const hasLoadedCourses = (match.years || []).some((entry) =>
				(entry.semesters || []).some((semester) => (semester.courses || []).length > 0)
			);

			if (!hasLoadedCourses && match.program_id) {
				try {
					hydratedMatch = await getProgramWithCourses(match.program_id);
					if (cancelled) return;
					if (!hydratedMatch) {
						resetSelectedProgramData();
						return;
					}
					setPrograms((prev) =>
						prev.map((program) =>
							program.program_id === hydratedMatch.program_id
								? { ...program, ...hydratedMatch }
								: program
						)
					);
				} catch (err) {
					console.error("Unable to load selected program courses", err);
					if (!cancelled) {
						setError("Unable to load program courses.");
						resetSelectedProgramData();
					}
					return;
				}
			}

			if (cancelled) return;
			const uniqueCourses =
				(hydratedMatch.years || []).flatMap((entry) =>
					(entry.semesters || []).flatMap((semester) =>
						(semester.courses || []).map((course) => ({
							recommended_year: course.recommended_year || entry.year,
							recommended_semester:
								course.recommended_semester || semester.semester,
							year: course.recommended_year || entry.year,
							semester: course.recommended_semester || semester.semester,
							code: course.code,
							name: course.name,
							credits: course.credits,
							is_elective: course.is_elective,
							default_plan_eligible: course.default_plan_eligible,
							prerequisite: course.prerequisite,
							corequisite: course.corequisite,
							schedule: course.schedule,
						}))
					)
				) || [];

			const cleanedCourses = dedupeCourses(uniqueCourses);
			setAvailableCourses(cleanedCourses);

			const builtDefaultPlan = dedupeCourses(
				cleanedCourses
					.filter((course) => course.default_plan_eligible)
					.map((course) => ({
						program: selectedProgram,
						university: selectedUniversity,
						year: course.year,
						semester: course.semester,
						courseName: course.name,
						code: course.code,
						credits: course.credits,
						prerequisite: course.prerequisite,
						corequisite: course.corequisite,
						schedule: course.schedule,
					}))
			);
			const defaultTerms = Array.from(
				new Map(
					builtDefaultPlan.map((course) => [
						`${course.year}::${course.semester}`,
						{
							key: `${course.year}::${course.semester}`,
							year: course.year,
							semester: course.semester,
						},
					])
				).values()
			)
				.sort((a, b) => {
					const yearDiff = getYearRank(a.year) - getYearRank(b.year);
					if (yearDiff !== 0) return yearDiff;
					return getSemesterRank(a.semester) - getSemesterRank(b.semester);
				})
				.slice(0, MAX_SEMESTERS);
			const defaultTermKeys = new Set(defaultTerms.map((term) => term.key));
			const placedDefaultPlan = builtDefaultPlan.filter((course) =>
				defaultTermKeys.has(`${course.year}::${course.semester}`)
			);
			setDefaultPlan(builtDefaultPlan);
			const degreeToUse = selectedDegree || hydratedMatch.degree || "";
			setSelectedDegree(degreeToUse);
			saveStorage("ProgramDegree", degreeToUse);

			const hasEditingCourses = Boolean(editingPlan?.courses?.length);
			const programMatch =
				String(editingPlan?.program || "").toLowerCase() ===
				String(selectedProgram || "").toLowerCase();
			const universityMatch =
				String(normalizeUniversityName(editingPlan?.university || "")).toLowerCase() ===
				String(selectedUniversity || "").toLowerCase();
			const degreeMatch =
				!editingPlan?.degree ||
				normalizeDegree(editingPlan.degree) === normalizeDegree(degreeToUse);
			const editingMatch =
				hasEditingCourses && programMatch && universityMatch && degreeMatch;

			if (editingMatch && !editApplied) {
				const editingCourses = dedupeCourses(editingPlan.courses);
				setCourses(editingCourses);
				const editingTerms = Array.from(
					new Map(
						editingCourses.map((course) => [
							`${course.year}::${course.semester}`,
							{
								key: `${course.year}::${course.semester}`,
								year: course.year,
								semester: course.semester,
							},
						])
					).values()
				);
				setPlanTerms(editingTerms);
				setActiveTermKey(editingTerms[0]?.key || "");
				setEditApplied(true);
				saveStorage("EditingPlanActive", false);
				return;
			}

			if (!editingMatch) {
				setEditApplied(false);
			}

			if (!editingMatch || !editApplied) {
				setCourses(placedDefaultPlan);
				setPlanTerms(defaultTerms);
				setActiveTermKey(defaultTerms[0]?.key || "");
				setExpandedTerms(
					Object.fromEntries(
						defaultTerms.map((term, index) => [term.key, index < 2])
					)
				);
			}
		};

		loadSelectedProgramCourses();

		return () => {
			cancelled = true;
		};
	}, [programs, selectedProgram, selectedDegree, selectedUniversity, editingPlan, editApplied]);

	const knownCodes = useMemo(
		() => buildCodeSet([...availableCourses, ...courses]),
		[availableCourses, courses]
	);

	useEffect(() => {
		setDependencyIssues(validatePlan(courses, knownCodes));
	}, [courses, knownCodes]);

	// Filter programs based on selected university
	const uniqueProgramOptions = useMemo(() => {
		const seen = new Set();
		let filteredPrograms = programs;

		// If university is selected, filter by that university
		if (selectedUniversity) {
			filteredPrograms = programs.filter(
				(program) => program.university === selectedUniversity
			);
		}

		// Remove duplicates
		return filteredPrograms.filter((program) => {
			const name = (program.program || "").trim().toLowerCase();
			if (!name || seen.has(name)) {
				return false;
			}
			seen.add(name);
			return true;
		});
	}, [programs, selectedUniversity]);

	// Clear selected program when university changes if the program is not available
	useEffect(() => {
		if (
			selectedProgram &&
			selectedUniversity &&
			uniqueProgramOptions.length > 0
		) {
			const programExists = uniqueProgramOptions.some(
				(p) => p.program === selectedProgram
			);
			if (!programExists) {
				setSelectedProgram("");
				saveStorage("Programname", "");
			}
		}
	}, [selectedUniversity, uniqueProgramOptions, selectedProgram]);

	const filteredPlanCourses = useMemo(() => {
		return courses.filter((course) => {
			const yearOk = yearFilter ? course.year === yearFilter : true;
			const semOk = semesterFilter ? course.semester === semesterFilter : true;
			return yearOk && semOk;
		});
	}, [courses, yearFilter, semesterFilter]);

	const groupedCourses = useMemo(() => {
		return filteredPlanCourses.reduce((acc, course) => {
			const key = `${course.year}::${course.semester}`;
			acc[key] = acc[key] || [];
			acc[key].push(course);
			return acc;
		}, {});
	}, [filteredPlanCourses]);

	const recommendedTerms = useMemo(() => {
		const terms = new Map();
		defaultPlan.forEach((course) => {
			const key = `${course.year}::${course.semester}`;
			if (!terms.has(key)) {
				terms.set(key, {
					key,
					year: course.year,
					semester: course.semester,
				});
			}
		});
		return Array.from(terms.values()).sort((a, b) => {
			const yearDiff = getYearRank(a.year) - getYearRank(b.year);
			if (yearDiff !== 0) return yearDiff;
			return getSemesterRank(a.semester) - getSemesterRank(b.semester);
		});
	}, [defaultPlan]);

	const groupedCourseEntries = useMemo(
		() => {
			const entries = new Map(
				planTerms.map((term) => [term.key, [term.key, groupedCourses[term.key] || []]])
			);
			Object.entries(groupedCourses).forEach(([key, list]) => {
				if (!entries.has(key)) entries.set(key, [key, list]);
			});
			return Array.from(entries.values()).sort(([a], [b]) => {
				const [yearA, semesterA] = a.split("::");
				const [yearB, semesterB] = b.split("::");
				const yearDiff = getYearRank(yearA) - getYearRank(yearB);
				if (yearDiff !== 0) return yearDiff;
				return getSemesterRank(semesterA) - getSemesterRank(semesterB);
			});
		},
		[groupedCourses, planTerms]
	);

	useEffect(() => {
		if (groupedCourseEntries.length === 0) {
			setExpandedTerms({});
			setActiveTermKey("");
			return;
		}
		setExpandedTerms((prev) => {
			const next = {};
			groupedCourseEntries.forEach(([key], index) => {
				next[key] = prev[key] ?? index < 2;
			});
			return next;
		});
		setActiveTermKey((prev) =>
			groupedCourseEntries.some(([key]) => key === prev)
				? prev
				: groupedCourseEntries[0][0]
		);
	}, [groupedCourseEntries]);

	const yearOptions = useMemo(
		() =>
			[...new Set(availableCourses.map((course) => course.year))].filter(
				Boolean
			),
		[availableCourses]
	);

	const selectedProgramMeta = useMemo(() => {
		if (!selectedProgram || !selectedUniversity) return null;
		const degreeNorm = normalizeDegree(selectedDegree);
		if (degreeNorm) {
			return (
				programs.find(
					(entry) =>
						entry.program === selectedProgram &&
						entry.university === selectedUniversity &&
						normalizeDegree(entry.degree) === degreeNorm
				) || null
			);
		}
		return (
			programs.find(
				(entry) =>
					entry.program === selectedProgram &&
					entry.university === selectedUniversity
			) || null
		);
	}, [programs, selectedProgram, selectedUniversity, selectedDegree]);

	const averageAnnualCost =
		selectedProgramMeta?.average_annual_cost ||
		selectedProgramMeta?.averageAnnualCost ||
		selectedProgramMeta?.college_profile?.average_annual_cost ||
		null;
	const eligibilityCriteria =
		selectedProgramMeta?.eligibility_criteria ||
		selectedProgramMeta?.eligibility ||
		selectedProgramMeta?.college_profile?.eligibility_criteria ||
		"";

	const programTotalCredits = selectedProgramMeta?.total_credit_hours ?? 0;

	// Filter courses to only show those not already in the plan
	const remainingCourses = useMemo(() => {
		const addedCourseCodes = new Set(courses.map((course) => course.code));
		return availableCourses.filter(
			(course) => !addedCourseCodes.has(course.code)
		);
	}, [availableCourses, courses]);

	const addSemester = () => {
		if (!selectedProgram || !selectedUniversity) {
			toast.error("Select a university and program first.");
			return;
		}
		if (planTerms.length >= MAX_SEMESTERS) {
			toast.error(`You can add a maximum of ${MAX_SEMESTERS} semesters.`);
			return;
		}
		const existing = new Set(planTerms.map((term) => term.key));
		const nextRecommended = recommendedTerms.find((term) => !existing.has(term.key));
		const fallbackIndex = planTerms.length + 1;
		const nextTerm =
			nextRecommended || {
				key: `Custom Year::Semester ${fallbackIndex}`,
				year: "Custom Year",
				semester: `Semester ${fallbackIndex}`,
			};

		setPlanTerms((prev) => {
			if (prev.some((term) => term.key === nextTerm.key)) return prev;
			return [...prev, nextTerm];
		});
		setActiveTermKey(nextTerm.key);
		setExpandedTerms((prev) => ({ ...prev, [nextTerm.key]: true }));
	};

	const deleteSemester = (term) => {
		const termCourses = courses.filter((course) => isSameTerm(course, term));
		const termLabel = `${term.year} - ${term.semester}`;

		if (
			termCourses.length > 0 &&
			!window.confirm(
				`Delete ${termLabel}? This will also remove ${termCourses.length} course${
					termCourses.length === 1 ? "" : "s"
				} from your plan.`
			)
		) {
			return;
		}

		setPlanTerms((prev) => prev.filter((entry) => entry.key !== term.key));
		setCourses((prev) => prev.filter((course) => !isSameTerm(course, term)));
		setExpandedTerms((prev) => {
			const next = { ...prev };
			delete next[term.key];
			return next;
		});
		setActiveTermKey((prev) => {
			if (prev !== term.key) return prev;
			return planTerms.find((entry) => entry.key !== term.key)?.key || "";
		});
		toast.success(`${termLabel} deleted.`);
	};

	const addCourse = (course) => {
		const activeTerm = planTerms.find((term) => term.key === activeTermKey);
		if (!activeTerm) {
			toast.error("Add a semester before adding subjects.");
			return;
		}
		setCourses((prev) => {
			const newEntry = {
				program: selectedProgram,
				university: selectedUniversity,
				year: activeTerm.year,
				semester: activeTerm.semester,
				courseName: course.name,
				code: course.code,
				credits: course.credits,
				prerequisite: course.prerequisite,
				corequisite: course.corequisite,
				schedule: course.schedule,
			};

			if (prev.some((item) => item.code === newEntry.code)) {
				toast.error("Course already in your plan.");
				return prev;
			}

			const currentTermCredits = prev
				.filter((item) => isSameTerm(item, newEntry))
				.reduce((sum, item) => sum + getCourseCredits(item), 0);
			const newCourseCredits = getCourseCredits(newEntry);

			if (currentTermCredits + newCourseCredits > MAX_SEMESTER_CREDITS) {
				setCreditLimitModal({
					courseName: newEntry.courseName,
					currentCredits: currentTermCredits,
					addingCredits: newCourseCredits,
					totalWouldBe: currentTermCredits + newCourseCredits,
					programLimit: MAX_SEMESTER_CREDITS,
					termLabel: `${newEntry.year} - ${newEntry.semester}`,
				});
				return prev;
			}

			const { prereqCodes, coreqCodes } = getDependencies(newEntry, knownCodes);

			for (const prereqCode of prereqCodes) {
				const prereqCourse = prev.find((item) => item.code === prereqCode);
				if (!prereqCourse) {
					toast(
						`${newEntry.courseName} requires ${prereqCode} in a prior term. Add the pre-requisite first.`
					);
					return prev;
				}
				if (!isBefore(prereqCourse, newEntry)) {
					toast(
						`${prereqCode} must be scheduled before ${newEntry.courseName}. Move the pre-requisite to an earlier term.`
					);
					return prev;
				}
			}

			const missingCoreqs = [];
			for (const code of coreqCodes) {
				const match = prev.find((item) => item.code === code);
				if (!match) {
					missingCoreqs.push(code);
					continue;
				}
				if (!isSameTerm(match, newEntry)) {
					toast(
						`${code} must be scheduled in ${newEntry.year} - ${newEntry.semester} with ${newEntry.courseName}. Move the co-requisite to the same term.`
					);
					return prev;
				}
			}

			const extraCourses = [];
			if (missingCoreqs.length) {
				const candidates = missingCoreqs
					.map((code) =>
						availableCourses.find((item) => item.code === code)
					)
					.filter(Boolean);

				const canAutoAdd = candidates.length === missingCoreqs.length;
				const confirmText = `Missing co-requisite ${missingCoreqs.join(
					", "
				)}. Add it to ${newEntry.year} - ${newEntry.semester}?`;
				if (canAutoAdd) {
					const confirmAdd = window.confirm(confirmText);
					if (confirmAdd) {
						candidates.forEach((item) => {
							if (prev.some((existing) => existing.code === item.code)) {
								return;
							}
							extraCourses.push({
								program: selectedProgram,
								university: selectedUniversity,
								year: activeTerm.year,
								semester: activeTerm.semester,
								courseName: item.name,
								code: item.code,
								credits: item.credits,
								prerequisite: item.prerequisite,
								corequisite: item.corequisite,
								schedule: item.schedule,
							});
						});
					} else {
						toast(
							`Co-requisite ${missingCoreqs.join(", ")} must be taken with ${
								newEntry.courseName
							}.`
						);
						return prev;
					}
				} else {
				toast(
					`Co-requisite ${missingCoreqs.join(", ")} must be taken with ${
						newEntry.courseName
					} in the same term.`
				);
				return dedupeCourses(prev);
			}
		}

			if (extraCourses.length) {
				const addingCredits = [newEntry, ...extraCourses].reduce(
					(sum, item) => sum + getCourseCredits(item),
					0
				);

				if (currentTermCredits + addingCredits > MAX_SEMESTER_CREDITS) {
					setCreditLimitModal({
						courseName: newEntry.courseName,
						currentCredits: currentTermCredits,
						addingCredits,
						totalWouldBe: currentTermCredits + addingCredits,
						programLimit: MAX_SEMESTER_CREDITS,
						termLabel: `${newEntry.year} - ${newEntry.semester}`,
					});
					return prev;
				}
			}

			toast.success("Successfully Added");
			return dedupeCourses([...prev, newEntry, ...extraCourses]);
		});
	};

		const removeCourse = (code) => {
			setCourses((prev) => {
				const target = prev.find((course) => course.code === code);
				if (!target) return prev;

				const dependents = prev.filter((course) =>
					getDependencies(course, knownCodes).coreqCodes.includes(code)
				);
				const prereqDependents = prev.filter((course) =>
					getDependencies(course, knownCodes).prereqCodes.includes(code)
				);

				// Block removal when other courses depend on this one and show a single toast message.
				if (dependents.length > 0 || prereqDependents.length > 0) {
					const parts = [];
					
					if (dependents.length > 0) {
						parts.push(
							`${target.courseName} is tied to a co-requisite course.\n\n`
						);
					}
					if (prereqDependents.length > 0) {
						parts.push(
							`Can't Remove ${target.courseName} because it is a pre-requisite course.`
						);
					}
					toast.error(parts.join(" "));
					return prev;
				}

				// Safe to remove only the selected course
				toast.success("Successfully Removed");
				return dedupeCourses(prev.filter((course) => course.code !== code));
			});
		};

	const getSemesterCreditIssues = () =>
		planTerms
			.map((term) => {
				const termCourses = courses.filter(
					(course) =>
						normalizeRequirement(course.year) === normalizeRequirement(term.year) &&
						normalizeRequirement(course.semester) === normalizeRequirement(term.semester)
				);
				const credits = termCourses.reduce(
					(sum, course) => sum + getCourseCredits(course),
					0
				);
				return {
					...term,
					credits,
					hasCourses: termCourses.length > 0,
				};
			})
			.filter(
				(term) =>
					term.hasCourses &&
					(term.credits < MIN_SEMESTER_CREDITS ||
						term.credits > MAX_SEMESTER_CREDITS)
			);

	const savePlanLocally = () => {
		if (!selectedUniversity || !selectedProgram) {
			toast.error("Select a university and program before saving.");
			return;
		}
		if (dependencyIssues.some((issue) => issue.blocking)) {
			toast.error("Fix pre-requisite/co-requisite issues before saving.");
			return;
		}
		const semesterCreditIssues = getSemesterCreditIssues();
		if (semesterCreditIssues.length > 0) {
			const firstIssue = semesterCreditIssues[0];
			toast.error(
				`${firstIssue.semester} must have ${MIN_SEMESTER_CREDITS}-${MAX_SEMESTER_CREDITS} credits before saving. Current: ${firstIssue.credits}.`
			);
			return;
		}
		const stored = loadStorage(LOCAL_PLAN_KEY, []);
		const selectedDegreeNorm = normalizeDegree(selectedDegree);
		const filtered = stored.filter((entry) => {
			const sameUniversity = entry.university === selectedUniversity;
			const sameProgram = entry.program === selectedProgram;
			const entryDegreeNorm = normalizeDegree(entry.degree || "");
			const sameDegree = entryDegreeNorm === selectedDegreeNorm;
			return !(sameUniversity && sameProgram && sameDegree);
		});
		const updated = [
			...filtered,
			{
				program: selectedProgram,
				university: selectedUniversity,
				degree: selectedDegree,
				courses,
			},
		];
		saveStorage(LOCAL_PLAN_KEY, updated);
		saveStorage("EditingPlanActive", false);
		toast.success("Education plan saved.");
		navigate("/view");
	};

	const savePlan = async () => {
		if (!userEmail) {
			savePlanLocally();
			return;
		}
		if (dependencyIssues.some((issue) => issue.blocking)) {
			toast.error("Fix pre-requisite/co-requisite issues before saving.");
			return;
		}
		const semesterCreditIssues = getSemesterCreditIssues();
		if (semesterCreditIssues.length > 0) {
			const firstIssue = semesterCreditIssues[0];
			toast.error(
				`${firstIssue.semester} must have ${MIN_SEMESTER_CREDITS}-${MAX_SEMESTER_CREDITS} credits before saving. Current: ${firstIssue.credits}.`
			);
			return;
		}
		try {
			await addEducationPlan({
				email: userEmail,
				program: courses,
				degree: selectedDegree || "",
			});
			toast.success("Education plan saved.");
			saveStorage("EditingPlanActive", false);
			navigate("/view");
		} catch (err) {
			console.error(err);
			if (err.response?.status === 401) {
				toast.error("Your session has expired. Please login again.");
			} else {
				toast.error("Unable to save plan. Please try again later.");
			}
		}
	};

	// Program-level counts (static; do not change when user adds/removes)
	const prereqProgramCount = useMemo(
		() =>
			defaultPlan.filter((course) =>
				hasMeaningfulRequirement(course.prerequisite)
			).length,
		[defaultPlan]
	);
	const coreqProgramCount = useMemo(
		() =>
			defaultPlan.filter((course) =>
				hasMeaningfulRequirement(course.corequisite)
			).length,
		[defaultPlan]
	);
	// Live plan totals (only total courses should change as user edits)
	const totalCourses = useMemo(() => courses.length, [courses]);
	const totalCredits = useMemo(
		() =>
			courses.reduce((sum, course) => {
				const value = Number(course.credits);
				return sum + (Number.isFinite(value) ? value : 0);
			}, 0),
		[courses]
	);
	const defaultPlanCredits = useMemo(
		() =>
			defaultPlan.reduce((sum, course) => {
				const value = Number(course.credits);
				return sum + (Number.isFinite(value) ? value : 0);
			}, 0),
		[defaultPlan]
	);
	const requiredCredits = Number(programTotalCredits) || defaultPlanCredits || totalCredits || 0;
	const creditsProgressText = `${totalCredits}/${requiredCredits || "N/A"} credits`;
	const progressPercent =
		requiredCredits > 0 ? Math.min(100, Math.round((totalCredits / requiredCredits) * 100)) : 0;
	const studentName = "Jack";
	const studentInitials = studentName
		.split(" ")
		.filter(Boolean)
		.slice(0, 2)
		.map((part) => part[0]?.toUpperCase())
		.join("") || "J";
	const studentId =
		profile.student_id || profile.studentId || profile.id || userEmail || "Local profile";
	const termOptions = planTerms.map((term, index) => {
		const [, semester] = term.key.split("::");
		return { key: term.key, label: `Sem ${index + 1}: ${semester || "Term"}` };
	});
	const activeTermOption =
		termOptions.find((term) => term.key === activeTermKey) || termOptions[0];
	const activeTermLabel = activeTermOption?.label || "No semester selected";
	const dashboardContent = (
		<div className="min-h-screen bg-slate-100 px-4 py-4 text-slate-900 sm:px-6 lg:px-8">
			<div className="mx-auto max-w-none">
				<header className="mb-4">
					<h1 className="text-2xl font-semibold text-slate-950">
						Customize Your Education <span className="text-blue-600">Plan</span>
					</h1>
				</header>

				{error && (
					<div className="mb-5 rounded-lg border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">
						{error}
					</div>
				)}

				<div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_430px]">
					<aside className="space-y-4 xl:order-2">
						<div className="hidden rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
							<div className="flex items-center gap-3">
								<div className="flex h-11 w-11 items-center justify-center rounded-lg bg-blue-700 text-sm font-extrabold text-white">
									{studentInitials}
								</div>
								<div className="min-w-0">
									<p className="truncate text-sm font-extrabold text-slate-900">
										{studentName}
									</p>
									<p className="truncate text-xs font-semibold text-slate-400">
										ID: {studentId}
									</p>
								</div>
							</div>

							<div className="mt-4 grid grid-cols-2 gap-2">
								<div className="rounded-md bg-slate-50 p-3">
									<p className="text-xs font-extrabold uppercase text-slate-400">UG GPA</p>
									<p className="text-lg font-extrabold text-blue-700">{profile.gpa || "N/A"}</p>
								</div>
								<div className="rounded-md bg-slate-50 p-3">
									<p className="text-xs font-extrabold uppercase text-slate-400">PG GPA</p>
									<p className="text-lg font-extrabold text-slate-500">N/A</p>
								</div>
							</div>

							<div className="mt-3 rounded-md bg-slate-50 p-3">
								<p className="text-xs font-extrabold uppercase text-slate-400">Program</p>
								<p className="mt-1 text-sm font-extrabold text-blue-700">
									{selectedProgram || "Not selected"}
								</p>
							</div>

							<div className="mt-4">
								<div className="mb-2 flex items-center justify-between text-xs font-extrabold text-slate-500">
									<span>Progress</span>
									<span>{progressPercent}%</span>
								</div>
								<div className="h-2 rounded-full bg-slate-100">
									<div className="h-2 rounded-full bg-blue-700" style={{ width: `${progressPercent}%` }} />
								</div>
								<p className="mt-2 text-center text-xs font-extrabold text-emerald-700">
									{totalCredits}/{requiredCredits || "N/A"} Credits
								</p>
							</div>
						</div>

						<div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
							<div className="mb-3 flex items-center justify-between">
								<h3 className="text-xs font-extrabold uppercase tracking-wide text-slate-500">
									Course Catalog
								</h3>
								<div className="flex items-center gap-2">
									<span className="rounded bg-slate-50 px-2 py-1 text-xs font-extrabold text-slate-500">
										{remainingCourses.length}
									</span>
									<button
										type="button"
										onClick={savePlan}
										disabled={dependencyIssues.some((issue) => issue.blocking)}
										className="rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-extrabold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
									>
										Save Plan
									</button>
								</div>
							</div>
							<p className="mb-3 rounded-md bg-blue-50 px-3 py-2 text-xs font-bold text-blue-700">
								Adding to: {activeTermLabel}
							</p>
							<div className="max-h-[calc(100vh-260px)] space-y-2 overflow-y-auto pr-1">
								{remainingCourses.length === 0 && (
									<p className="rounded-md bg-slate-50 p-3 text-center text-sm font-semibold text-slate-500">
										{availableCourses.length === 0
											? "Select a program to create your Education Plan."
											: "All courses have been added to your plan."}
									</p>
								)}
								{remainingCourses.map((course) => (
									<button
										key={`${course.code}-${course.semester}`}
										type="button"
										onClick={() => addCourse(course)}
										className="w-full rounded-md border border-slate-100 bg-white p-3 text-left shadow-sm transition hover:border-blue-200 hover:bg-blue-50"
									>
										<div className="flex items-start gap-2">
											<div className="min-w-0 flex-1">
												<p className="truncate text-sm font-extrabold text-slate-800">
													{course.name}
												</p>
												<p className="mt-1 text-xs font-semibold text-slate-500">
													{course.code} - {course.credits ?? "N/A"}CR
												</p>
											</div>
											<FaPlus className="mt-1 h-3 w-3 text-blue-700" />
										</div>
									</button>
								))}
							</div>
						</div>
					</aside>

					<main className="space-y-4 xl:order-1">
						<h2 className="text-xl font-semibold text-slate-800">
							My Education Plan
						</h2>
						<div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
							<div className="grid gap-4 lg:grid-cols-[1fr_auto]">
								<div className="space-y-3">
									<label className="block text-xs font-extrabold uppercase tracking-wide text-slate-400">
										University
										{selectedUniversity ? (
											<span className="mt-2 block rounded-md border border-blue-100 bg-blue-50 px-3 py-2 text-sm font-bold normal-case tracking-normal text-blue-800">
												{selectedUniversity}
												{selectedDegree && <span className="ml-2 text-blue-600">({selectedDegree})</span>}
											</span>
										) : (
											<span className="mt-2 block rounded-md border border-rose-100 bg-rose-50 px-3 py-2 text-sm font-bold normal-case tracking-normal text-rose-700">
												Select a University/College from the Find University Page.
											</span>
										)}
									</label>

									<label className="block text-xs font-extrabold uppercase tracking-wide text-slate-400">
										Program
										<select
											value={selectedProgram}
											onChange={(event) => {
												setSelectedProgram(event.target.value);
												saveStorage("Programname", event.target.value);
												const found = programs.find(
													(p) =>
														p.program === event.target.value &&
														p.university === selectedUniversity
												);
												if (found) {
													setSelectedDegree(found.degree || "");
													saveStorage("ProgramDegree", found.degree || "");
												} else {
													setSelectedDegree("");
													saveStorage("ProgramDegree", "");
												}
											}}
											className="mt-2 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-bold normal-case tracking-normal text-slate-700 outline-none focus:border-blue-500"
										>
											<option value="">Select Program</option>
											{uniqueProgramOptions.map((program) => (
												<option
													key={`${program.university}-${program.program}`}
													value={program.program}
												>
													{program.program}
												</option>
											))}
										</select>
									</label>
								</div>

								<div className="flex flex-wrap items-start gap-2 lg:justify-end">
									<select
										value={activeTermOption?.key || ""}
										onChange={(event) => {
											const nextKey = event.target.value;
											setActiveTermKey(nextKey);
											setExpandedTerms((prev) => ({ ...prev, [nextKey]: true }));
										}}
										className="h-11 rounded-lg border-2 border-blue-700 bg-white px-3 text-sm font-extrabold text-slate-800 outline-none"
									>
										{termOptions.length === 0 ? (
											<option value="">No terms</option>
										) : (
											termOptions.map((term) => (
												<option key={term.key} value={term.key}>
													{term.label}
												</option>
											))
										)}
									</select>
					<button
						type="button"
						onClick={addSemester}
						disabled={planTerms.length >= MAX_SEMESTERS}
						title={
							planTerms.length >= MAX_SEMESTERS
								? `Maximum of ${MAX_SEMESTERS} semesters reached`
								: "Add a semester"
						}
						className="inline-flex h-11 items-center gap-2 rounded-lg bg-blue-700 px-4 text-sm font-extrabold text-white shadow-sm hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-300"
					>
						<FaPlus className="h-3 w-3" />
						Add Semester
						<span className="text-xs font-bold opacity-80">
							({planTerms.length}/{MAX_SEMESTERS})
						</span>
					</button>
								</div>
							</div>

							<div className="mt-4 flex flex-wrap gap-3 border-t border-slate-100 pt-4">
								<select
									value={yearFilter}
									onChange={(e) => setYearFilter(e.target.value)}
									className="rounded-md border border-slate-200 px-3 py-2 text-sm font-bold text-slate-700"
								>
									<option value="">All Years</option>
									{yearOptions.map((yr) => (
										<option key={yr} value={yr}>
											{yr}
										</option>
									))}
								</select>
								<select
									value={semesterFilter}
									onChange={(e) => setSemesterFilter(e.target.value)}
									className="rounded-md border border-slate-200 px-3 py-2 text-sm font-bold text-slate-700"
								>
									<option value="">All Semesters</option>
									{[...new Set(courses.map((c) => c.semester).filter(Boolean))].map((sem) => (
										<option key={sem} value={sem}>
											{sem}
										</option>
									))}
								</select>
								<span className="rounded-md bg-blue-50 px-3 py-2 text-sm font-extrabold text-blue-700">
									{totalCourses} courses
								</span>
								<span className="rounded-md bg-emerald-50 px-3 py-2 text-sm font-extrabold text-emerald-700">
									{creditsProgressText}
								</span>
								<span className="rounded-md bg-slate-50 px-3 py-2 text-sm font-bold text-slate-600">
									Pre: {prereqProgramCount} / Co: {coreqProgramCount}
								</span>
								<span className="rounded-md bg-amber-50 px-3 py-2 text-sm font-bold text-amber-700">
									Semester limit: {MIN_SEMESTER_CREDITS}-{MAX_SEMESTER_CREDITS} credits
								</span>
								{averageAnnualCost && (
									<span className="rounded-md bg-slate-50 px-3 py-2 text-sm font-bold text-slate-600">
										Avg. Annual Cost: {averageAnnualCost}
									</span>
								)}
							</div>
						</div>

						{dependencyIssues.length > 0 && (
							<div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 shadow-sm">
								<p className="font-extrabold">Resolve these before saving:</p>
								<ul className="mt-2 list-inside list-disc space-y-1">
									{dependencyIssues.map((issue) => (
										<li key={`${issue.type}-${issue.courseCode}-${issue.relatedCode || ""}`}>
											{issue.message}
										</li>
									))}
								</ul>
							</div>
						)}

						{eligibilityCriteria && (
							<div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 shadow-sm">
								<span className="font-extrabold text-slate-800">Eligibility Criteria: </span>
								{eligibilityCriteria}
							</div>
						)}

						<div className="space-y-2">
							{groupedCourseEntries.map(([groupKey, courseList], index) => {
								const [courseYear, courseSemester] = groupKey.split("::");
								const semesterCredits = courseList.reduce((sum, course) => {
									const value = Number(course.credits);
									return sum + (Number.isFinite(value) ? value : 0);
								}, 0);
								const isExpanded = Boolean(expandedTerms[groupKey]);
								const status = activeTermKey === groupKey ? "Selected" : "Planned";
								const statusClass =
									status === "Selected"
										? "bg-blue-50 text-blue-700"
										: "bg-slate-100 text-slate-500";

								return (
									<div
										key={groupKey}
										className={`rounded-lg border bg-white shadow-sm ${
											isExpanded ? "border-emerald-100" : "border-slate-200"
										}`}
									>
						<div
							className={`flex w-full items-center gap-3 px-4 py-4 ${
								activeTermKey === groupKey ? "bg-blue-50/70" : ""
							}`}
						>
						<button
							type="button"
							onClick={() => {
								setActiveTermKey(groupKey);
								setExpandedTerms((prev) => ({
									...prev,
									[groupKey]: !prev[groupKey],
								}));
							}}
							className="flex min-w-0 flex-1 items-center gap-3 text-left"
						>
											<span
												className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-sm font-extrabold text-white ${
													activeTermKey === groupKey ? "bg-blue-700" : "bg-slate-400"
												}`}
											>
												{index + 1}
											</span>
											<div className="min-w-0 flex-1">
												<h3 className="truncate text-sm font-extrabold text-slate-900">
													Sem {index + 1}: {courseSemester}
												</h3>
												<p className="text-xs font-medium text-slate-500">
									{courseList.length} courses - {semesterCredits} credits - {courseYear}
								</p>
							</div>
						</button>
						<button
							type="button"
							onClick={() =>
								deleteSemester({
									key: groupKey,
									year: courseYear,
									semester: courseSemester,
								})
							}
							className="inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-xs font-extrabold text-rose-500 hover:bg-rose-50 hover:text-rose-700"
							aria-label={`Delete semester ${index + 1}: ${courseSemester}`}
							title="Delete semester"
						>
							<FaTrash className="h-3 w-3" />
							<span className="hidden sm:inline">Delete</span>
						</button>
							<span className={`rounded-md px-3 py-1 text-xs font-extrabold uppercase ${statusClass}`}>
								{status}
							</span>
						<button
							type="button"
							onClick={() => {
								setActiveTermKey(groupKey);
								setExpandedTerms((prev) => ({
									...prev,
									[groupKey]: !prev[groupKey],
								}));
							}}
							className="shrink-0 rounded p-1"
							aria-label={`${isExpanded ? "Collapse" : "Expand"} semester ${index + 1}`}
						>
							{isExpanded ? (
								<FaChevronUp className="h-3 w-3 text-slate-400" />
							) : (
								<FaChevronDown className="h-3 w-3 text-slate-400" />
							)}
						</button>
						</div>

										{isExpanded && (
											<div className="space-y-2 border-t border-slate-100 px-4 pb-4 pt-3">
												{courseList.length === 0 && (
													<div className="rounded-md border border-dashed border-slate-200 bg-slate-50 p-4 text-sm font-semibold text-slate-500">
														Select this semester, then add subjects from the course catalog.
													</div>
												)}
												{courseList.map((course) => {
													const prereqText = normalizeRequirement(course.prerequisite);
													const coreqText = normalizeRequirement(course.corequisite);
													const scheduleText = formatSchedule(course.schedule);
													const hasIssue = dependencyIssues.some(
														(issue) => issue.courseCode === course.code
													);

													return (
														<div
															key={course.code}
															className={`rounded-md border bg-white px-3 py-2 shadow-sm ${
																hasIssue ? "border-rose-200 bg-rose-50" : "border-slate-100"
															}`}
														>
															<div className="flex items-center gap-3">
																<div className="min-w-0 flex-1">
																	<p className="truncate text-sm font-semibold text-slate-900">
																		{course.courseName}
																	</p>
																	<div className="mt-1 flex flex-wrap gap-x-5 gap-y-1 text-xs font-medium text-slate-600">
																		<span>Code: <span className="font-semibold text-slate-800">{course.code}</span></span>
																		<span>Credits: <span className="font-semibold text-slate-800">{course.credits ?? "N/A"}</span></span>
																		{hasMeaningfulRequirement(prereqText) && (
																			<span className="text-sky-700">
																				Pre-requisite: <span className="text-orange-500">{prereqText}</span>
																			</span>
																		)}
																		{hasMeaningfulRequirement(coreqText) && (
																			<span className="text-sky-700">
																				Corequisite: <span className="text-yellow-500">{coreqText}</span>
																			</span>
																		)}
																	</div>
																</div>
																<button
																	type="button"
																	onClick={() => removeCourse(course.code)}
																	className="shrink-0 rounded px-2 py-1 text-xs font-bold text-rose-500 hover:bg-rose-50"
																	aria-label={`Remove ${course.courseName}`}
																>
																	Remove
																</button>
															</div>
															{scheduleText && (
																<p className="mt-1 truncate text-xs font-medium text-slate-500">
																	{scheduleText}
																</p>
															)}
														</div>
													);
												})}
											</div>
										)}
									</div>
								);
							})}

							{selectedProgram && selectedUniversity && groupedCourseEntries.length === 0 && (
								<div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm font-semibold text-slate-500 shadow-sm">
									Click Add Semester to start building Jack&apos;s plan.
								</div>
							)}

							{(!selectedProgram || !selectedUniversity) && (
								<div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm font-semibold text-slate-500 shadow-sm">
									Select a university and program to build your semester plan.
								</div>
							)}
						</div>
					</main>
				</div>
			</div>
		</div>
	);

	return (
		<section className="space-y-4">
			{/* Credit Limit Modal */}
			{creditLimitModal && (
				<div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
					<div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4 animate-in fade-in zoom-in duration-200">
						<div className="flex items-start gap-4">
							<div className="flex-shrink-0 w-12 h-12 rounded-full bg-rose-100 flex items-center justify-center">
								<svg
									className="w-6 h-6 text-rose-600"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
										d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
									/>
								</svg>
							</div>
							<div className="flex-1">
								<h3 className="text-lg font-semibold text-slate-900">
									Cannot add {creditLimitModal.courseName}
								</h3>
								<p className="text-sm text-slate-600 mt-1">
									This exceeds the selected semester credit limit.
								</p>
							</div>
						</div>

						<div className="bg-slate-50 rounded-lg p-4 space-y-2 text-sm">
							{creditLimitModal.termLabel && (
								<div className="flex justify-between items-center">
									<span className="text-slate-600">Semester:</span>
									<span className="font-semibold text-slate-900">
										{creditLimitModal.termLabel}
									</span>
								</div>
							)}
							<div className="flex justify-between items-center">
								<span className="text-slate-600">Current:</span>
								<span className="font-semibold text-slate-900">
									{creditLimitModal.currentCredits} credits
								</span>
							</div>
							<div className="flex justify-between items-center">
								<span className="text-slate-600">Adding:</span>
								<span className="font-semibold text-indigo-600">
									+{creditLimitModal.addingCredits} credits
								</span>
							</div>
							<div className="border-t border-slate-200 pt-2 flex justify-between items-center">
								<span className="text-slate-600">Total would be:</span>
								<span className="font-bold text-rose-600">
									{creditLimitModal.totalWouldBe} credits
								</span>
							</div>
							<div className="flex justify-between items-center">
								<span className="text-slate-600">Semester limit:</span>
								<span className="font-bold text-slate-900">
									{creditLimitModal.programLimit} credits
								</span>
							</div>
						</div>

						<p className="text-sm text-slate-600">
							Remove some courses from this semester before adding {creditLimitModal.courseName}.
						</p>

						<button
							onClick={() => setCreditLimitModal(null)}
							className="w-full px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
						>
							OK
						</button>
					</div>
				</div>
			)}

			{dashboardContent}
		</section>
	);
};

export default EducationPlanEditor;

