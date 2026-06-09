import { useState, useEffect, useRef } from "react";
import { load, save } from "../utils/storage";
import { getRecommendedPrograms } from "../utils/recommendationEngine";
import clsx from "clsx";

// --- Icons (SVG) ---
const Icons = {
  Brain: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5A3 3 0 0 0 13.6 4.4"/><path d="M6.401 6.5A3 3 0 0 1 10.4 4.4"/></svg>,
  Database: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>,
  Calendar: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>,
  Sparkles: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>,
  Check: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>,
  Loader: () => <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" x2="12" y1="2" y2="6"/><line x1="12" x2="12" y1="18" y2="22"/><line x1="4.93" x2="7.76" y1="4.93" y2="7.76"/><line x1="16.24" x2="19.07" y1="16.24" y2="19.07"/><line x1="2" x2="6" y1="12" y2="12"/><line x1="18" x2="22" y1="12" y2="12"/><line x1="4.93" x2="7.76" y1="19.07" y2="16.24"/><line x1="16.24" x2="19.07" y1="7.76" y2="4.93"/></svg>,
  Filter: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
};

// --- Agentic Workflow Visualizer Component ---
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

// --- Generated Artifact (Schedule Card) ---
const ScheduleArtifact = ({ prog }) => {
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
      </div>
    </div>
  );
};

