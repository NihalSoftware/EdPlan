import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { FaBookOpen, FaCheckCircle, FaChevronRight, FaGraduationCap, FaRedo, FaSyncAlt } from "react-icons/fa";

const academicProfile = {
  university: "Northern New Mexico College",
  degree: "Bachelor of Science",
  major: "Computer Science",
  academicYear: "2026 - 2027",
  studentId: "NMMC-26CS-0521",
  creditsCompleted: 30,
};

const semesters = [
  { value: "Fall 2026", registrationWindow: "May 1 - Aug 15, 2026" },
  { value: "Spring 2027", registrationWindow: "Oct 20 - Jan 12, 2027" },
];

const savedPlans = [
  { id: "balanced", semester: "Fall 2026", name: "Fall 2026 Balanced Plan", credits: 15, courseCount: 5, createdDate: "May 12, 2026", status: "Finalized", color: "#1668DC", courses: ["COMP 350", "MATH 270", "ENGL 112", "CSCI 245", "PHYS 210"] },
  { id: "accelerated", semester: "Fall 2026", name: "Fall 2026 Accelerated Plan", credits: 18, courseCount: 6, createdDate: "May 5, 2026", status: "Draft", color: "#7C3AED", courses: ["COMP 350", "MATH 270", "ENGL 112", "CSCI 245", "PHYS 210", "DATA 340"] },
  { id: "core", semester: "Fall 2026", name: "Fall 2026 Core Focus Plan", credits: 12, courseCount: 4, createdDate: "Apr 28, 2026", status: "Finalized", color: "#059669", courses: ["COMP 350", "MATH 270", "CSCI 245", "ENGL 112"] },
  { id: "light", semester: "Fall 2026", name: "Fall 2026 Light Load Plan", credits: 9, courseCount: 3, createdDate: "Apr 20, 2026", status: "Draft", color: "#DB2777", courses: ["MATH 270", "ENGL 112", "PHYS 210"] },
  { id: "spring-balanced", semester: "Spring 2027", name: "Spring 2027 Balanced Plan", credits: 15, courseCount: 5, createdDate: "Nov 2, 2026", status: "Draft", color: "#1668DC", courses: ["COMP 350", "MATH 270", "ENGL 112", "CSCI 245", "DATA 340"] },
];

const scheduleSections = {
  "COMP 350": { name: "COMP 350", credits: 3, color: "bg-blue-100 border-blue-300 text-blue-900", meetings: [{ day: "Monday", start: "10:00 AM", end: "11:15 AM", slot: "10:00 AM" }, { day: "Wednesday", start: "10:00 AM", end: "11:15 AM", slot: "10:00 AM" }] },
  "MATH 270": { name: "MATH 270", credits: 3, color: "bg-emerald-100 border-emerald-300 text-emerald-900", meetings: [{ day: "Tuesday", start: "9:00 AM", end: "10:15 AM", slot: "9:00 AM" }, { day: "Thursday", start: "9:00 AM", end: "10:15 AM", slot: "9:00 AM" }] },
  "ENGL 112": { name: "ENGL 112", credits: 3, color: "bg-violet-100 border-violet-300 text-violet-900", meetings: [{ day: "Monday", start: "1:00 PM", end: "2:15 PM", slot: "1:00 PM" }, { day: "Wednesday", start: "1:00 PM", end: "2:15 PM", slot: "1:00 PM" }] },
  "CSCI 245": { name: "CSCI 245", credits: 3, color: "bg-pink-100 border-pink-300 text-pink-900", meetings: [{ day: "Tuesday", start: "2:30 PM", end: "3:45 PM", slot: "2:00 PM" }, { day: "Thursday", start: "2:30 PM", end: "3:45 PM", slot: "2:00 PM" }] },
  "PHYS 210": { name: "PHYS 210", credits: 3, color: "bg-amber-100 border-amber-300 text-amber-900", meetings: [{ day: "Monday", start: "3:00 PM", end: "4:15 PM", slot: "3:00 PM" }, { day: "Wednesday", start: "3:00 PM", end: "4:15 PM", slot: "3:00 PM" }] },
  "DATA 340": { name: "DATA 340", credits: 3, color: "bg-cyan-100 border-cyan-300 text-cyan-900", meetings: [{ day: "Friday", start: "10:00 AM", end: "12:30 PM", slot: "10:00 AM" }] },
};

const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const timeSlots = ["8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"];
const scheduleGenerationDelayMs = 11000;

const generateSchedule = (plan) => {
  const weeklySchedule = Object.fromEntries(days.map((day) => [day, []]));
  const courses = plan.courses.map((code) => scheduleSections[code]).filter(Boolean);

  courses.forEach((course) => {
    course.meetings.forEach((meeting) => {
      weeklySchedule[meeting.day].push({ ...meeting, course: course.name, color: course.color });
    });
  });

  const freeDays = days.filter((day) => weeklySchedule[day].length === 0);
  const workload = plan.credits >= 17 ? "High" : plan.credits <= 10 ? "Light" : "Balanced";

  return {
    semester: plan.semester,
    totalCredits: plan.credits,
    courseCount: plan.courseCount,
    workload,
    studyHours: plan.credits >= 17 ? "20 - 24 hrs" : plan.credits <= 10 ? "9 - 12 hrs" : "15 - 18 hrs",
    prerequisiteStatus: "All prerequisites satisfied",
    conflicts: "No conflicts found",
    freeDays: freeDays.length ? freeDays.join(", ") : "No free weekdays",
    weeklySchedule,
  };
};

const SchedulePilotPage = () => {
  const [currentStep, setCurrentStep] = useState("profile");
  const [selectedSemester, setSelectedSemester] = useState("Fall 2026");
  const [selectedPlanId, setSelectedPlanId] = useState("");

  const selectedSemesterMeta = semesters.find((semester) => semester.value === selectedSemester) || semesters[0];
  const plansForSemester = savedPlans.filter((plan) => plan.semester === selectedSemester);
  const selectedPlan = plansForSemester.find((plan) => plan.id === selectedPlanId);
  const schedule = useMemo(() => (selectedPlan ? generateSchedule(selectedPlan) : null), [selectedPlan]);

  const handleSemesterChange = (value) => {
    setSelectedSemester(value);
    setSelectedPlanId("");
    setCurrentStep("semester");
  };

  const loadPlans = () => {
    setCurrentStep("loadingPlans");
    window.setTimeout(() => setCurrentStep("plans"), 650);
  };

  const selectPlan = (planId) => {
    setSelectedPlanId(planId);
    setCurrentStep("generating");
    window.setTimeout(() => setCurrentStep("schedule"), scheduleGenerationDelayMs);
  };

  const regenerateSchedule = () => {
    if (!selectedPlan) return;
    setCurrentStep("generating");
    window.setTimeout(() => setCurrentStep("schedule"), scheduleGenerationDelayMs);
  };

  return (
    <section className="min-h-screen bg-[#F4F7FC] p-6">
      <div className="mx-auto max-w-7xl space-y-5">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-900">SchedulePilot</h1>
            <p className="mt-2 text-sm text-slate-600">Plan, select, and generate your perfect semester schedule.</p>
          </div>
          <Link to="/nexus" className="inline-flex h-11 items-center justify-center rounded-[8px] border border-[#DCE3F0] bg-white px-5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
            Back to Nexus
          </Link>
        </div>

        <AcademicProfileCard currentStep={currentStep} onContinue={() => setCurrentStep("semester")} />

        {currentStep !== "profile" && (
          <div className="space-y-5">
            <SemesterSelector
              currentStep={currentStep}
              selectedSemester={selectedSemester}
              selectedSemesterMeta={selectedSemesterMeta}
              onSemesterChange={handleSemesterChange}
              onLoadPlans={loadPlans}
            />

            {currentStep === "semester" && <AgentWaitingCard title="Select a semester" detail="Load saved education plans for the selected semester to begin scheduling." />}

            {["loadingPlans", "plans", "generating", "schedule"].includes(currentStep) && (
              <SavedPlansPanel plans={plansForSemester} selectedPlan={selectedPlan} currentStep={currentStep} onSelectPlan={selectPlan} />
            )}

            {currentStep === "plans" && <AgentWaitingCard title="Choose an education plan" detail="Selecting a plan will trigger the scheduling agent automatically." />}
            {currentStep === "generating" && <AgentWaitingCard title="Scheduling agent is working" detail="Reading courses, matching sections, checking prerequisites, avoiding conflicts, and calculating workload. This takes about 10-12 seconds." active />}
            {currentStep === "schedule" && schedule && (
              <>
                <GeneratedScheduleCard selectedPlan={selectedPlan} schedule={schedule} onRegenerate={regenerateSchedule} />
                <ScheduleInsights schedule={schedule} />
              </>
            )}
          </div>
        )}
      </div>
    </section>
  );
};

