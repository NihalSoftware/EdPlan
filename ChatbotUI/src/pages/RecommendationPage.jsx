import { useState, useEffect } from "react";
import { load } from "../utils/storage";
import { getRecommendedPrograms, getProgramList } from "../utils/recommendationEngine";
import clsx from "clsx";

const RecommendationPage = () => {
  const [list, setList] = useState([]);
  const [programOptions, setProgramOptions] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState("All Programs");
  const [hasSearched, setHasSearched] = useState(false);
  
  // Track currently expanded card
  const [expandedIndex, setExpandedIndex] = useState(null);
  
  // Naya State: Track active year tab for the expanded card (Default: 0 for 1st Year)
  const [activeYearIndex, setActiveYearIndex] = useState(0);
  
  const [busyDays, setBusyDays] = useState({
    Mon: false, Tue: false, Wed: false, Thu: false, Fri: false
  });

  const [busyTimes, setBusyTimes] = useState({
    morning: false,
    afternoon: false,
    evening: false
  });

  useEffect(() => {
    setProgramOptions(getProgramList());
  }, []);

  const toggleDay = (day) => {
    setBusyDays((prev) => ({ ...prev, [day]: !prev[day] }));
  };

  const toggleTime = (timeSlot) => {
    setBusyTimes((prev) => ({ ...prev, [timeSlot]: !prev[timeSlot] }));
  };

  const handleSearch = () => {
    try {
      const profile = load("UserProfile") || {};
      const searchParams = { ...profile, selectedProgram, busyDays, busyTimes };
      
      const recommendations = getRecommendedPrograms(searchParams);
      setList(recommendations);
      setHasSearched(true);
      setExpandedIndex(null); // Collapse any open cards on new search
      setActiveYearIndex(0); // Reset year tab
    } catch (error) {
      console.error("Error generating recommendations:", error);
    }
  };

  // Card expand/collapse toggle logic
  const toggleExpand = (index) => {
    if (expandedIndex === index) {
      setExpandedIndex(null); // Agar same card click kiya toh band kar do
    } else {
      setExpandedIndex(index); // Naya card open karo
      setActiveYearIndex(0);   // Naye card ke liye hamesha 1st Year se shuru karo
    }
  };

  return (
    <div className="p-8 md:p-12 max-w-5xl mx-auto">
      <header className="mb-10">
        <h2 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-3">Smart Course Schedule</h2>
        <p className="text-lg text-slate-600">Filter programs by your interest and work schedule to find the perfect fit.</p>
      </header>

      {/* Control Panel */}
      <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm mb-10">
        <div className="mb-8">
          <label className="block font-semibold text-lg mb-3 text-slate-800">1. Which program are you interested in?</label>
          <select 
            value={selectedProgram} 
            onChange={(e) => setSelectedProgram(e.target.value)}
            className="w-full md:w-1/2 p-3 border border-slate-300 rounded-lg bg-slate-50 focus:ring-2 focus:ring-[#016ce6] focus:border-[#016ce6] outline-none"
          >
            {programOptions.map((prog, idx) => (
              <option key={idx} value={prog}>{prog}</option>
            ))}
          </select>
        </div>

        <div className="mb-8">
          <label className="block font-semibold text-lg mb-3 text-slate-800">2. Select the days you are BUSY (working/unavailable):</label>
          <div className="flex flex-wrap gap-3">
            {Object.keys(busyDays).map((day) => (
              <button
                key={day}
                onClick={() => toggleDay(day)}
                className={clsx(
                  "px-6 py-2.5 rounded-full font-medium transition-all duration-200 border",
                  busyDays[day]
                    ? "bg-indigo-600 text-white border-indigo-600 shadow-md transform scale-105"
                    : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
                )}
              >
                {day}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-8">
          <label className="block font-semibold text-lg mb-3 text-slate-800">3. Select the time slots you are BUSY on those days:</label>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => toggleTime('morning')}
              className={clsx("px-6 py-2.5 rounded-full font-medium transition-all duration-200 border", busyTimes.morning ? "bg-indigo-600 text-white border-indigo-600" : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50")}
            >
              Morning (8 AM - 12 PM)
            </button>
            <button
              onClick={() => toggleTime('afternoon')}
              className={clsx("px-6 py-2.5 rounded-full font-medium transition-all duration-200 border", busyTimes.afternoon ? "bg-indigo-600 text-white border-indigo-600" : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50")}
            >
              Afternoon (12 PM - 4 PM)
            </button>
            <button
              onClick={() => toggleTime('evening')}
              className={clsx("px-6 py-2.5 rounded-full font-medium transition-all duration-200 border", busyTimes.evening ? "bg-indigo-600 text-white border-indigo-600" : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50")}
            >
              Evening (4 PM onwards)
            </button>
          </div>
        </div>

        <button 
          onClick={handleSearch}
          className="bg-[#016ce6] hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-bold text-lg transition-colors w-full md:w-auto shadow-sm"
        >
          Generate Recommendations
        </button>
      </div>

      {/* Results Section */}
      <div className="grid gap-6">
        {hasSearched && list.length === 0 && (
          <div className="p-8 bg-amber-50 text-amber-800 rounded-2xl border border-amber-200 flex flex-col items-center text-center">
            <span className="text-4xl mb-3">⚠️</span>
            <h3 className="text-xl font-bold mb-2">No Match Found</h3>
            <p className="max-w-lg">
              It looks like your busy schedule conflicts with all available classes for the selected program. Try freeing up some days, or look for fully online/asynchronous programs.
            </p>
          </div>
        )}

        {list.length > 0 && list.map((prog, i) => (
          <div key={i} className="bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow overflow-hidden">
            {/* Card Header (Summary) */}
            <div className="p-6 md:p-8 flex flex-col md:flex-row md:items-start justify-between gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-2xl font-bold text-slate-900">{prog.program || "Unknown Program"}</h3>
                  <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide">
                    {prog.degree || "Degree"}
                  </span>
                </div>
                <p className="text-slate-600 text-lg font-medium mb-3">{prog.university || "University not specified"}</p>
                
                <div className="flex flex-wrap gap-4 text-sm text-slate-500 mb-4">
                  <span className="flex items-center gap-1 bg-slate-100 px-3 py-1 rounded-md">
                    ⏱ Credits: {prog.total_credit_hours || "N/A"}
                  </span>
                  <span className="flex items-center gap-1 bg-slate-100 px-3 py-1 rounded-md">
                    💸 {prog.average_annual_cost ? `${prog.average_annual_cost.split(' ')[0]} / yr` : "Cost N/A"}
                  </span>
                </div>
              </div>
              
              <div className="flex flex-col items-end gap-3 min-w-[200px]">
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-2 rounded-xl text-center shadow-sm w-full">
                  <div className="font-bold">Perfect Match ✓</div>
                </div>
                <button 
                  onClick={() => toggleExpand(i)}
                  className="w-full text-center px-4 py-2 border-2 border-[#016ce6] text-[#016ce6] hover:bg-[#016ce6] hover:text-white rounded-lg font-semibold transition"
                >
                  {expandedIndex === i ? "Hide Details ⬆" : "View Full Details ⬇"}
                </button>
              </div>
            </div>

            {/* A to Z Expanded Data Section */}
            {expandedIndex === i && (
              <div className="p-6 md:p-8 border-t border-slate-200 bg-slate-50">
                
                {/* College Profile Section */}
                {prog.college_profile && (
                  <div className="mb-8 bg-white p-6 rounded-xl border border-slate-200">
                    <h4 className="text-xl font-bold text-slate-800 border-b pb-3 mb-4">🏫 College Profile</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-700">
                      <p><strong>Campus Size:</strong> {prog.college_profile.size || "N/A"}</p>
                      <p><strong>Acceptance Rate:</strong> {prog.college_profile.acceptance_rate || "N/A"}</p>
                      <p><strong>Graduation Rate:</strong> {prog.college_profile.graduation_rate || "N/A"}</p>
                      <p><strong>Median Earnings:</strong> {prog.college_profile.median_earnings || "N/A"}</p>
                      <p><strong>Student/Faculty:</strong> {prog.college_profile.student_to_faculty_ratio || "N/A"}</p>
                      <p><strong>Website:</strong> <a href={prog.college_profile.website} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{prog.college_profile.website}</a></p>
                    </div>
                  </div>
                )}

                {/* Eligibility */}
                {prog.eligibility_criteria && (
                  <div className="mb-8">
                    <h4 className="text-xl font-bold text-slate-800 mb-2">📋 Eligibility Criteria</h4>
                    <p className="text-slate-600 bg-white p-4 rounded-lg border border-slate-200">{prog.eligibility_criteria}</p>
                  </div>
                )}

                {/* Dynamic Year Tabs (Only shows 1 year at a time) */}
                {prog.years && prog.years.length > 0 && (
                  <div>
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-4">
                      <h4 className="text-xl font-bold text-slate-800">📚 Course Curriculum</h4>
                      
                      {/* Year Selection Buttons */}
                      <div className="flex flex-wrap gap-2">
                        {prog.years.map((yearData, idx) => (
                          <button
                            key={idx}
                            onClick={() => setActiveYearIndex(idx)}
                            className={clsx(
                              "px-4 py-2 rounded-lg font-semibold text-sm transition-colors",
                              activeYearIndex === idx 
                                ? "bg-[#016ce6] text-white shadow-md" 
                                : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                            )}
                          >
                            {yearData.year}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Active Year Data Rendering */}
                    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm animate-fade-in">
                      <h5 className="text-lg font-bold text-[#016ce6] mb-4">
                        {prog.years[activeYearIndex].year} Schedule
                      </h5>
                      
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {prog.years[activeYearIndex].semesters?.map((sem, sIdx) => (
                          <div key={sIdx}>
                            <h6 className="font-semibold text-slate-700 mb-3 bg-slate-100 px-3 py-1 rounded inline-block">
                              {sem.semester} Semester ({sem.total_credits} Credits)
                            </h6>
                            <ul className="space-y-3">
                              {sem.courses?.map((course, cIdx) => (
                                <li key={cIdx} className="text-sm p-4 border border-slate-100 rounded-lg bg-slate-50 hover:bg-white transition-colors">
                                  <div className="font-bold text-slate-800 text-base mb-1">
                                    {course.code}: {course.name} <span className="text-slate-500 font-normal">({course.credits} Cr)</span>
                                  </div>
                                  <div className="text-slate-600 flex flex-wrap gap-2">
                                    <span className="bg-white px-2 py-1 border border-slate-200 rounded shadow-sm text-xs font-medium">
                                      🕒 {course.schedule?.day || "TBD"} | {course.schedule?.time || "TBD"}
                                    </span>
                                    {course.prerequisite !== "None" && (
                                      <span className="bg-amber-50 text-amber-700 px-2 py-1 border border-amber-200 rounded text-xs font-medium">
                                        Req: {course.prerequisite}
                                      </span>
                                    )}
                                  </div>
                                </li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationPage;