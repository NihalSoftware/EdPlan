import {
	getCatalogCourses,
	getCatalogPrograms,
	getCatalogUniversities,
} from "./catalogService.js";

let educationCache = null;

const YEAR_LABELS = {
	1: "First Year",
	2: "Second Year",
	3: "Third Year",
	4: "Fourth Year",
	5: "Fifth Year",
	6: "Sixth Year",
	7: "Seventh Year",
	8: "Eighth Year",
};

const UNIVERSITY_DISPLAY_ALIASES = {
	"new mexico state university": "New Mexico State University-Main Campus",
	"university of new mexico": "University of New Mexico-Main Campus",
};

const displayUniversityName = (name = "") => {
	const cleaned = String(name || "").trim();
	return UNIVERSITY_DISPLAY_ALIASES[cleaned.toLowerCase()] || cleaned;
};

const normalizeCourse = (course) => ({
	id: course.course_id,
	code: course.course_code,
	name: course.course_name,
	courseName: course.course_name,
	credits: course.credits,
	lecture_hours: course.lecture_hours,
	lab_hours: course.lab_hours,
	prerequisite: "",
	corequisite: "",
	recommended_year:
		YEAR_LABELS[course.recommended_year] ||
		course.recommended_year ||
		"Unassigned Year",
	recommended_semester: course.recommended_semester || "Unassigned Semester",
	description: course.description || "",
});

const groupCoursesByTerm = (courses = []) => {
	const yearMap = new Map();

	courses.forEach((course) => {
		const year = course.recommended_year || course.year || "Unassigned Year";
		const semester =
			course.recommended_semester || course.semester || "Unassigned Semester";

		if (!yearMap.has(year)) {
			yearMap.set(year, new Map());
		}
		const semesterMap = yearMap.get(year);
		if (!semesterMap.has(semester)) {
			semesterMap.set(semester, []);
		}
		semesterMap.get(semester).push(course);
	});

	return Array.from(yearMap.entries()).map(([year, semesterMap]) => ({
		year,
		semesters: Array.from(semesterMap.entries()).map(
			([semester, semesterCourses]) => ({
				semester,
				courses: semesterCourses,
			})
		),
	}));
};

const loadPrograms = async () => {
	if (educationCache) return educationCache;
	const universities = await getCatalogUniversities();
	const programGroups = await Promise.all(
		universities.map(async (university) => {
			const programs = await getCatalogPrograms(university.university_id);
			const universityName = displayUniversityName(university.university_name);
			return Promise.all(
				programs.map(async (program) => {
					const courses = (await getCatalogCourses(program.program_id)).map(
						normalizeCourse
					);
					return {
						...program,
						program: program.program_name,
						university: universityName,
						campus: universityName,
						degree: program.degree,
						total_credit_hours: program.total_credit_hours,
						college_profile: {
							university_name: universityName,
							city: university.city,
							state: university.state,
							website: university.website,
						},
						courses,
						years: groupCoursesByTerm(courses),
					};
				})
			);
		})
	);
	educationCache = programGroups.flat();
	return educationCache;
};

export const findProgramPlan = async (programName, universityName) => {
	const programs = await loadPrograms();
	return (
		programs.find(
			(program) =>
				program.program === programName && program.university === universityName
		) || null
	);
};

export const listPrograms = async () => loadPrograms();
