import { useState, useEffect, useRef } from "react";
import { load, save } from "../utils/storage";
import { getRecommendedPrograms, getProgramList } from "../utils/recommendationEngine";
import clsx from "clsx";

// --- Sub-Component: Smart Modern Result Card ---
const ResultCard = ({ prog }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeSemIndex, setActiveSemIndex] = useState(0);

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm mb-5 overflow-hidden transition-all hover:shadow-md w-full">
      <div className="p-6 flex flex-col md:flex-row justify-between items-start gap-5">
        <div className="flex-1 w-full">
          <div className="flex flex-wrap items-center gap-3 mb-2">
            <h3 className="text-xl font-extrabold text-slate-800">{prog.program}</h3>
            <span className="bg-blue-50 text-blue-600 px-3 py-1 rounded-full text-xs font-bold tracking-wider border border-blue-100 whitespace-nowrap">
              {prog.degree}
            </span>
          </div>
          <p className="text-slate-500 font-medium text-sm flex items-center gap-1 mb-4">
            🏛️ {prog.university}
          </p>
          
          <div className="flex flex-wrap gap-2 text-xs font-semibold text-slate-600">
            <span className="bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">⏱ {prog.total_credit_hours} Credits</span>
            <span className="bg-emerald-50 text-emerald-700 px-3 py-1.5 rounded-lg border border-emerald-100">✨ Fits your schedule</span>
          </div>
        </div>
        
        <button 
          onClick={() => { setIsExpanded(!isExpanded); setActiveSemIndex(0); }}
          className="w-full md:w-auto px-6 py-2.5 bg-slate-900 text-white hover:bg-blue-600 rounded-xl text-sm font-bold transition-all shadow-sm"
        >
          {isExpanded ? "Close Details ⌃" : "View Curriculum ⌄"}
        </button>
      </div>

      {isExpanded && (
        <div className="p-6 border-t border-slate-100 bg-[#f8fafc] animate-fade-in">
          {prog.semesters && prog.semesters.length > 0 && (
            <div>
              {/* Semester Tabs */}
              <div className="flex flex-wrap gap-2 mb-5 bg-slate-200/50 p-1.5 rounded-xl w-fit">
                {prog.semesters.map((semData, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveSemIndex(idx)}
                    className={clsx(
                      "px-4 py-2 rounded-lg font-bold text-xs transition-all duration-300",
                      activeSemIndex === idx ? "bg-white text-blue-600 shadow-sm border border-slate-200" : "text-slate-500 hover:text-slate-800"
                    )}
                  >
                    {semData.semesterName}
                  </button>
                ))}
              </div>

              {/* Course Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {prog.semesters[activeSemIndex].courses?.map((course, cIdx) => (
                  <div key={cIdx} className="p-4 border border-slate-200/80 rounded-2xl bg-white hover:border-blue-300 transition-colors shadow-sm">
                    <div className="flex justify-between items-start mb-2 gap-2">
                      <div className="font-extrabold text-slate-800 break-words">{course.code}</div>
                      <div className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded-md whitespace-nowrap">{course.credits} Cr</div>
                    </div>
                    <div className="text-sm font-semibold text-slate-600 mb-3">{course.name}</div>
                    
                    <div className="flex flex-col gap-2 mt-auto">
                      <div className="flex items-center gap-2 text-xs font-medium text-slate-500 bg-slate-50 p-2 rounded-lg border border-slate-100">
                        <span className="text-blue-500">🕒</span> {course.schedule.day} | {course.schedule.time}
                      </div>
                      <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 px-1 mt-1">
                        <span className="truncate mr-2">👤 {course.instructor || "TBA"}</span>
                        <span className="whitespace-nowrap">📍 {course.campus}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// --- Modern Main Chatbot App (Full Screen) ---
const RecommendationPage = () => {
  const [messages, setMessages] = useState([]);
  const [step, setStep] = useState(1); 
  const [isTyping, setIsTyping] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const chatEndRef = useRef(null);

  const [keyword, setKeyword] = useState("");
  const [filteredPrograms, setFilteredPrograms] = useState([]);
  const allPrograms = getProgramList();

  const [userInputs, setUserInputs] = useState({
    selectedProgram: "",
    busyDays: { Mon: false, Tue: false, Wed: false, Thu: false, Fri: false },
    busyTimes: { morning: false, afternoon: false, evening: false }
  });

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping, step]);

  useEffect(() => {
    const profile = load("UserProfile") || {};
    const name = profile.firstName || "there";
    
    setMessages([
      { sender: "bot", type: "text", text: `Hi ${name}! 👋 I am EdPlan AI.` },
      { sender: "bot", type: "text", text: "Tell me, which subject or career path are you interested in? (e.g., Computer, Art, Math)" }
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

  const handleKeywordSubmit = (e) => {
    e.preventDefault();
    if (!keyword.trim()) return;

    addUserMessage(keyword);
    const searchTerms = keyword.toLowerCase().split(' ').filter(Boolean);
    setKeyword("");
    setIsTyping(true);

    setTimeout(() => {
      setIsTyping(false);
      
      const matches = allPrograms.filter(prog => {
        if (prog === "All Programs") return false;
        const progLower = prog.toLowerCase();
        return searchTerms.some(term => progLower.includes(term));
      });

      if (matches.length > 0) {
        setFilteredPrograms(matches);
        setStep(1.5);
        setMessages(prev => [...prev, { 
          sender: "bot", 
          type: "text", 
          text: `I found these related programs. Tap the one you want:` 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          sender: "bot", 
          type: "text", 
          text: "I couldn't find a match for that. Try something like 'Computer', 'Science', or 'Nursing'." 
        }]);
      }
    }, 800);
  };

  const handleProgramSelect = (prog) => {
    setUserInputs(prev => ({ ...prev, selectedProgram: prog }));
    addUserMessage(prog);
    setStep(2);
    addBotMessage("Got it! Now, select the days you usually WORK or are BUSY:");
  };

  const toggleDay = (day) => {
    setUserInputs(prev => ({
      ...prev, busyDays: { ...prev.busyDays, [day]: !prev.busyDays[day] }
    }));
  };

  const submitDays = () => {
    const selected = Object.keys(userInputs.busyDays).filter(d => userInputs.busyDays[d]);
    const replyText = selected.length > 0 ? selected.join(", ") : "I'm totally free!";
    addUserMessage(replyText);
    
    if (selected.length === 0) {
      setStep(4);
      analyzeResults({ ...userInputs, busyDays: {} });
    } else {
      setStep(3);
      addBotMessage("Cool. And what specific times are you busy on those days?");
    }
  };

  const toggleTime = (timeSlot) => {
    setUserInputs(prev => ({
      ...prev, busyTimes: { ...prev.busyTimes, [timeSlot]: !prev.busyTimes[timeSlot] }
    }));
  };

  const submitTimes = () => {
    const selected = Object.keys(userInputs.busyTimes).filter(t => userInputs.busyTimes[t]);
    const replyText = selected.length > 0 ? selected.join(", ") : "Any time!";
    addUserMessage(replyText);
    setStep(4);
    analyzeResults(userInputs);
  };

  const analyzeResults = (finalInputs) => {
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setMessages(prev => [...prev, { sender: "bot", type: "text", text: "Scanning campus schedules to find your perfect fit... ⚙️" }]);
      
      setTimeout(() => {
        try {
          const profile = load("UserProfile") || {};
          const searchParams = { ...profile, ...finalInputs };
          const results = getRecommendedPrograms(searchParams);
          
          if (results.length === 0) {
            setMessages(prev => [...prev, { sender: "bot", type: "text", text: "Hmm, your schedule is a bit too tight for the current offerings. You may need to clear up some days." }]);
          } else {
            setSearchResults(results);
            setMessages(prev => [...prev, { sender: "bot", type: "results", data: results }]);
          }
          setStep(5);
        } catch (error) {
          console.error(error);
        }
      }, 1500);
    }, 800);
  };

  const handleSavePlan = () => {
    if (searchResults.length === 0) return;
    const existingPlans = load("SavedPlans") || [];
    const newPlan = { id: Date.now(), date: new Date().toLocaleDateString(), program: userInputs.selectedProgram, results: searchResults };
    save("SavedPlans", [...existingPlans, newPlan]);
    setMessages(prev => [...prev, { sender: "bot", type: "text", text: "✅ Saved securely to your EdPlan profile!" }]);
    setStep(6);
  };

  const restartChat = () => {
    setMessages([{ sender: "bot", type: "text", text: "Let's find something else. What subject are you looking for?" }]);
    setUserInputs({ selectedProgram: "", busyDays: { Mon: false, Tue: false, Wed: false, Thu: false, Fri: false }, busyTimes: { morning: false, afternoon: false, evening: false } });
    setSearchResults([]);
    setStep(1);
    setKeyword("");
  };

  return (
    // Full Screen Edge-to-Edge Container
    <div className="flex flex-col h-screen w-full bg-[#f4f6f8]">
      
      {/* Top Header - Full Width */}
      <header className="w-full bg-white px-6 py-4 flex items-center justify-between border-b border-slate-200 shadow-sm z-20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white font-extrabold text-lg shadow-md">
            AI
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-800 tracking-tight">EdPlan Assistant</h2>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Online</span>
            </div>
          </div>
        </div>
        {step > 1 && (
          <button onClick={restartChat} className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 text-sm font-bold rounded-lg transition-colors flex items-center gap-2">
            <span>🔄</span> <span className="hidden sm:inline">Restart Chat</span>
          </button>
        )}
      </header>

      {/* Chat Area - Centered Content */}
      <div className="flex-1 overflow-y-auto w-full scroll-smooth flex justify-center">
        <div className="w-full max-w-4xl p-4 md:p-8 space-y-6">
          {messages.map((msg, index) => (
            <div key={index} className={clsx("flex", msg.sender === "user" ? "justify-end" : "justify-start")}>
              
              {/* Bot Avatar */}
              {msg.sender === "bot" && msg.type !== "results" && (
                 <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px] font-bold mr-3 mt-1 shadow-sm flex-shrink-0">AI</div>
              )}
              
              {/* Chat Bubbles */}
              <div className={clsx(
                "max-w-[85%] md:max-w-[75%]",
                msg.sender === "user" 
                  ? "bg-blue-600 text-white rounded-2xl rounded-tr-sm px-5 py-3.5 shadow-md font-medium" 
                  : msg.type === "results" 
                    ? "w-full max-w-full" 
                    : "bg-white text-slate-800 rounded-2xl rounded-tl-sm px-5 py-3.5 shadow-sm border border-slate-200 font-medium leading-relaxed"
              )}>
                {msg.type === "text" && <p>{msg.text}</p>}
                
                {msg.type === "results" && (
                  <div className="w-full mt-2 animate-fade-in-up">
                    {msg.data.map((prog, i) => <ResultCard key={i} prog={prog} />)}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start animate-fade-in">
               <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px] font-bold mr-3 mt-1 flex-shrink-0">AI</div>
               <div className="bg-white rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm border border-slate-200 flex gap-1.5 items-center">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
               </div>
            </div>
          )}
          
          <div ref={chatEndRef} className="h-4" />
        </div>
      </div>

      {/* Dynamic Input Control Panel - Centered Content */}
      <div className="w-full bg-white border-t border-slate-200 flex justify-center shadow-[0_-10px_40px_rgba(0,0,0,0.03)] z-20">
        <div className="w-full max-w-4xl p-4 md:p-6 min-h-[90px] max-h-[35vh] overflow-y-auto">
          
          {/* Step 1: Text Search */}
          {step === 1 && !isTyping && (
            <form onSubmit={handleKeywordSubmit} className="flex gap-3 bg-slate-50 p-2 rounded-2xl border border-slate-200 animate-fade-in-up">
              <input 
                type="text" 
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Type 'Computer', 'Nursing', 'Math'..." 
                className="flex-1 bg-transparent px-4 py-2 font-medium text-slate-800 placeholder-slate-400 outline-none w-full"
                autoFocus
              />
              <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-sm">
                Search
              </button>
            </form>
          )}

          {/* Step 1.5: Select Program Pills */}
          {step === 1.5 && !isTyping && (
             <div className="flex flex-wrap gap-2 animate-fade-in-up">
               {filteredPrograms.map(prog => (
                 <button 
                   key={prog} 
                   onClick={() => handleProgramSelect(prog)}
                   className="bg-white border border-slate-200 text-slate-700 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 px-5 py-2.5 rounded-full text-sm font-bold transition-all shadow-sm"
                 >
                   {prog}
                 </button>
               ))}
               <button onClick={() => setStep(1)} className="text-blue-600 underline text-sm ml-2 self-center font-bold hover:text-blue-800">
                 Try another search
               </button>
             </div>
          )}

          {/* Step 2: Day Picker */}
          {step === 2 && !isTyping && (
             <div className="animate-fade-in-up flex flex-col sm:flex-row gap-4 justify-between items-center">
               <div className="flex flex-wrap gap-3">
                 {Object.keys(userInputs.busyDays).map((day) => (
                   <button
                     key={day}
                     onClick={() => toggleDay(day)}
                     className={clsx(
                       "w-14 h-14 sm:w-16 sm:h-16 rounded-2xl font-bold flex items-center justify-center transition-all",
                       userInputs.busyDays[day] ? "bg-slate-900 text-white shadow-md transform -translate-y-1" : "bg-white text-slate-600 border border-slate-200 hover:border-slate-400"
                     )}
                   >
                     {day}
                   </button>
                 ))}
               </div>
               <button onClick={submitDays} className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-2xl font-bold text-sm shadow-md transition-all w-full sm:w-auto">
                 Confirm Days ➔
               </button>
             </div>
          )}

          {/* Step 3: Time Picker */}
          {step === 3 && !isTyping && (
             <div className="animate-fade-in-up flex flex-col gap-4">
               <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <button onClick={() => toggleTime('morning')} className={clsx("p-4 rounded-2xl font-bold flex flex-col items-center gap-1 transition-all border", userInputs.busyTimes.morning ? "bg-slate-900 text-white border-slate-900 shadow-md" : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50")}>
                    <span className="text-2xl">🌅</span> Morning <span className="text-xs font-medium opacity-70">8am - 12pm</span>
                  </button>
                  <button onClick={() => toggleTime('afternoon')} className={clsx("p-4 rounded-2xl font-bold flex flex-col items-center gap-1 transition-all border", userInputs.busyTimes.afternoon ? "bg-slate-900 text-white border-slate-900 shadow-md" : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50")}>
                    <span className="text-2xl">☀️</span> Afternoon <span className="text-xs font-medium opacity-70">12pm - 4pm</span>
                  </button>
                  <button onClick={() => toggleTime('evening')} className={clsx("p-4 rounded-2xl font-bold flex flex-col items-center gap-1 transition-all border", userInputs.busyTimes.evening ? "bg-slate-900 text-white border-slate-900 shadow-md" : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50")}>
                    <span className="text-2xl">🌙</span> Evening <span className="text-xs font-medium opacity-70">4pm Onwards</span>
                  </button>
               </div>
               <button onClick={submitTimes} className="bg-emerald-500 hover:bg-emerald-600 text-white px-8 py-4 rounded-2xl font-bold text-sm shadow-md transition-all self-end w-full sm:w-auto">
                 Find My Perfect Schedule ✨
               </button>
             </div>
          )}

          {/* Step 5: Save Button */}
          {step === 5 && !isTyping && (
             <div className="flex justify-center animate-fade-in-up py-2">
               <button onClick={handleSavePlan} className="bg-slate-900 hover:bg-black text-white px-10 py-4 rounded-2xl font-bold shadow-lg flex items-center gap-2 transition-transform transform hover:-translate-y-1">
                 <span>💾</span> Save Plan to Profile
               </button>
             </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecommendationPage;