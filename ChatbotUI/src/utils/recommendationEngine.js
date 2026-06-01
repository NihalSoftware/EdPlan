// src/utils/recommendationEngine.js
import programData from "../../public/assets/programdetail_old.json";

// Helper function: Extract unique programs for the dropdown
export const getProgramList = () => {
  if (!programData) return [];
  const programs = programData.map(p => p.program);
  return ["All Programs", ...new Set(programs)]; // Removes duplicates
};

// Helper function: Strictly check time conflicts
const checkTimeConflict = (courseTimeStr, busyTimes) => {
  if (!courseTimeStr || courseTimeStr === "TBD" || courseTimeStr === "Asynchronous" || courseTimeStr === "Online") {
    return false; // Flexible courses never clash
  }

  const timeLower = courseTimeStr.toLowerCase();
  let isMorning = false;   
  let isAfternoon = false; 
  let isEvening = false;   

  // Regex for accurate time slot matching
  if (timeLower.includes("am")) isMorning = true;
  if (timeLower.match(/(12:|1:|2:|3:).*pm/)) isAfternoon = true;
  if (timeLower.match(/(4:|5:|6:|7:|8:|9:|10:|11:).*pm/)) isEvening = true;

  // Agar user ne time select nahi kiya par day match ho gaya, to default "busy" mano
  const noTimeSelected = !busyTimes.morning && !busyTimes.afternoon && !busyTimes.evening;
  if (noTimeSelected) return true; 

  if (busyTimes.morning && isMorning) return true;
  if (busyTimes.afternoon && isAfternoon) return true;
  if (busyTimes.evening && isEvening) return true;

  return false;
};

export const getRecommendedPrograms = (searchParams) => {
  if (!searchParams || !programData) return [];

  const { selectedProgram, busyDays, busyTimes } = searchParams;
  const busyDaysArray = busyDays ? Object.keys(busyDays).filter((day) => busyDays[day]) : [];

  return programData.filter((program) => {
    // 1. Program Dropdown Filter
    if (selectedProgram && selectedProgram !== "All Programs" && program.program !== selectedProgram) {
      return false; // Reject if it doesn't match the selected program
    }

    // 2. Schedule Filter
    if (busyDaysArray.length === 0) return true; // No busy days = free for everything

    let hasScheduleConflict = false;

    // Deep loop through the curriculum
    if (program.years) {
      for (const year of program.years) {
        if (year.semesters) {
          for (const sem of year.semesters) {
            if (sem.courses) {
              for (const course of sem.courses) {
                const schedule = course.schedule || {};
                const courseDays = schedule.day || "";
                const courseTime = schedule.time || "";

                if (courseDays === "Online" || courseDays === "TBD" || courseDays === "Asynchronous") {
                  continue;
                }

                // Split course days (e.g., "Mon, Wed" -> ["Mon", "Wed"]) and check exact match
                const parsedCourseDays = courseDays.split(',').map(d => d.trim());
                const dayMatch = parsedCourseDays.some(d => busyDaysArray.includes(d));

                if (dayMatch) {
                  const timeClash = checkTimeConflict(courseTime, busyTimes);
                  if (timeClash) {
                    hasScheduleConflict = true;
                    break; // Inner loop break
                  }
                }
              }
              if (hasScheduleConflict) break;
            }
            if (hasScheduleConflict) break;
          }
        }
        if (hasScheduleConflict) break;
      }
    }

    return !hasScheduleConflict;
  });
};