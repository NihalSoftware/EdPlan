// src/utils/recommendationEngine.js
import programData from "../../public/assets/programdetail_old.json";

// Helper function: Course ke time ko user ke busy time se match karne ke liye
const checkTimeConflict = (courseTimeStr, busyTimes) => {
  if (courseTimeStr === "TBD" || courseTimeStr === "Asynchronous" || courseTimeStr === "Online") {
    return false; // In courses ka time flexible hota hai, toh clash nahi hoga
  }

  const timeLower = courseTimeStr.toLowerCase();
  let isMorning = false;   // 8:00 AM - 11:59 AM
  let isAfternoon = false; // 12:00 PM - 3:59 PM
  let isEvening = false;   // 4:00 PM onwards

  // Basic time keyword matching
  if (timeLower.includes("am")) isMorning = true;
  if (timeLower.includes("12:") || timeLower.includes("1:") || timeLower.includes("2:") || timeLower.includes("3:")) {
    if (timeLower.includes("pm")) isAfternoon = true;
  }
  if (timeLower.includes("4:") || timeLower.includes("5:") || timeLower.includes("6:") || timeLower.includes("7:")) {
    if (timeLower.includes("pm")) isEvening = true;
  }

  // Agar user us time par busy hai jis time class hai, toh true (conflict) return karo
  if (busyTimes.morning && isMorning) return true;
  if (busyTimes.afternoon && isAfternoon) return true;
  if (busyTimes.evening && isEvening) return true;

  // Agar user ne koi specific time select nahi kiya, lekin day match hua hai, toh hum assume karenge us din pura time busy hai
  const noTimeSelected = !busyTimes.morning && !busyTimes.afternoon && !busyTimes.evening;
  if (noTimeSelected) return true; 

  return false;
};

export const getRecommendedPrograms = (studentParams) => {
  if (!studentParams || !programData) return [];

  const { busyDays, busyTimes } = studentParams;
  const busyDaysArray = busyDays ? Object.keys(busyDays).filter((day) => busyDays[day]) : [];

  return programData.filter((program) => {
    let hasScheduleConflict = false;

    // Agar student ne koi din select hi nahi kiya, toh sab valid hai
    if (busyDaysArray.length === 0) return true;

    // JSON ke andar loop lagana (Year -> Semester -> Course)
    if (program.years) {
      for (const year of program.years) {
        if (year.semesters) {
          for (const sem of year.semesters) {
            if (sem.courses) {
              for (const course of sem.courses) {
                if (course.schedule && course.schedule.day) {
                  const courseDays = course.schedule.day;
                  const courseTime = course.schedule.time;

                  if (courseDays === "Online" || courseDays === "TBD") continue;

                  // Check if day clashes
                  let dayMatch = false;
                  for (const bDay of busyDaysArray) {
                    if (courseDays.includes(bDay)) {
                      dayMatch = true;
                      break;
                    }
                  }

                  // Agar din match hota hai, toh check karo ki kya time bhi clash kar raha hai
                  if (dayMatch) {
                    const timeClash = checkTimeConflict(courseTime, busyTimes);
                    if (timeClash) {
                      hasScheduleConflict = true;
                      break;
                    }
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

    // Return only those programs that do NOT have a conflict
    return !hasScheduleConflict;
  });
};