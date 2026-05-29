// src/pages/RecommendationPage.jsx
import { useState } from "react";
import { load } from "../utils/storage";
import { getRecommendedPrograms } from "../utils/recommendationEngine";
import clsx from "clsx";

const RecommendationPage = () => {
  const [list, setList] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  
  const [busyDays, setBusyDays] = useState({
    Mon: false, Tue: false, Wed: false, Thu: false, Fri: false
  });

  const [busyTimes, setBusyTimes] = useState({
    morning: false, // 8 AM - 12 PM
    afternoon: false, // 12 PM - 4 PM
    evening: false // 4 PM onwards
  });

  const toggleDay = (day) => {
    setBusyDays((prev) => ({ ...prev, [day]: !prev[day] }));
  };

  const toggleTime = (timeSlot) => {
    setBusyTimes((prev) => ({ ...prev, [timeSlot]: !prev[timeSlot] }));
  };

  const handleSearch = () => {
    const profile = load("UserProfile") || {};
    // Ek sath days aur times bhejo filtering ke liye
    const searchParams = { ...profile, busyDays, busyTimes };
    
    const recommendations = getRecommendedPrograms(searchParams);
    setList(recommendations);
    setHasSearched(true);
  };

  return (
    <div className="p-10 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-2">Find Your Perfect Schedule</h2>
      <p className="text-slate-600 mb-8">Tell us when you work or have other commitments, and we'll find programs that fit your free time.</p>

      {/* Input Section */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm mb-8">
        
        {/* Days Selection */}
        <h3 className="font-semibold text-lg mb-4 text-slate-800">1. Select your busy working days:</h3>
        <div className="flex flex-wrap gap-3 mb-8">
          {Object.keys(busyDays).map((day) => (
            <button
              key={day}
              onClick={() => toggleDay(day)}
              className={clsx(
                "px-5 py-2 rounded-full font-medium transition whitespace-nowrap",
                busyDays[day]
                  ? "bg-indigo-600 text-white shadow-md"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              )}
            >
              {day}
            </button>
          ))}
        </div>

        {/* Times Selection */}
        <h3 className="font-semibold text-lg mb-4 text-slate-800">2. Select your busy working hours on those days:</h3>
        <div className="flex flex-wrap gap-3 mb-6">
          <button
            onClick={() => toggleTime('morning')}
            className={clsx("px-5 py-2 rounded-full font-medium transition whitespace-nowrap", busyTimes.morning ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200")}
          >
            Morning (8 AM - 12 PM)
          </button>
          <button
            onClick={() => toggleTime('afternoon')}
            className={clsx("px-5 py-2 rounded-full font-medium transition whitespace-nowrap", busyTimes.afternoon ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200")}
          >
            Afternoon (12 PM - 4 PM)
          </button>
          <button
            onClick={() => toggleTime('evening')}
            className={clsx("px-5 py-2 rounded-full font-medium transition whitespace-nowrap", busyTimes.evening ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200")}
          >
            Evening (4 PM onwards)
          </button>
        </div>

        <button 
          onClick={handleSearch}
          className="bg-[#016ce6] hover:bg-blue-700 text-white px-6 py-2 rounded-md font-semibold transition mt-4 w-full sm:w-auto"
        >
          Find Matching Programs
        </button>
      </div>

      {/* Results Section */}
      <div className="grid gap-6">
        {hasSearched && list.length === 0 && (
          <div className="p-6 bg-red-50 text-red-600 rounded-xl border border-red-100 font-medium">
            No programs match your exact schedule. Try adjusting your busy days/times.
          </div>
        )}

        {list.length > 0 && list.map((prog, i) => (
          <div key={i} className="p-6 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-bold text-[#016ce6]">{prog.program}</h3>
              <p className="text-slate-600 font-medium">{prog.university}</p>
              <p className="mt-1 text-sm text-slate-500">Total Credits: {prog.total_credit_hours}</p>
            </div>
            <div className="bg-green-100 text-green-700 px-4 py-2 rounded-md text-sm font-bold whitespace-nowrap">
              Matches Your Schedule ✓
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationPage;