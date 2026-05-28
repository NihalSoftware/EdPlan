let educationCache = null;

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

const normalizeProgramCatalog = (payload) => {
	if (Array.isArray(payload)) return payload;

	if (Array.isArray(payload?.universities)) {
		return payload.universities.flatMap((universityEntry) =>
			(universityEntry.programs || []).map((program) => ({
				...program,
				university: program.university || universityEntry.university,
				college_profile:
					program.college_profile || universityEntry.college_profile || null,
				years: program.years || groupCoursesByTerm(program.courses || []),
			}))
		);
	}

	return [];
};

const loadPrograms = async () => {
	if (educationCache) return educationCache;
	const response = await fetch("/assets/programdetail.json");
	if (!response.ok) {
		throw new Error("Unable to load education plans");
	}
	const payload = await response.json();
	educationCache = normalizeProgramCatalog(payload);
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