const AcademicProfileCard = ({ currentStep, onContinue }) => (
  <div className="overflow-hidden rounded-[16px] border border-[#DCE3F0] bg-white p-5 shadow-sm">
    <div className="grid gap-6 xl:grid-cols-[72px_1fr_380px] xl:items-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full border border-[#BFD4F7] bg-[#E8F1FF] text-[#1668DC]">
        <FaGraduationCap className="h-8 w-8" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-slate-900">My Academic Information</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <ProfileField label="University" value={academicProfile.university} />
          <ProfileField label="Program / Degree" value={academicProfile.degree} />
          <ProfileField label="Major" value={academicProfile.major} />
          <ProfileField label="Academic Year" value={academicProfile.academicYear} />
          <ProfileField label="Student ID" value={academicProfile.studentId} />
          <ProfileField label="Credits Completed" value={academicProfile.creditsCompleted} />
        </div>
      </div>
      <div className="hidden min-h-[140px] rounded-[14px] bg-gradient-to-br from-[#E8F1FF] via-white to-[#E6F7EE] p-5 xl:block">
        <div className="ml-auto h-24 w-44 rounded-t-[80px] border border-[#BFD4F7] bg-white/70" />
        <div className="mt-2 h-5 rounded-full bg-emerald-200/80" />
      </div>
    </div>
    {currentStep === "profile" && (
      <div className="mt-5 flex flex-col gap-3 rounded-[12px] border border-[#E6EAF3] bg-slate-50 px-4 py-3 md:flex-row md:items-center md:justify-between">
        <p className="text-sm text-slate-600">SchedulePilot verified your profile. Continue when you are ready to choose a semester.</p>
        <button type="button" onClick={onContinue} className="inline-flex h-11 items-center justify-center rounded-[8px] bg-[#1668DC] px-5 text-sm font-semibold text-white transition hover:bg-[#1659c9]">
          Continue to Semester
        </button>
      </div>
    )}
  </div>
);

const SemesterSelector = ({ currentStep, selectedSemester, selectedSemesterMeta, onSemesterChange, onLoadPlans }) => (
  <div className="rounded-[16px] border border-[#DCE3F0] bg-white p-4 shadow-sm">
    <div className="grid gap-3 md:grid-cols-[120px_1fr_180px_auto] md:items-center">
      <label className="text-sm font-semibold text-slate-900" htmlFor="semester">Select Semester</label>
      <select id="semester" value={selectedSemester} onChange={(event) => onSemesterChange(event.target.value)} className="h-12 rounded-[8px] border border-[#DCE3F0] bg-slate-50 px-4 text-sm font-semibold text-slate-800 outline-none focus:border-[#1668DC]">
        {semesters.map((semester) => (
          <option key={semester.value} value={semester.value}>{semester.value}</option>
        ))}
      </select>
      <div className="rounded-[8px] border border-[#DCE3F0] bg-[#F8FBFF] px-3 py-2 text-xs text-slate-600">
        <span className="font-semibold text-slate-900">Registration Window</span>
        <br />
        {selectedSemesterMeta.registrationWindow}
      </div>
      <button type="button" onClick={onLoadPlans} className="inline-flex h-12 items-center justify-center rounded-[8px] bg-[#1668DC] px-4 text-sm font-semibold text-white transition hover:bg-[#1659c9]">
        {currentStep === "loadingPlans" ? "Loading..." : "Load Plans"}
      </button>
    </div>
  </div>
);

const SavedPlansPanel = ({ plans, selectedPlan, currentStep, onSelectPlan }) => (
  <div className="rounded-[16px] border border-[#DCE3F0] bg-white p-5 shadow-sm">
    <div className="flex items-center justify-between gap-3">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Saved Education Plans</h2>
        <p className="mt-1 text-sm text-slate-500">{currentStep === "loadingPlans" ? "SchedulePilot is fetching plans for the selected semester." : "Choose a plan to generate your schedule."}</p>
      </div>
      <FaSyncAlt className="h-4 w-4 text-[#1668DC]" />
    </div>
    <div className="mt-5 space-y-4">
      {currentStep === "loadingPlans"
        ? [1, 2, 3].map((item) => <div key={item} className="h-[82px] animate-pulse rounded-[12px] border border-[#E6EAF3] bg-slate-50" />)
        : plans.map((plan) => <PlanButton key={plan.id} plan={plan} selected={plan.id === selectedPlan?.id} onClick={() => onSelectPlan(plan.id)} />)}
    </div>
    <div className="mt-6 flex items-center justify-between rounded-[10px] border border-[#E6EAF3] bg-slate-50 px-4 py-3 text-sm text-slate-600">
      <span>Can't find a plan? Create a new education plan for this semester.</span>
      <Link to="/educationplan" className="rounded-[8px] border border-[#1668DC] bg-white px-4 py-2 text-sm font-semibold text-[#1668DC]">Create New Plan</Link>
    </div>
  </div>
);