// --- Main Agentic Scheduler App ---
const RecommendationPage = () => {
  const [feed, setFeed] = useState([]); 
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentAgentStep, setCurrentAgentStep] = useState(0);
  const [isSearchingContext, setIsSearchingContext] = useState(true);
  const [keyword, setKeyword] = useState("");
  const feedEndRef = useRef(null);

  // --- MEMORY STATE: Agent ab context yaad rakhega ---
  const [agentMemory, setAgentMemory] = useState({
    selectedProgram: "",
    busyDays: {},
    busyTimes: {}
  });

  useEffect(() => {
    feedEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [feed, currentAgentStep]);

  useEffect(() => {
    const profile = load("UserProfile") || {};
    const name = profile.firstName || "User";
    
    setFeed([
      { 
        type: "agent-text", 
        content: `System initialized. Welcome, ${name}. I am the EdPlan Scheduling Agent. My core function is to generate optimal learning pathways based on your subject interests and scheduling constraints. How may I assist you today?` 
      }
    ]);
  }, []);

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
        // Handle Out of Scope / General Chat
        if (extractedData.is_relevant === false) {
            setIsProcessing(false);
            setCurrentAgentStep(0);
            setFeed(prev => [...prev, { 
                type: "agent-text", 
                content: "I am specifically designed to function as an Educational Scheduling Agent. I can help you find courses, build a schedule, and filter programs based on your availability. Please provide a request related to your educational planning." 
            }]);
            return;
        }

        // --- MERGE MEMORY (Update Context) ---
        const updatedMemory = { ...agentMemory };
        if (extractedData.selectedProgram) updatedMemory.selectedProgram = extractedData.selectedProgram;
        if (extractedData.busyDays && Object.keys(extractedData.busyDays).length > 0) {
            updatedMemory.busyDays = { ...updatedMemory.busyDays, ...extractedData.busyDays };
        }
        if (extractedData.busyTimes && Object.keys(extractedData.busyTimes).length > 0) {
            updatedMemory.busyTimes = { ...updatedMemory.busyTimes, ...extractedData.busyTimes };
        }
        setAgentMemory(updatedMemory);

        // Check if we have enough info to search (We need a program)
        if (!updatedMemory.selectedProgram) {
            setIsSearchingContext(false);
            setCurrentAgentStep(4); // Skip to end of short workflow
            
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

        // If we have a program, proceed with full search
        setIsSearchingContext(true);
        setCurrentAgentStep(2);
        
        setTimeout(() => {
          setCurrentAgentStep(3);
          const profile = load("UserProfile") || {};
          const searchParams = { ...profile, ...updatedMemory }; // Use Merged Memory!
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
      console.error(error);
      setIsProcessing(false);
      setCurrentAgentStep(0);
      setFeed(prev => [...prev, { type: "agent-text", content: "System Error: Connection to the primary reasoning engine failed. Verify backend services." }]);
    }
  };

  const handleSavePlan = (planData) => {
    const existingPlans = load("SavedPlans") || [];
    const newPlan = { id: Date.now(), date: new Date().toLocaleDateString(), program: planData[0]?.program || "Agent Plan", results: planData };
    save("SavedPlans", [...existingPlans, newPlan]);
    setFeed(prev => [...prev, { type: "agent-text", content: "Action executed. The selected artifact has been saved to your secure profile." }]);
  };

  const handleClearContext = () => {
    setAgentMemory({ selectedProgram: "", busyDays: {}, busyTimes: {} });
    setFeed([{ type: "agent-text", content: "Active memory flushed. Session cleared. Awaiting new scheduling directives." }]);
  };

  // Helper to render active filters
  const hasActiveFilters = agentMemory.selectedProgram || Object.keys(agentMemory.busyDays).length > 0 || Object.keys(agentMemory.busyTimes).length > 0;

  return (
    <div className="flex flex-col h-screen w-full bg-[#fafafa] font-sans selection:bg-blue-100">
      
      {/* Sleek Agent Header */}
      <header className="w-full bg-white px-6 py-4 flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200/60 sticky top-0 z-20 gap-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center text-white shadow-sm">
            <Icons.Sparkles />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-800 tracking-tight leading-none">EdPlan Scheduling Agent</h2>
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

      {/* Execution Feed */}
      <div className="flex-1 overflow-y-auto w-full flex justify-center py-10 px-4 md:px-0">
        <div className="w-full max-w-3xl space-y-8">
          
          {feed.map((block, index) => (
            <div key={index} className="animate-fade-in-up">
              
              {/* User Command Block */}
              {block.type === "user-command" && (
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-500 text-xs flex-shrink-0 uppercase">You</div>
                  <div className="pt-1">
                    <p className="text-lg font-medium text-slate-800 leading-relaxed">{block.content}</p>
                  </div>
                </div>
              )}

              {/* Agent Text Block */}
              {block.type === "agent-text" && (
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded-md bg-blue-600 flex items-center justify-center text-white flex-shrink-0 shadow-sm mt-1">
                    <Icons.Brain />
                  </div>
                  <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm w-full">
                    <p className="text-slate-700 font-medium leading-relaxed">{block.content}</p>
                  </div>
                </div>
              )}

              {/* Generated Artifacts (Results) */}
              {block.type === "artifact" && (
                <div className="pl-12 w-full">
                  <div className="mb-3 flex items-center gap-2">
                    <span className="h-[1px] flex-1 bg-slate-200"></span>
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Generated Artifacts</span>
                    <span className="h-[1px] flex-1 bg-slate-200"></span>
                  </div>
                  {block.data.map((prog, i) => <ScheduleArtifact key={i} prog={prog} />)}
                  
                  <div className="flex justify-end mt-2">
                    <button 
                      onClick={() => handleSavePlan(block.data)}
                      className="flex items-center gap-2 bg-white border border-slate-200 hover:border-slate-400 text-slate-700 px-4 py-2 rounded-lg text-sm font-bold shadow-sm transition-all"
                    >
                      <Icons.Check /> Accept & Save Plan
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Active Processing State */}
          {isProcessing && (
            <div className="pl-12">
              <AgentWorkflow currentStep={currentAgentStep} isSearching={isSearchingContext} />
            </div>
          )}
          
          <div ref={feedEndRef} className="h-32" />
        </div>
      </div>

      {/* Persistent Command Bar with Active Context */}
      <div className="w-full flex flex-col items-center fixed bottom-0 left-0 px-4 pb-6 bg-gradient-to-t from-[#fafafa] via-[#fafafa] to-transparent pointer-events-none">
        
        {/* Active Memory Chips */}
        {hasActiveFilters && (
          <div className="w-full max-w-3xl flex gap-2 mb-2 px-2 overflow-x-auto scrollbar-hide">
             <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-widest mr-2">
                <Icons.Filter /> Active Context:
             </div>
             {agentMemory.selectedProgram && (
               <span className="bg-blue-100 text-blue-700 px-2.5 py-1 rounded-md text-xs font-bold whitespace-nowrap">
                 🎯 {agentMemory.selectedProgram}
               </span>
             )}
             {Object.keys(agentMemory.busyDays).length > 0 && (
               <span className="bg-rose-100 text-rose-700 px-2.5 py-1 rounded-md text-xs font-bold whitespace-nowrap">
                 🚫 Days: {Object.keys(agentMemory.busyDays).join(", ")}
               </span>
             )}
             {Object.keys(agentMemory.busyTimes).length > 0 && (
               <span className="bg-amber-100 text-amber-700 px-2.5 py-1 rounded-md text-xs font-bold whitespace-nowrap">
                 🕒 Times: {Object.keys(agentMemory.busyTimes).join(", ")}
               </span>
             )}
          </div>
        )}

        {/* Input Box */}
        <div className="w-full max-w-3xl bg-white rounded-2xl shadow-[0_10px_40px_rgba(0,0,0,0.1)] border border-slate-200 p-2 pointer-events-auto transition-all focus-within:shadow-[0_10px_50px_rgba(37,99,235,0.15)] focus-within:border-blue-400 ring-1 ring-black/5">
          <form onSubmit={handleCommandSubmit} className="flex items-center gap-2 relative">
            <div className="pl-4 text-slate-400">
              <Icons.Sparkles />
            </div>
            <input 
              type="text" 
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="E.g., Map out an Art plan, or exclude Monday mornings..." 
              className="flex-1 bg-transparent px-2 py-3 font-medium text-slate-700 placeholder-slate-400 outline-none w-full text-base"
              autoFocus
              disabled={isProcessing}
              autoComplete="off"
            />
            <button 
              type="submit" 
              disabled={isProcessing || !keyword.trim()}
              className="bg-slate-900 hover:bg-blue-600 disabled:bg-slate-200 disabled:text-slate-400 text-white px-5 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2"
            >
              Execute
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RecommendationPage;