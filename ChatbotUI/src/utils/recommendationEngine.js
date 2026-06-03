// src/utils/recommendationEngine.js
import programData from "../../public/assets/ScheduleNNMC.json";

const dayMap = {
  "M": "Mon",
  "T": "Tue",
  "W": "Wed",
  "R": "Thu",
  "F": "Fri",
  "S": "Sat",
  "U": "Sun"
};

// Extract unique programs
export const getProgramList = () => {
  if (!programData || !programData.semesters) return ["All Programs"];

  const programsSet = new Set();
  
  Object.values(programData.semesters).forEach((semester) => {
    if (semester.programs) {
      Object.keys(semester.programs).forEach((progName) => {
        programsSet.add(progName);
      });
    }
  });

  return ["All Programs", ...Array.from(programsSet).sort()]; // Sorted alphabetically
};

// Strict Time Matcher
const checkTimeConflict = (startTime, busyTimes) => {
  if (!startTime) return false;

  const hour = parseInt(startTime.split(":")[0], 10);
  let isMorning = hour >= 0 && hour < 12;
  let isAfternoon = hour >= 12 && hour < 16;
  let isEvening = hour >= 16;

  const noTimeSelected = !busyTimes.morning && !busyTimes.afternoon && !busyTimes.evening;
  if (noTimeSelected) return true; 

  if (busyTimes.morning && isMorning) return true;
  if (busyTimes.afternoon && isAfternoon) return true;
  if (busyTimes.evening && isEvening) return true;

  return false;
};

// Naya Grouping Engine
export const getRecommendedPrograms = (searchParams) => {
  if (!searchParams || !programData || !programData.semesters) return [];

  const { selectedProgram, busyDays, busyTimes } = searchParams;
  const busyDaysArray = busyDays ? Object.keys(busyDays).filter((day) => busyDays[day]) : [];

  const groupedPrograms = {};
  const uniName = programData.universityName || "Northern New Mexico College";

  Object.entries(programData.semesters).forEach(([semesterKey, semesterData]) => {
    if (!semesterData.programs) return;

    Object.entries(semesterData.programs).forEach(([progName, progData]) => {
      
      if (selectedProgram && selectedProgram !== "All Programs" && progName !== selectedProgram) {
        return; 
      }

      let hasConflict = false;
      let semCredits = 0;
      const formattedCourses = [];

      if (progData.courses) {
        Object.values(progData.courses).forEach(course => {
          let validSectionFound = false;
          let selectedSection = null;

          if (course.sections && course.sections.length > 0) {
            for (const sec of course.sections) {
              const days = sec.days || [];
              const startTime = sec.startTime;
              const mappedDays = days.map(d => dayMap[d] || d);
              let sectionClash = false;

              if (busyDaysArray.length > 0 && days.length > 0) {
                const dayMatch = mappedDays.some(d => busyDaysArray.includes(d));
                if (dayMatch) {
                  if (checkTimeConflict(startTime, busyTimes)) sectionClash = true;
                }
              }

              if (!sectionClash) {
                validSectionFound = true;
                selectedSection = sec;
                break;
              }
            }

            if (!validSectionFound) {
              hasConflict = true; 
            } else {
              semCredits += selectedSection.credits || 0;
              formattedCourses.push({
                code: course.courseCode,
                name: course.courseName,
                credits: selectedSection.credits,
                instructor: selectedSection.instructor,
                campus: selectedSection.campus || "Main",
                schedule: {
                  day: selectedSection.days.map(d => dayMap[d]).join(", ") || (selectedSection.instructionMethod.includes("OL") ? "Online" : "TBD"),
                  time: selectedSection.startTime ? `${selectedSection.startTime} - ${selectedSection.endTime}` : "Asynchronous"
                }
              });
            }
          }
        });
      }

      if (!hasConflict && formattedCourses.length > 0) {
        // Grouping Data into single Program Card
        if (!groupedPrograms[progName]) {
            groupedPrograms[progName] = {
                program: progName,
                university: uniName,
                degree: "Degree / Certificate",
                total_credit_hours: 0,
                semesters: []
            };
        }
        groupedPrograms[progName].total_credit_hours += semCredits;
        groupedPrograms[progName].semesters.push({
            semesterName: semesterKey.replace("_", " "), 
            total_credits: semCredits,
            courses: formattedCourses
        });
      }
    });
  });

  return Object.values(groupedPrograms);
};