const PlanButton = ({ plan, selected, onClick }) => (
  <button type="button" onClick={onClick} className={`w-full rounded-[12px] border p-4 text-left transition ${selected ? "border-[#1668DC] bg-[#F8FBFF] shadow-sm" : "border-[#E6EAF3] bg-white hover:border-[#BFD4F7]"}`}>
    <div className="flex items-center gap-4">
      <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-[10px]" style={{ backgroundColor: `${plan.color}1A`, color: plan.color }}>
        <FaBookOpen className="h-5 w-5" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="font-semibold text-slate-900">{plan.name}</h3>
          <span className={`rounded-full px-2 py-1 text-xs font-semibold ${plan.status === "Finalized" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>{plan.status}</span>
        </div>
        <p className="mt-2 text-sm text-slate-600">
          {plan.credits} Credits <span className="mx-2 text-slate-300">-</span> {plan.courseCount} Courses <span className="mx-2 text-slate-300">-</span> Created: {plan.createdDate}
        </p>
      </div>
      {selected ? <FaCheckCircle className="h-5 w-5 text-[#1668DC]" /> : <FaChevronRight className="h-4 w-4 text-slate-400" />}
    </div>
  </button>
);

const AgentWaitingCard = ({ title, detail, active = false }) => (
  <div className="rounded-[16px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
    <div className={`rounded-[12px] border px-4 py-3 ${active ? "border-blue-200 bg-blue-50" : "border-[#E6EAF3] bg-slate-50"}`}>
      <p className="text-lg font-semibold text-slate-900">{title}</p>
      <p className="mt-2 text-sm leading-6 text-slate-600">{detail}</p>
      {active && <div className="mt-4 h-2 overflow-hidden rounded-full bg-blue-100"><div className="h-full w-2/3 animate-pulse rounded-full bg-[#1668DC]" /></div>}
    </div>
  </div>
);

const GeneratedScheduleCard = ({ selectedPlan, schedule, onRegenerate }) => (
  <div className="rounded-[16px] border border-[#DCE3F0] bg-white p-5 shadow-sm">
    <div className="flex flex-col gap-3 rounded-[10px] border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm md:flex-row md:items-center md:justify-between">
      <div className="flex items-center gap-2 font-semibold text-emerald-700"><FaCheckCircle className="h-4 w-4" />Schedule generated successfully!</div>
      <button type="button" onClick={onRegenerate} className="inline-flex h-9 items-center justify-center gap-2 rounded-[8px] border border-[#1668DC] bg-white px-4 text-sm font-semibold text-[#1668DC]">Regenerate<FaRedo className="h-3 w-3" /></button>
    </div>
    <h2 className="mt-5 text-xl font-semibold text-slate-900">{selectedPlan?.semester} {schedule.workload} Plan Schedule</h2>
    <div className="mt-4 grid gap-3 md:grid-cols-4">
      <MetricCard label="Total Credits" value={schedule.totalCredits} />
      <MetricCard label="Course Count" value={schedule.courseCount} />
      <MetricCard label="Workload" value={schedule.workload} />
      <MetricCard label="Est. Weekly Study Hours" value={schedule.studyHours} />
    </div>
    <div className="mt-6">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">Weekly Timetable</h3>
        <div className="rounded-[8px] border border-[#DCE3F0] bg-slate-50 p-1 text-xs font-semibold text-slate-600">
          <span className="inline-block rounded-[6px] px-3 py-1">List View</span>
          <span className="inline-block rounded-[6px] bg-white px-3 py-1 text-[#1668DC] shadow-sm">Calendar View</span>
        </div>
      </div>
      <Timetable schedule={schedule} />
    </div>
  </div>
);

const Timetable = ({ schedule }) => (
  <div className="overflow-x-auto rounded-[12px] border border-[#DCE3F0]">
    <table className="min-w-[760px] w-full table-fixed border-collapse bg-white text-sm">
      <thead>
        <tr className="bg-slate-50 text-slate-600">
          <th className="w-24 border-b border-r border-[#E6EAF3] px-3 py-3 text-left font-semibold">Time</th>
          {days.map((day) => <th key={day} className="border-b border-r border-[#E6EAF3] px-3 py-3 text-center font-semibold last:border-r-0">{day}</th>)}
        </tr>
      </thead>
      <tbody>
        {timeSlots.map((slot) => (
          <tr key={slot} className="h-16">
            <td className="border-r border-t border-[#E6EAF3] px-3 py-2 font-medium text-slate-700">{slot}</td>
            {days.map((day) => {
              const meeting = schedule.weeklySchedule[day].find((item) => item.slot === slot);
              return (
                <td key={`${day}-${slot}`} className="border-r border-t border-[#E6EAF3] p-1 align-top last:border-r-0">
                  {meeting && <div className={`rounded-[6px] border px-2 py-2 text-xs font-semibold leading-5 ${meeting.color}`}>{meeting.course}<br /><span className="font-medium">{meeting.start} - {meeting.end}</span></div>}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const ScheduleInsights = ({ schedule }) => (
  <div className="rounded-[16px] border border-[#DCE3F0] bg-white p-5 shadow-sm">
    <h2 className="text-lg font-semibold text-slate-900">Schedule Insights</h2>
    <div className="mt-4 grid gap-3 md:grid-cols-5">
      <InsightCard label="Workload Indicator" value={schedule.workload} />
      <InsightCard label="Prerequisite Status" value={schedule.prerequisiteStatus} positive />
      <InsightCard label="Credit Distribution" value={`${schedule.totalCredits} / 18 planned`} />
      <InsightCard label="Free Days" value={schedule.freeDays} />
      <InsightCard label="Conflicts" value={schedule.conflicts} positive />
    </div>
  </div>
);

const ProfileField = ({ label, value }) => (
  <div className="border-l border-[#DCE3F0] pl-5 first:border-l-0 first:pl-0">
    <p className="text-sm text-slate-500">{label}</p>
    <p className="mt-1 font-semibold text-slate-900">{value}</p>
  </div>
);

const MetricCard = ({ label, value }) => (
  <div className="rounded-[10px] border border-[#E6EAF3] bg-slate-50 p-4">
    <p className="text-xs font-medium text-slate-500">{label}</p>
    <p className="mt-2 text-lg font-semibold text-slate-900">{value}</p>
  </div>
);

const InsightCard = ({ label, value, positive = false }) => (
  <div className="rounded-[10px] border border-[#E6EAF3] bg-slate-50 p-3">
    <p className="text-xs font-semibold text-slate-600">{label}</p>
    <div className="mt-3 flex items-center gap-2 text-xs font-semibold text-slate-700">
      {positive && <FaCheckCircle className="h-3 w-3 text-emerald-600" />}
      <span>{value}</span>
    </div>
  </div>
);

export default SchedulePilotPage;
