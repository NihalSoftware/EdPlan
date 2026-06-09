// src/utils/recommendationEngine.js
import programData from "../../public/assets/ScheduleNNMC.json";

const dayMap = {
  "Mon": "Mon", "Tue": "Tue", "Wed": "Wed", "Thu": "Thu", "Fri": "Fri",
  "M": "Mon", "T": "Tue", "W": "Wed", "R": "Thu", "F": "Fri", "S": "Sat", "U": "Sun"
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

  return ["All Programs", ...Array.from(programsSet).sort()];
};

// Strict Time Matcher
const checkTimeConflict = (startTime, busyTimes) => {
  if (!startTime) return false; // Agar asynchronous/online hai to conflict nahi hai

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

// Advanced Smart Matching Engine
export const getRecommendedPrograms = (searchParams) => {
  if (!searchParams || !programData || !programData.semesters) return [];

  const { selectedProgram, busyDays, busyTimes } = searchParams;
  
  // Clean busy days arrays
  const busyDaysArray = busyDays ? Object.keys(busyDays).filter((day) => busyDays[day]) : [];
  
  // Format search keyword for fuzzy matching
  const searchKeyword = selectedProgram && selectedProgram !== "All Programs" 
    ? selectedProgram.toLowerCase().trim() 
    : "";

  const groupedPrograms = {};
  const uniName = programData.universityName || "Northern New Mexico College";

  Object.entries(programData.semesters).forEach(([semesterKey, semesterData]) => {
    if (!semesterData.programs) return;

    Object.entries(semesterData.programs).forEach(([progName, progData]) => {
      
      // ✅ FIX: FUZZY MATCHING
      // Agar user ne "math" bola hai to "Mathematics, General" match ho jayega
      if (searchKeyword) {
        const actualName = progName.toLowerCase();
        if (!actualName.includes(searchKeyword)) {
          return; // Match nahi hua to skip kar do
        }
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
              
              // Map short days like 'M', 'T' to 'Mon', 'Tue'
              const mappedDays = days.map(d => dayMap[d] || d);
              let sectionClash = false;

              // Day & Time Conflict Check
              if (busyDaysArray.length > 0 && days.length > 0) {
                const dayMatch = mappedDays.some(d => busyDaysArray.includes(d));
                if (dayMatch) {
                  // Agar day match hua, tab time check karo
                  if (checkTimeConflict(startTime, busyTimes || {})) {
                    sectionClash = true;
                  }
                }
              }

              // Agar clash nahi hai, tab is section ko add karo
              if (!sectionClash) {
                validSectionFound = true;
                selectedSection = sec;
                break; // Ek valid section mil gaya ek course ke liye, toh baaki check karne ki zarurat nahi
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
                  day: selectedSection.days.map(d => dayMap[d]).join(", ") || (selectedSection.instructionMethod.includes("OL") ? "Online" : "Asynchronous"),
                  time: selectedSection.startTime ? `${selectedSection.startTime} - ${selectedSection.endTime}` : "Flexible"
                }
              });
            }
          }
        });
      }

      // Agar kisi bhi course me conflict nahi hai aur at least 1 course mila hai, toh result me daalo
      if (!hasConflict && formattedCourses.length > 0) {
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