import { useState, useEffect, useRef } from "react";
import { load, save } from "../utils/storage";
import { getRecommendedPrograms, getProgramList } from "../utils/recommendationEngine";
import clsx from "clsx";

// ==========================================
// 1. ICONS & SHARED COMPONENTS
// ==========================================
const Icons = {
  Brain: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5A3 3 0 0 0 13.6 4.4"/><path d="M6.401 6.5A3 3 0 0 1 10.4 4.4"/></svg>,
  Database: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>,
  Calendar: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>,
  Sparkles: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1-1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>,
  Check: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>,
  Loader: () => <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" x2="12" y1="2" y2="6"/><line x1="12" x2="12" y1="18" y2="22"/><line x1="4.93" x2="7.76" y1="4.93" y2="7.76"/><line x1="16.24" x2="19.07" y1="16.24" y2="19.07"/><line x1="2" x2="6" y1="12" y2="12"/><line x1="18" x2="22" y1="12" y2="12"/><line x1="4.93" x2="7.76" y1="19.07" y2="16.24"/><line x1="16.24" x2="19.07" y1="7.76" y2="4.93"/></svg>,
  Filter: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>,
  Back: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
};

// ==========================================
// 2. MANUAL SCHEDULER COMPONENTS
// ==========================================
const ManualResultCard = ({ prog, expandedIndex, setExpandedIndex, i }) => {
  const [activeYearIndex, setActiveYearIndex] = useState(0);

  const toggleExpand = () => {
    if (expandedIndex === i) {
      setExpandedIndex(null);
    } else {
      setExpandedIndex(i);
      setActiveYearIndex(0);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow overflow-hidden">
      <div className="p-6 md:p-8 flex flex-col md:flex-row md:items-start justify-between gap-6">
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-3 mb-2">
            <h3 className="text-2xl font-bold text-slate-900">{prog.program || "Unknown Program"}</h3>
            <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide whitespace-nowrap">
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
          <button onClick={toggleExpand} className="w-full text-center px-4 py-2 border-2 border-[#016ce6] text-[#016ce6] hover:bg-[#016ce6] hover:text-white rounded-lg font-semibold transition">
            {expandedIndex === i ? "Hide Details ⬆" : "View Full Details ⬇"}
          </button>
        </div>
      </div>

      {expandedIndex === i && (
        <div className="p-6 md:p-8 border-t border-slate-200 bg-slate-50">
          {prog.semesters && prog.semesters.length > 0 && (
            <div>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-4">
                <h4 className="text-xl font-bold text-slate-800">📚 Course Curriculum</h4>
                <div className="flex flex-wrap gap-2">
                  {prog.semesters.map((semData, idx) => (
                    <button
                      key={idx}
                      onClick={() => setActiveYearIndex(idx)}
                      className={clsx(
                        "px-4 py-2 rounded-lg font-semibold text-sm transition-colors",
                        activeYearIndex === idx ? "bg-[#016ce6] text-white shadow-md" : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                      )}
                    >
                      {semData.semesterName}
                    </button>
                  ))}
                </div>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm animate-fade-in">
                <h5 className="text-lg font-bold text-[#016ce6] mb-4">
                  {prog.semesters[activeYearIndex].semesterName} Schedule
                </h5>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <ul className="space-y-3 col-span-2">
                      {prog.semesters[activeYearIndex].courses?.map((course, cIdx) => (
                        <li key={cIdx} className="text-sm p-4 border border-slate-100 rounded-lg bg-slate-50 hover:bg-white transition-colors">
                          <div className="font-bold text-slate-800 text-base mb-1">
                            {course.code}: {course.name} <span className="text-slate-500 font-normal">({course.credits} Cr)</span>
                          </div>
                          <div className="text-slate-600 flex flex-wrap gap-2">
                            <span className="bg-white px-2 py-1 border border-slate-200 rounded shadow-sm text-xs font-medium">
                              🕒 {course.schedule?.day || "TBD"} | {course.schedule?.time || "TBD"}
                            </span>
                            <span className="bg-slate-100 text-slate-600 px-2 py-1 border border-slate-200 rounded shadow-sm text-xs font-medium">
                              👤 {course.instructor || "TBA"} | 📍 {course.campus}
                            </span>
                          </div>
                        </li>
                      ))}
                    </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ==========================================
// 3. AI AGENT COMPONENTS
// ==========================================
const AgentWorkflow = ({ currentStep, isSearching }) => {
  const steps = isSearching 
    ? [
        { id: 1, label: "Analyzing contextual intent", icon: <Icons.Brain /> },
        { id: 2, label: "Cross-referencing university database", icon: <Icons.Database /> },
        { id: 3, label: "Mapping availability matrices", icon: <Icons.Calendar /> },
        { id: 4, label: "Synthesizing schedule artifacts", icon: <Icons.Sparkles /> },
      ]
    : [
        { id: 1, label: "Updating system parameters", icon: <Icons.Brain /> },
        { id: 4, label: "Awaiting further directives", icon: <Icons.Check /> },
      ];

  return (
    <div className="bg-slate-50/80 border border-slate-200 rounded-xl p-5 mb-6 max-w-2xl font-mono text-sm shadow-sm animate-fade-in">
      <div className="text-slate-500 font-bold mb-4 flex items-center gap-2 uppercase tracking-wider text-[10px]">
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
        </span>
        Agent Execution in Progress
      </div>
      <div className="space-y-3">
        {steps.map((step) => {
          const isCompleted = currentStep > step.id;
          const isActive = currentStep === step.id;
          const isPending = currentStep < step.id;

          return (
            <div key={step.id} className={clsx(
              "flex items-center gap-3 transition-opacity duration-500",
              isPending ? "opacity-30" : "opacity-100"
            )}>
              <div className={clsx(
                "w-6 h-6 rounded-md flex items-center justify-center transition-colors",
                isCompleted ? "bg-green-100 text-green-600" : isActive ? "bg-blue-100 text-blue-600" : "bg-slate-200 text-slate-400"
              )}>
                {isCompleted ? <Icons.Check /> : isActive ? <Icons.Loader /> : step.icon}
              </div>
              <span className={clsx(
                "font-medium transition-colors",
                isCompleted ? "text-slate-600" : isActive ? "text-slate-900" : "text-slate-400"
              )}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const AgentScheduleArtifact = ({ prog, handleSavePlan }) => {
  const [activeSemIndex, setActiveSemIndex] = useState(0);

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 w-full mb-6 group">
      <div className="bg-slate-900 px-6 py-4 flex justify-between items-center rounded-t-2xl">
        <div className="flex items-center gap-3">
          <span className="text-xl">🎓</span>
          <h3 className="text-lg font-bold text-white tracking-wide">{prog.program}</h3>
        </div>
        <span className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-md text-xs font-bold uppercase tracking-wider border border-blue-500/30">
          Generated Plan
        </span>
      </div>
      
      <div className="p-6">
        <div className="flex flex-wrap gap-4 mb-6 pb-6 border-b border-slate-100">
          <div className="flex-1 min-w-[200px]">
            <p className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-1">Institution</p>
            <p className="text-slate-800 font-semibold">{prog.university}</p>
          </div>
          <div className="flex-1 min-w-[120px]">
            <p className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-1">Credential</p>
            <p className="text-slate-800 font-semibold">{prog.degree}</p>
          </div>
          <div className="flex-1 min-w-[100px]">
            <p className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-1">Total Workload</p>
            <p className="text-slate-800 font-semibold">{prog.total_credit_hours} Credits</p>
          </div>
        </div>

        {prog.semesters && prog.semesters.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span className="text-sm font-bold text-slate-800">Timeline / Curriculum</span>
              <div className="h-[1px] flex-1 bg-slate-100 ml-2"></div>
            </div>
            
            <div className="flex gap-2 mb-4 overflow-x-auto pb-2 scrollbar-hide">
              {prog.semesters.map((semData, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveSemIndex(idx)}
                  className={clsx(
                    "px-4 py-2 rounded-lg font-bold text-sm transition-all whitespace-nowrap",
                    activeSemIndex === idx ? "bg-slate-900 text-white shadow-md" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  )}
                >
                  {semData.semesterName}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {prog.semesters[activeSemIndex].courses?.map((course, cIdx) => (
                <div key={cIdx} className="p-4 border border-slate-200 rounded-xl bg-slate-50 hover:bg-white transition-colors group-hover:border-blue-100 relative">
                  <div className="absolute top-4 right-4 bg-white border border-slate-200 text-slate-600 text-[10px] font-extrabold px-2 py-1 rounded shadow-sm">
                    {course.credits} CR
                  </div>
                  <div className="text-xs font-mono text-blue-600 font-bold mb-1">{course.code}</div>
                  <div className="text-sm font-bold text-slate-800 mb-3 pr-10 leading-tight">{course.name}</div>
                  
                  <div className="bg-white p-2.5 rounded-lg border border-slate-100 shadow-sm flex items-center gap-2 mb-2">
                    <span className="text-slate-400"><Icons.Calendar /></span>
                    <span className="text-xs font-bold text-slate-700">{course.schedule.day} • {course.schedule.time}</span>
                  </div>
                  <div className="flex justify-between text-[11px] font-semibold text-slate-500 px-1">
                    <span>Prof. {course.instructor || "TBA"}</span>
                    <span>{course.campus} Campus</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-end mt-6 pt-4 border-t border-slate-100">
          <button 
            onClick={() => handleSavePlan([prog])}
            className="flex items-center gap-2 bg-white border border-slate-200 hover:border-slate-400 text-slate-700 px-4 py-2 rounded-lg text-sm font-bold shadow-sm transition-all"
          >
            <Icons.Check /> Accept & Save Plan
          </button>
        </div>

      </div>
    </div>
  );
};

// ==========================================
// 4. MAIN PAGE (ENTRY & SWITCHER)
// ==========================================
const RecommendationPage = () => {
  // Mode: null (Selection View) | 'manual' | 'agent'
  const [mode, setMode] = useState(null);

  // --- MANUAL STATE ---
  const [manualList, setManualList] = useState([]);
  const [programOptions, setProgramOptions] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState("All Programs");
  const [hasSearched, setHasSearched] = useState(false);
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [busyDays, setBusyDays] = useState({ Mon: false, Tue: false, Wed: false, Thu: false, Fri: false });
  const [busyTimes, setBusyTimes] = useState({ morning: false, afternoon: false, evening: false });

  // --- AGENT STATE ---
  const [feed, setFeed] = useState([]); 
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentAgentStep, setCurrentAgentStep] = useState(0);
  const [isSearchingContext, setIsSearchingContext] = useState(true);
  const [keyword, setKeyword] = useState("");
  const feedEndRef = useRef(null);
  const [agentMemory, setAgentMemory] = useState({ selectedProgram: "", busyDays: {}, busyTimes: {} });

  // Initialization
  useEffect(() => {
    setProgramOptions(getProgramList());
    const profile = load("UserProfile") || {};
    const name = profile.firstName || "User";
    setFeed([
      { 
        type: "agent-text", 
        content: `System initialized. Welcome, ${name}. I am the EdPlan Scheduling Agent. My core function is to generate optimal learning pathways based on your subject interests and scheduling constraints. How may I assist you today?` 
      }
    ]);
  }, []);

  // Agent Auto-Scroll
  useEffect(() => {
    if (mode === 'agent') feedEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [feed, currentAgentStep, mode]);

  // --- MANUAL HANDLERS ---
  const handleManualSearch = () => {
    try {
      const profile = load("UserProfile") || {};
      const searchParams = { ...profile, selectedProgram, busyDays, busyTimes };
      const recommendations = getRecommendedPrograms(searchParams);
      setManualList(recommendations);
      setHasSearched(true);
      setExpandedIndex(null);
    } catch (error) {
      console.error("Error generating recommendations:", error);
    }
  };

  const toggleDay = (day) => setBusyDays((prev) => ({ ...prev, [day]: !prev[day] }));
  const toggleTime = (timeSlot) => setBusyTimes((prev) => ({ ...prev, [timeSlot]: !prev[timeSlot] }));

  // --- AGENT HANDLERS ---
  const handleCommandSubmit = async (e) => {
    e.preventDefault();
    if (!keyword.trim() || isProcessing) return;

    const userCommand = keyword;
    setFeed(prev => [...prev, { type: "user-command", content: userCommand }]);
    setKeyword("");
    setIsProcessing(true);
    setCurrentAgentStep(1); 

    try {
      const response = await fetch("http://127.0.0.1:8000/api/extract-intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userCommand }),
      });

      if (!response.ok) throw new Error("API Connection Failed");
      const extractedData = await response.json();
      
      setTimeout(() => {
        // Handle Out of Scope
        if (extractedData.is_relevant === false) {
            setIsProcessing(false);
            setCurrentAgentStep(0);
            setFeed(prev => [...prev, { 
                type: "agent-text", 
                content: "I am specifically designed to function as an Educational Scheduling Agent. I can help you find courses, build a schedule, and filter programs based on your availability. Please provide a request related to your educational planning." 
            }]);
            return;
        }

        // Merge Memory
        const updatedMemory = { ...agentMemory };
        if (extractedData.selectedProgram) updatedMemory.selectedProgram = extractedData.selectedProgram;
        if (extractedData.busyDays && Object.keys(extractedData.busyDays).length > 0) {
            updatedMemory.busyDays = { ...updatedMemory.busyDays, ...extractedData.busyDays };
        }
        if (extractedData.busyTimes && Object.keys(extractedData.busyTimes).length > 0) {
            updatedMemory.busyTimes = { ...updatedMemory.busyTimes, ...extractedData.busyTimes };
        }
        setAgentMemory(updatedMemory);

        // Check if we need program
        if (!updatedMemory.selectedProgram) {
            setIsSearchingContext(false);
            setCurrentAgentStep(4); 
            setTimeout(() => {
                setIsProcessing(false);
                setCurrentAgentStep(0);
                setFeed(prev => [...prev, { 
                    type: "agent-text", 
                    content: "I have updated your scheduling constraints in my active memory. However, I still need to know: Which specific program or subject are you interested in studying?" 
                }]);
            }, 1000);
            return;
        }

        // Proceed Full Search
        setIsSearchingContext(true);
        setCurrentAgentStep(2);
        
        setTimeout(() => {
          setCurrentAgentStep(3);
          const profile = load("UserProfile") || {};
          const searchParams = { ...profile, ...updatedMemory };
          const results = getRecommendedPrograms(searchParams);

          setTimeout(() => {
            setCurrentAgentStep(4);
            setTimeout(() => {
              setIsProcessing(false);
              setCurrentAgentStep(0);
              
              if (results.length === 0) {
                setFeed(prev => [...prev, { 
                  type: "agent-text", 
                  content: `Analysis complete. I scanned the database for '${updatedMemory.selectedProgram}' with your current time constraints, but could not resolve a valid schedule. Consider relaxing your availability.` 
                }]);
              } else {
                setFeed(prev => [...prev, { 
                  type: "agent-text", 
                  content: `Resolution successful. I synthesized optimal schedule(s) for '${updatedMemory.selectedProgram}'. Review the generated artifacts below:` 
                }]);
                setFeed(prev => [...prev, { type: "artifact", data: results }]);
              }
            }, 1200); 
          }, 1500); 
        }, 1200); 
      }, 1000); 

    } catch (error) {
      setIsProcessing(false);
      setCurrentAgentStep(0);
      setFeed(prev => [...prev, { type: "agent-text", content: "System Error: Connection to the primary reasoning engine failed. Verify backend services." }]);
    }
  };

  const handleSavePlan = (planData) => {
    const existingPlans = load("SavedPlans") || [];
    const newPlan = { id: Date.now(), date: new Date().toLocaleDateString(), program: planData[0]?.program || "Agent Plan", results: planData };
    save("SavedPlans", [...existingPlans, newPlan]);
    if(mode === 'agent') {
      setFeed(prev => [...prev, { type: "agent-text", content: "Action executed. The selected artifact has been saved to your secure profile." }]);
    } else {
      alert("Plan Saved Successfully!");
    }
  };

  const handleClearContext = () => {
    setAgentMemory({ selectedProgram: "", busyDays: {}, busyTimes: {} });
    setFeed([{ type: "agent-text", content: "Active memory flushed. Session cleared. Awaiting new scheduling directives." }]);
  };

  const hasActiveFilters = agentMemory.selectedProgram || Object.keys(agentMemory.busyDays).length > 0 || Object.keys(agentMemory.busyTimes).length > 0;

  // ==========================================
  // RENDER: ENTRY SELECTION SCREEN
  // ==========================================
  if (mode === null) {
  return (
    <div className="min-h-[calc(100vh-80px)] bg-gradient-to-b from-blue-50 via-white to-blue-100 flex items-center justify-center p-6 md:p-10">
      <div className="max-w-7xl w-full">

        {/* Header */}
        <div className="text-center mb-16">
          <span className="inline-flex items-center px-5 py-2 rounded-full bg-blue-100 text-blue-700 font-semibold text-sm border border-blue-200">
            🎓 Smart Academic Planner
          </span>

          <h1 className="mt-6 text-5xl md:text-7xl font-black text-slate-900 leading-tight">
            Student Schedule
            <span className="block text-blue-600">
              Planning Assistant
            </span>
          </h1>

          <p className="mt-6 text-lg text-slate-600 max-w-3xl mx-auto">
            Choose how you would like to create your academic schedule.
            Build it manually or let AI generate the best timetable for you.
          </p>
        </div>

        {/* Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">

          {/* Manual Builder */}
          <div
            onClick={() => setMode("manual")}
            className="group relative overflow-hidden rounded-[32px] bg-white border border-blue-100 p-10 cursor-pointer shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-500"
          >
            {/* Glow */}
            <div className="absolute top-0 right-0 w-56 h-56 bg-blue-100 rounded-full blur-3xl opacity-60" />

            {/* Icon */}
            <div className="relative w-24 h-24 rounded-3xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-xl mb-8 group-hover:rotate-6 transition-all duration-500">
              <svg
                className="w-12 h-12 text-white"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                viewBox="0 0 24 24"
              >
                <path d="M4 6h16M4 12h16M4 18h10" />
              </svg>
            </div>

            <span className="inline-flex px-4 py-2 rounded-full bg-blue-50 text-blue-700 text-sm font-semibold border border-blue-100">
              Traditional Method
            </span>

            <h2 className="mt-6 text-3xl font-bold text-slate-900">
              Manual Builder
            </h2>

            <p className="mt-4 text-slate-600 text-lg leading-relaxed">
              Select courses, free days, timings and preferences manually.
              Perfect for students who want complete control over their
              timetable.
            </p>

            <div className="mt-8 flex items-center text-blue-600 font-bold text-lg">
              Create Manually
              <span className="ml-2 group-hover:translate-x-2 transition-transform">
                →
              </span>
            </div>
          </div>

          {/* AI Builder */}
          <div
            onClick={() => setMode("agent")}
            className="group relative overflow-hidden rounded-[32px] bg-gradient-to-br from-blue-600 via-blue-700 to-blue-900 p-10 cursor-pointer shadow-xl hover:shadow-2xl hover:-translate-y-2 transition-all duration-500"
          >
            {/* Background Effects */}
            <div className="absolute -top-20 -right-20 w-72 h-72 bg-white/10 rounded-full blur-3xl"></div>

            {/* Robot */}
            <div className="flex justify-center mb-8">
              <div className="relative">

                {/* Antenna */}
                <div className="absolute -top-5 left-1/2 -translate-x-1/2">
                  <div className="w-1 h-5 bg-white"></div>
                  <div className="w-4 h-4 rounded-full bg-white animate-pulse"></div>
                </div>

                {/* Head */}
                <div className="w-32 h-32 rounded-[30px] bg-white shadow-2xl flex items-center justify-center group-hover:scale-110 transition-all duration-500">

                  <div>

                    {/* Eyes */}
                    <div className="flex justify-center gap-5 mb-4">
                      <div className="w-4 h-4 bg-blue-600 rounded-full animate-pulse"></div>
                      <div className="w-4 h-4 bg-blue-600 rounded-full animate-pulse"></div>
                    </div>

                    {/* Mouth */}
                    <div className="w-10 h-2 bg-blue-500 rounded-full mx-auto"></div>

                  </div>
                </div>

                {/* Side Ears */}
                <div className="absolute top-10 -left-3 w-3 h-8 rounded-full bg-white"></div>
                <div className="absolute top-10 -right-3 w-3 h-8 rounded-full bg-white"></div>

              </div>
            </div>

            <div className="text-center">

              <span className="inline-flex px-4 py-2 rounded-full bg-white/20 text-white text-sm font-semibold border border-white/20">
                AI Powered
              </span>

              <h2 className="mt-6 text-3xl font-bold text-white">
                AI Schedule Agent
              </h2>

              <p className="mt-4 text-blue-100 text-lg leading-relaxed">
                Tell the AI your requirements in simple language and receive
                a fully optimized academic timetable instantly.
              </p>

              <div className="mt-8 flex justify-center items-center text-white font-bold text-lg">
                Generate with Help of AI agent
                <span className="ml-2 group-hover:translate-x-2 transition-transform">
                  ✨
                </span>
              </div>

            </div>
          </div>

        </div>

      </div>
    </div>
  );
}

  // ==========================================
  // RENDER: MANUAL SCREEN
  // ==========================================
  if (mode === 'manual') {
    return (
      <div className="min-h-[calc(100vh-80px)] bg-slate-50 p-6 md:p-12">
        <div className="max-w-5xl mx-auto">
          
          <button onClick={() => setMode(null)} className="flex items-center gap-2 text-slate-500 hover:text-slate-900 font-bold mb-8 transition-colors">
            <Icons.Back /> Switch to AI Agent
          </button>

          <header className="mb-10">
            <h2 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-3">Manual Schedule Builder</h2>
            <p className="text-lg text-slate-600">Filter programs by your interest and work schedule to find the perfect fit.</p>
          </header>

          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm mb-10">
            <div className="mb-8">
              <label className="block font-semibold text-lg mb-3 text-slate-800">1. Which program are you interested in?</label>
              <select 
                value={selectedProgram} 
                onChange={(e) => setSelectedProgram(e.target.value)}
                className="w-full md:w-1/2 p-3 border border-slate-300 rounded-lg bg-slate-50 focus:ring-2 focus:ring-[#016ce6] focus:border-[#016ce6] outline-none font-medium text-slate-700"
              >
                {programOptions.map((prog, idx) => (
                  <option key={idx} value={prog}>{prog}</option>
                ))}
              </select>
            </div>

            <div className="mb-8">
              <label className="block font-semibold text-lg mb-3 text-slate-800">2. Select the days you are BUSY:</label>
              <div className="flex flex-wrap gap-3">
                {Object.keys(busyDays).map((day) => (
                  <button
                    key={day}
                    onClick={() => toggleDay(day)}
                    className={clsx(
                      "px-6 py-2.5 rounded-xl font-bold transition-all duration-200 border",
                      busyDays[day] ? "bg-slate-900 text-white border-slate-900 shadow-md" : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
                    )}
                  >
                    {day}
                  </button>
                ))}
              </div>
            </div>

            <div className="mb-8">
              <label className="block font-semibold text-lg mb-3 text-slate-800">3. Select the time slots you are BUSY:</label>
              <div className="flex flex-wrap gap-3">
                <button onClick={() => toggleTime('morning')} className={clsx("px-6 py-2.5 rounded-xl font-bold transition-all border", busyTimes.morning ? "bg-slate-900 text-white border-slate-900" : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50")}>Morning (8 AM - 12 PM)</button>
                <button onClick={() => toggleTime('afternoon')} className={clsx("px-6 py-2.5 rounded-xl font-bold transition-all border", busyTimes.afternoon ? "bg-slate-900 text-white border-slate-900" : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50")}>Afternoon (12 PM - 4 PM)</button>
                <button onClick={() => toggleTime('evening')} className={clsx("px-6 py-2.5 rounded-xl font-bold transition-all border", busyTimes.evening ? "bg-slate-900 text-white border-slate-900" : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50")}>Evening (4 PM+)</button>
              </div>
            </div>

            <button 
              onClick={handleManualSearch}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3.5 rounded-xl font-bold text-lg transition-colors w-full md:w-auto shadow-sm flex items-center justify-center gap-2"
            >
              <Icons.Sparkles /> Generate Recommendations
            </button>
          </div>

          <div className="grid gap-6">
            {hasSearched && manualList.length === 0 && (
              <div className="p-8 bg-amber-50 text-amber-800 rounded-3xl border border-amber-200 flex flex-col items-center text-center">
                <span className="text-4xl mb-3">⚠️</span>
                <h3 className="text-xl font-bold mb-2">No Match Found</h3>
                <p className="max-w-lg font-medium">It looks like your busy schedule conflicts with all available classes. Try freeing up some days, or select another program.</p>
              </div>
            )}
            {manualList.length > 0 && manualList.map((prog, i) => (
              <ManualResultCard key={i} prog={prog} expandedIndex={expandedIndex} setExpandedIndex={setExpandedIndex} i={i} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ==========================================
  // RENDER: AGENT SCREEN
  // ==========================================
  if (mode === 'agent') {
    return (
      <div className="flex flex-col h-[calc(100vh-80px)] w-full bg-[#fafafa] font-sans selection:bg-blue-100">
        <header className="w-full bg-white px-6 py-4 flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200/60 sticky top-0 z-20 gap-4">
          <div className="flex items-center gap-4">
            <button onClick={() => setMode(null)} className="text-slate-400 hover:text-slate-900 transition-colors mr-2" title="Back to Selection">
              <Icons.Back />
            </button>
            <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center text-white shadow-sm">
              <Icons.Sparkles />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800 tracking-tight leading-none">EdPlan Reasoning Agent</h2>
              <div className="flex items-center gap-1.5 mt-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">System Active</span>
              </div>
            </div>
          </div>
          <button 
            onClick={handleClearContext} 
            className="text-xs font-bold text-slate-400 hover:text-slate-800 transition-colors uppercase tracking-wider self-start md:self-auto"
          >
            Reset Context & Session
          </button>
        </header>

        <div className="flex-1 overflow-y-auto w-full flex justify-center py-10 px-4 md:px-0">
          <div className="w-full max-w-3xl space-y-8">
            {feed.map((block, index) => (
              <div key={index} className="animate-fade-in-up">
                {block.type === "user-command" && (
                  <div className="flex items-start gap-4">
                    <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-500 text-xs flex-shrink-0 uppercase">You</div>
                    <div className="pt-1"><p className="text-lg font-medium text-slate-800 leading-relaxed">{block.content}</p></div>
                  </div>
                )}
                {block.type === "agent-text" && (
                  <div className="flex items-start gap-4">
                    <div className="w-8 h-8 rounded-md bg-blue-600 flex items-center justify-center text-white flex-shrink-0 shadow-sm mt-1"><Icons.Brain /></div>
                    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm w-full"><p className="text-slate-700 font-medium leading-relaxed">{block.content}</p></div>
                  </div>
                )}
                {block.type === "artifact" && (
                  <div className="pl-12 w-full">
                    <div className="mb-3 flex items-center gap-2">
                      <span className="h-[1px] flex-1 bg-slate-200"></span>
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Generated Artifacts</span>
                      <span className="h-[1px] flex-1 bg-slate-200"></span>
                    </div>
                    {block.data.map((prog, i) => <AgentScheduleArtifact key={i} prog={prog} handleSavePlan={handleSavePlan} />)}
                  </div>
                )}
              </div>
            ))}
            {isProcessing && <div className="pl-12"><AgentWorkflow currentStep={currentAgentStep} isSearching={isSearchingContext} /></div>}
            <div ref={feedEndRef} className="h-32" />
          </div>
        </div>

        <div className="w-full flex flex-col items-center fixed bottom-0 left-0 px-4 pb-6 bg-gradient-to-t from-[#fafafa] via-[#fafafa] to-transparent pointer-events-none">
          {hasActiveFilters && (
            <div className="w-full max-w-3xl flex gap-2 mb-2 px-2 overflow-x-auto scrollbar-hide pointer-events-auto">
               <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-widest mr-2"><Icons.Filter /> Active Context:</div>
               {agentMemory.selectedProgram && <span className="bg-blue-100 text-blue-700 px-2.5 py-1 rounded-md text-xs font-bold whitespace-nowrap">🎯 {agentMemory.selectedProgram}</span>}
               {Object.keys(agentMemory.busyDays).length > 0 && <span className="bg-rose-100 text-rose-700 px-2.5 py-1 rounded-md text-xs font-bold whitespace-nowrap">🚫 Days: {Object.keys(agentMemory.busyDays).join(", ")}</span>}
               {Object.keys(agentMemory.busyTimes).length > 0 && <span className="bg-amber-100 text-amber-700 px-2.5 py-1 rounded-md text-xs font-bold whitespace-nowrap">🕒 Times: {Object.keys(agentMemory.busyTimes).join(", ")}</span>}
            </div>
          )}
          <div className="w-full max-w-3xl bg-white rounded-2xl shadow-[0_10px_40px_rgba(0,0,0,0.1)] border border-slate-200 p-2 pointer-events-auto transition-all focus-within:shadow-[0_10px_50px_rgba(37,99,235,0.15)] focus-within:border-blue-400 ring-1 ring-black/5">
            <form onSubmit={handleCommandSubmit} className="flex items-center gap-2 relative">
              <div className="pl-4 text-slate-400"><Icons.Sparkles /></div>
              <input type="text" value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="E.g., Map out an Art plan, or exclude Monday mornings..." className="flex-1 bg-transparent px-2 py-3 font-medium text-slate-700 placeholder-slate-400 outline-none w-full text-base" autoFocus disabled={isProcessing} autoComplete="off"/>
              <button type="submit" disabled={isProcessing || !keyword.trim()} className="bg-slate-900 hover:bg-blue-600 disabled:bg-slate-200 disabled:text-slate-400 text-white px-5 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2">Execute</button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default RecommendationPage; 