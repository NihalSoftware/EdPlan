import { useState, useEffect, useRef } from "react";
import { load } from "../utils/storage";
import { getRecommendedPrograms, getProgramList } from "../utils/recommendationEngine";
import clsx from "clsx";

// --- Sub-Component: Individual Result Card ---
const ResultCard = ({ prog }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeYearIndex, setActiveYearIndex] = useState(0);

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm mb-4 overflow-hidden">
      <div className="p-5 flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-xl font-bold text-slate-900">{prog.program || "Unknown Program"}</h3>
            <span className="bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wide">
              {prog.degree || "Degree"}
            </span>
          </div>
          <p className="text-slate-600 font-medium mb-3 text-sm">{prog.university || "University not specified"}</p>
          
          <div className="flex flex-wrap gap-3 text-xs text-slate-500 mb-3">
            <span className="bg-slate-100 px-2 py-1 rounded-md">⏱ Credits: {prog.total_credit_hours || "N/A"}</span>
            <span className="bg-slate-100 px-2 py-1 rounded-md">💸 {prog.average_annual_cost ? `${prog.average_annual_cost.split(' ')[0]}/yr` : "Cost N/A"}</span>
          </div>
        </div>
        
        <div className="flex flex-col items-end gap-2 min-w-[140px]">
          <div className="bg-green-50 border border-green-200 text-green-700 px-3 py-1.5 rounded-lg text-center shadow-sm w-full text-xs font-bold">
            Perfect Match ✓
          </div>
          <button 
            onClick={() => { setIsExpanded(!isExpanded); setActiveYearIndex(0); }}
            className="w-full text-center px-3 py-1.5 border border-[#016ce6] text-[#016ce6] hover:bg-[#016ce6] hover:text-white rounded-lg text-sm font-semibold transition"
          >
            {isExpanded ? "Hide ⬆" : "Details ⬇"}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="p-5 border-t border-slate-200 bg-slate-50 animate-fade-in">
          {/* ... (College Profile aur Curriculum wala code same rahega) ... */}
          {prog.college_profile && (
            <div className="mb-6 bg-white p-4 rounded-xl border border-slate-200">
              <h4 className="text-sm font-bold text-slate-800 border-b pb-2 mb-3">🏫 College Profile</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-700">
                <p><strong>Size:</strong> {prog.college_profile.size || "N/A"}</p>
                <p><strong>Acceptance:</strong> {prog.college_profile.acceptance_rate || "N/A"}</p>
                <p><strong>Earnings:</strong> {prog.college_profile.median_earnings || "N/A"}</p>
              </div>
            </div>
          )}

          {prog.years && prog.years.length > 0 && (
            <div>
              <div className="flex flex-wrap gap-2 mb-4">
                {prog.years.map((yearData, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveYearIndex(idx)}
                    className={clsx(
                      "px-3 py-1.5 rounded-lg font-semibold text-xs transition-colors",
                      activeYearIndex === idx ? "bg-[#016ce6] text-white shadow-md" : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                    )}
                  >
                    {yearData.year}
                  </button>
                ))}
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm animate-fade-in">
                <h5 className="text-sm font-bold text-[#016ce6] mb-3">{prog.years[activeYearIndex].year} Schedule</h5>
                <div className="space-y-4">
                  {prog.years[activeYearIndex].semesters?.map((sem, sIdx) => (
                    <div key={sIdx}>
                      <h6 className="font-semibold text-slate-700 mb-2 bg-slate-100 px-2 py-1 rounded text-xs inline-block">
                        {sem.semester} Sem ({sem.total_credits} Cr)
                      </h6>
                      <ul className="space-y-2">
                        {sem.courses?.map((course, cIdx) => (
                          <li key={cIdx} className="text-xs p-3 border border-slate-100 rounded-lg bg-slate-50">
                            <div className="font-bold text-slate-800 mb-1">
                              {course.code}: {course.name} <span className="text-slate-500 font-normal">({course.credits} Cr)</span>
                            </div>
                            <div className="flex gap-2 mt-1">
                              <span className="bg-white px-2 py-0.5 border border-slate-200 rounded shadow-sm font-medium">
                                🕒 {course.schedule?.day || "TBD"} | {course.schedule?.time || "TBD"}
                              </span>
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
  );
};

// --- Main Chatbot Page ---
const RecommendationPage = () => {
  const [messages, setMessages] = useState([]);
  const [step, setStep] = useState(1); // 1: Search Text, 1.5: Pick Program, 2: Days, 3: Times, 4: Done
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  // Search aur filtering states
  const [keyword, setKeyword] = useState("");
  const [filteredPrograms, setFilteredPrograms] = useState([]);
  const allPrograms = getProgramList();

  const [userInputs, setUserInputs] = useState({
    selectedProgram: "",
    busyDays: { Mon: false, Tue: false, Wed: false, Thu: false, Fri: false },
    busyTimes: { morning: false, afternoon: false, evening: false }
  });

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping, step]);

  // Initial Greeting
  useEffect(() => {
    const profile = load("UserProfile") || {};
    const name = profile.firstName || "there";
    
    setMessages([
      { sender: "bot", type: "text", text: `Hi ${name}! 👋 I am your AI Education Planner.` },
      { sender: "bot", type: "text", text: "What field of study or program are you looking for? (e.g., 'Computer', 'Nursing', 'Business')" }
    ]);
  }, []);

  const addBotMessage = (text, delay = 600) => {
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setMessages(prev => [...prev, { sender: "bot", type: "text", text }]);
    }, delay);
  };

  const addUserMessage = (text) => {
    setMessages(prev => [...prev, { sender: "user", type: "text", text }]);
  };

  // --- Step 1: Handle Search Text Input ---
  const handleKeywordSubmit = (e) => {
    e.preventDefault();
    if (!keyword.trim()) return;

    addUserMessage(keyword);
    setKeyword("");
    setIsTyping(true);

    setTimeout(() => {
      setIsTyping(false);
      // Search program list based on keyword
      const matches = allPrograms.filter(prog => 
        prog.toLowerCase().includes(keyword.toLowerCase()) && prog !== "All Programs"
      );

      if (matches.length > 0) {
        setFilteredPrograms(matches);
        setStep(1.5);
        setMessages(prev => [...prev, { 
          sender: "bot", 
          type: "text", 
          text: `I found ${matches.length} matching program(s). Please select one from the options below:` 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          sender: "bot", 
          type: "text", 
          text: "I couldn't find any programs matching that keyword. Could you try a different word?" 
        }]);
      }
    }, 600);
  };

  // --- Step 1.5: Program Selection ---
  const handleProgramSelect = (prog) => {
    setUserInputs(prev => ({ ...prev, selectedProgram: prog }));
    addUserMessage(prog);
    setStep(2);
    addBotMessage("Great choice! Now, tell me which days you are BUSY (working or unavailable)?");
  };

  // --- Step 2: Days Selection ---
  const toggleDay = (day) => {
    setUserInputs(prev => ({
      ...prev, busyDays: { ...prev.busyDays, [day]: !prev.busyDays[day] }
    }));
  };

  const submitDays = () => {
    const selected = Object.keys(userInputs.busyDays).filter(d => userInputs.busyDays[d]);
    const replyText = selected.length > 0 ? selected.join(", ") : "I'm free all week!";
    addUserMessage(replyText);
    setStep(3);
    
    if (selected.length === 0) {
      analyzeResults({ ...userInputs, busyDays: {} });
    } else {
      addBotMessage("Got it. And what time slots are you BUSY on those days?");
    }
  };

  // --- Step 3: Times Selection ---
  const toggleTime = (timeSlot) => {
    setUserInputs(prev => ({
      ...prev, busyTimes: { ...prev.busyTimes, [timeSlot]: !prev.busyTimes[timeSlot] }
    }));
  };

  const submitTimes = () => {
    const selected = Object.keys(userInputs.busyTimes).filter(t => userInputs.busyTimes[t]);
    const replyText = selected.length > 0 ? selected.join(", ") : "Any time works for me!";
    addUserMessage(replyText);
    setStep(4);
    analyzeResults(userInputs);
  };

  // --- Final Step: Generate Results ---
  const analyzeResults = (finalInputs) => {
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setMessages(prev => [...prev, { sender: "bot", type: "text", text: "Analyzing schedules and your availability... 🔍" }]);
      
      setTimeout(() => {
        try {
          const profile = load("UserProfile") || {};
          const searchParams = { ...profile, ...finalInputs };
          const results = getRecommendedPrograms(searchParams);
          
          if (results.length === 0) {
            setMessages(prev => [...prev, { sender: "bot", type: "text", text: "⚠️ I couldn't find any classes that perfectly match this schedule. You might need to free up some days." }]);
          } else {
            setMessages(prev => [...prev, { sender: "bot", type: "text", text: `I found ${results.length} perfect match(es) for you! Here they are:` }]);
            setMessages(prev => [...prev, { sender: "bot", type: "results", data: results }]);
          }
          setStep(5);
        } catch (error) {
          console.error(error);
        }
      }, 1000);
    }, 800);
  };

  const restartChat = () => {
    setMessages([{ sender: "bot", type: "text", text: "Let's start over! What field of study are you looking for?" }]);
    setUserInputs({
      selectedProgram: "",
      busyDays: { Mon: false, Tue: false, Wed: false, Thu: false, Fri: false },
      busyTimes: { morning: false, afternoon: false, evening: false }
    });
    setStep(1);
    setKeyword("");
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-80px)] flex flex-col bg-slate-50 font-sans shadow-xl border-x border-slate-200">
      
      {/* Header */}
      <header className="bg-white p-5 border-b border-slate-200 flex items-center justify-between shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#016ce6] rounded-full flex items-center justify-center text-white font-bold text-xl shadow-inner">
            AI
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-800">EdPlan Scheduler Agent</h2>
            <p className="text-xs text-green-600 font-medium flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> Online
            </p>
          </div>
        </div>
        {step > 1 && (
          <button onClick={restartChat} className="text-sm font-semibold text-slate-500 hover:text-[#016ce6] transition bg-slate-100 px-3 py-1.5 rounded-lg">
            🔄 Restart
          </button>
        )}
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 bg-[#f0f2f5] scroll-smooth custom-scrollbar">
        {messages.map((msg, index) => (
          <div key={index} className={clsx("flex", msg.sender === "user" ? "justify-end" : "justify-start")}>
            {msg.sender === "bot" && msg.type !== "results" && (
               <div className="w-8 h-8 rounded-full bg-[#016ce6] text-white flex items-center justify-center text-xs font-bold mr-2 mt-1 flex-shrink-0">AI</div>
            )}
            
            <div className={clsx(
              "max-w-[85%] md:max-w-[75%]",
              msg.sender === "user" 
                ? "bg-[#016ce6] text-white rounded-2xl rounded-tr-sm px-5 py-3 shadow-sm" 
                : msg.type === "results" 
                  ? "w-full" 
                  : "bg-white text-slate-800 rounded-2xl rounded-tl-sm px-5 py-3 shadow-sm border border-slate-100"
            )}>
              {msg.type === "text" && <p className="text-sm md:text-base leading-relaxed">{msg.text}</p>}
              
              {msg.type === "results" && (
                <div className="w-full mt-2 animate-fade-in-up">
                  {msg.data.map((prog, i) => <ResultCard key={i} prog={prog} />)}
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start animate-fade-in">
             <div className="w-8 h-8 rounded-full bg-[#016ce6] text-white flex items-center justify-center text-xs font-bold mr-2 mt-1 flex-shrink-0">AI</div>
             <div className="bg-white rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm border border-slate-100 flex gap-1 items-center">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
             </div>
          </div>
        )}
        
        <div ref={chatEndRef} />
      </div>

      {/* Input Area (Strict Height Constraints to Prevent Overflow) */}
      <div className="bg-white border-t border-slate-200 p-4 md:p-5 min-h-[80px] max-h-[35vh] overflow-y-auto">
        
        {/* Step 1: Text Search Input */}
        {step === 1 && !isTyping && (
          <form onSubmit={handleKeywordSubmit} className="flex gap-2 animate-fade-in-up">
            <input 
              type="text" 
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Type a subject (e.g. Science, Art...)" 
              className="flex-1 p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-[#016ce6] focus:border-[#016ce6] outline-none transition"
              autoFocus
            />
            <button type="submit" className="bg-[#016ce6] hover:bg-blue-700 text-white px-6 rounded-xl font-bold transition shadow-sm">
              Send
            </button>
          </form>
        )}

        {/* Step 1.5: Filtered Program Selection (No Overflow now!) */}
        {step === 1.5 && !isTyping && (
           <div className="flex flex-wrap gap-2 animate-fade-in-up">
             {filteredPrograms.map(prog => (
               <button 
                 key={prog} 
                 onClick={() => handleProgramSelect(prog)}
                 className="bg-slate-50 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-300 text-slate-700 px-4 py-2.5 rounded-full text-sm font-semibold transition shadow-sm"
               >
                 {prog}
               </button>
             ))}
             <button 
               onClick={() => setStep(1)}
               className="text-slate-500 underline text-sm ml-2 self-center hover:text-slate-800"
             >
               Search again
             </button>
           </div>
        )}

        {/* Step 2: Days Selection */}
        {step === 2 && !isTyping && (
           <div className="animate-fade-in-up flex flex-col gap-4">
             <div className="flex flex-wrap gap-2">
               {Object.keys(userInputs.busyDays).map((day) => (
                 <button
                   key={day}
                   onClick={() => toggleDay(day)}
                   className={clsx(
                     "px-5 py-2.5 rounded-full font-semibold text-sm transition-all border shadow-sm",
                     userInputs.busyDays[day] ? "bg-[#016ce6] text-white border-[#016ce6] transform scale-[1.02]" : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
                   )}
                 >
                   {day}
                 </button>
               ))}
             </div>
             <button onClick={submitDays} className="self-end bg-[#016ce6] hover:bg-blue-700 text-white px-8 py-2.5 rounded-xl font-bold text-sm shadow-md transition">
               Submit Days ➔
             </button>
           </div>
        )}

        {/* Step 3: Times Selection */}
        {step === 3 && !isTyping && (
           <div className="animate-fade-in-up flex flex-col gap-4">
             <div className="flex flex-wrap gap-2">
                <button onClick={() => toggleTime('morning')} className={clsx("px-5 py-2.5 rounded-full font-semibold text-sm border shadow-sm transition", userInputs.busyTimes.morning ? "bg-[#016ce6] text-white border-[#016ce6]" : "bg-white text-slate-600 border-slate-300")}>Morning (8am-12pm)</button>
                <button onClick={() => toggleTime('afternoon')} className={clsx("px-5 py-2.5 rounded-full font-semibold text-sm border shadow-sm transition", userInputs.busyTimes.afternoon ? "bg-[#016ce6] text-white border-[#016ce6]" : "bg-white text-slate-600 border-slate-300")}>Afternoon (12pm-4pm)</button>
                <button onClick={() => toggleTime('evening')} className={clsx("px-5 py-2.5 rounded-full font-semibold text-sm border shadow-sm transition", userInputs.busyTimes.evening ? "bg-[#016ce6] text-white border-[#016ce6]" : "bg-white text-slate-600 border-slate-300")}>Evening (4pm+)</button>
             </div>
             <button onClick={submitTimes} className="self-end bg-green-600 hover:bg-green-700 text-white px-8 py-2.5 rounded-xl font-bold text-sm shadow-md transition">
               Find Matches 🔍
             </button>
           </div>
        )}

        {step === 5 && (
           <div className="text-center text-slate-500 text-sm font-medium animate-fade-in py-2">
             Mission accomplished! Check your tailored recommendations above.
           </div>
        )}

      </div>
    </div>
  );
};

export default RecommendationPage;