import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import {
  FaArrowLeft,
  FaBolt,
  FaBookOpen,
  FaBookmark,
  FaCalendarAlt,
  FaCalendarCheck,
  FaChartLine,
  FaCheckCircle,
  FaGraduationCap,
  FaMagic,
  FaRobot,
  FaRocket,
  FaSave,
  FaShieldAlt,
} from "react-icons/fa";
import { load as loadStorage, save as saveStorage } from "../utils/storage.js";

const promptSuggestions = [
  "Plan my academic roadmap for graduation",
  "Create a balanced semester-by-semester education plan",
  "Help me finish my degree with a manageable workload",
  "Build a course plan around prerequisites and credit limits",
];

const processingSteps = ["Thinking....", "Analysing....", "Generating...."];
const generationDelayMs = 11000;

const getMaxCredits = (hoursPerDay) => {
  const hours = Number(hoursPerDay);
  if (hours >= 6) return 18;
  if (hours >= 4) return 15;
  if (hours >= 2) return 12;
  return 9;
};

const findBestPlan = (plans, formValues) => {
  const completedCredits = Number(formValues.completedCredits) || 0;
  const hoursPerDay = Number(formValues.hoursPerDay) || 0;

  return [...plans].sort((a, b) => {
    const aCreditGap = Math.abs((a.criteria?.completedCredits ?? 0) - completedCredits);
    const bCreditGap = Math.abs((b.criteria?.completedCredits ?? 0) - completedCredits);
    const aHourGap = Math.abs((a.criteria?.studyHoursPerDay ?? 0) - hoursPerDay);
    const bHourGap = Math.abs((b.criteria?.studyHoursPerDay ?? 0) - hoursPerDay);

    return aCreditGap + aHourGap - (bCreditGap + bHourGap);
  })[0];
};

const PathfinderPage = () => {
  const [catalog, setCatalog] = useState(null);
  const [mockPlanCatalog, setMockPlanCatalog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [step, setStep] = useState("prompt");
  const [prompt, setPrompt] = useState("");
  const [processing, setProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);
  const [plan, setPlan] = useState(null);
  const [saveStatus, setSaveStatus] = useState("");
  const generationTimerRef = useRef(null);
  const [form, setForm] = useState({
    university: "",
    program: "",
    completedCredits: 0,
    hoursPerDay: 4,
    startTerm: "Fall 2026",
    goal: "Graduate on time with a balanced workload",
  });

  useEffect(() => {
    Promise.all([fetch("/assets/programdetail.json"), fetch("/assets/mock_education_plans.json")])
      .then(([programResponse, planResponse]) => Promise.all([programResponse.json(), planResponse.json()]))
      .then(([programJson, planJson]) => {
        setCatalog(programJson);
        setMockPlanCatalog(planJson);
        const firstUniversity = programJson.universities?.[0];
        const firstProgram = firstUniversity?.programs?.[0];
        setForm((current) => ({
          ...current,
          university: firstUniversity?.university || "",
          program: firstProgram?.program || "",
        }));
      })
      .catch(() => {
        setCatalog(null);
        setMockPlanCatalog(null);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!processing) {
      setProcessingStep(0);
      return undefined;
    }

    const statusTimer = window.setInterval(() => {
      setProcessingStep((current) => (current + 1) % processingSteps.length);
    }, 1800);

    return () => window.clearInterval(statusTimer);
  }, [processing]);

  useEffect(() => {
    return () => {
      if (generationTimerRef.current) {
        window.clearTimeout(generationTimerRef.current);
      }
    };
  }, []);

  const universities = catalog?.universities || [];
  const selectedUniversity = useMemo(
    () => universities.find((item) => item.university === form.university) || universities[0],
    [form.university, universities]
  );
  const programs = selectedUniversity?.programs || [];
  const selectedProgram = useMemo(
    () => programs.find((item) => item.program === form.program) || programs[0],
    [form.program, programs]
  );

  const updateForm = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleUniversityChange = (value) => {
    const nextUniversity = universities.find((item) => item.university === value);
    setForm((current) => ({
      ...current,
      university: value,
      program: nextUniversity?.programs?.[0]?.program || "",
    }));
  };

  const runPrompt = () => {
    if (!prompt.trim()) return;
    setStep("details");
  };

  const generatePlan = (event) => {
    event.preventDefault();
    if (!selectedProgram || processing) return;

    setProcessing(true);
    setProcessingStep(0);
    setPlan(null);
    setSaveStatus("");

    if (generationTimerRef.current) {
      window.clearTimeout(generationTimerRef.current);
    }

    generationTimerRef.current = window.setTimeout(() => {
      const bestPlan = findBestPlan(mockPlanCatalog?.plans || [], form);

      setPlan({
        selected: bestPlan || null,
        options: bestPlan ? [bestPlan] : [],
      });
      setProcessing(false);
      setStep("plan");
      generationTimerRef.current = null;
    }, generationDelayMs);
  };

  const saveSelectedPlan = () => {
    if (!plan?.selected) return;

    const flatCourses = plan.selected.semesters.flatMap((semester, semesterIndex) =>
      semester.courses.map((course) => ({
        ...course,
        courseName: course.name,
        name: course.name,
        year: `Year ${Math.floor(semesterIndex / 2) + 1}`,
        semester: semester.title,
      }))
    );

    const savedPlan = {
      ...plan.selected,
      savedAt: new Date().toISOString(),
      savedDate: new Date().toISOString(),
      studentInput: form,
      university: selectedUniversity?.college_profile?.university_name || form.university,
      program: selectedProgram?.program || form.program,
      degree: selectedProgram?.degree || "",
      courses: flatCourses,
      source: "pathfinder",
    };

    const existingPlans = loadStorage("LocalSavedPlans", []);
    saveStorage("LocalSavedPlans", [savedPlan, ...existingPlans]);
    saveStorage("pathfinderSavedPlan", savedPlan);
    setSaveStatus("Saved");
    toast.success("Saved successfully.");
  };

  if (loading) {
    return (
      <section className="min-h-screen bg-[#F4F7FC] p-6">
        <div className="mx-auto flex max-w-6xl items-center justify-center py-32 text-slate-500">Loading PathFinder...</div>
      </section>
    );
  }

  if (!catalog || !selectedProgram || !mockPlanCatalog) {
    return (
      <section className="min-h-screen bg-[#F4F7FC] p-6">
        <div className="mx-auto max-w-6xl rounded-[24px] border border-[#DCE3F0] bg-white p-10 shadow-sm">Unable to load PathFinder plan data.</div>
      </section>
    );
  }

  return (
    <section className="min-h-screen bg-[#F4F7FC] p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="relative overflow-hidden rounded-[24px] border border-[#DCE3F0] bg-gradient-to-br from-[#EEF4FF] via-white to-[#EFEAFF] p-8 shadow-sm">
          <div className="pointer-events-none absolute right-8 top-7 hidden h-32 w-56 rounded-[50%] border border-[#A99CFF] opacity-70 lg:block" />
          <div className="pointer-events-none absolute right-14 top-14 hidden h-24 w-48 rotate-[-18deg] rounded-[50%] border border-[#BFD4F7] opacity-70 lg:block" />
          <div className="pointer-events-none absolute right-28 top-20 hidden text-4xl text-[#7C3AED] lg:block">+</div>
          <div className="relative flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div className="flex max-w-3xl gap-5">
              <div className="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-full bg-[#E2E7FF] text-[#4F46E5]">
                <FaMagic className="h-7 w-7" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.38em] text-[#4F46E5]">PathFinder AI</p>
                <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-900">Academic plan generator</h1>
                <p className="mt-4 text-base leading-7 text-slate-600">
                  Tell PathFinder what you need, confirm your academic details, and generate a semester roadmap with 8-18 credits per term.
                </p>
              </div>
            </div>
            {step === "plan" ? (
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={() => setStep("details")}
                  className="inline-flex h-11 items-center justify-center gap-2 rounded-full border border-[#DCE3F0] bg-slate-50 px-5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
                >
                  <FaArrowLeft className="h-4 w-4" />
                  Back to Details
                </button>
                <button
                  type="button"
                  onClick={saveSelectedPlan}
                  className="inline-flex h-11 items-center justify-center gap-2 rounded-full bg-[#1668DC] px-5 text-sm font-semibold text-white transition hover:bg-[#1659c9]"
                >
                  <FaSave className="h-4 w-4" />
                  {saveStatus || "Save Plan"}
                </button>
              </div>
            ) : (
              <Link
                to="/nexus"
                className="inline-flex h-11 items-center justify-center gap-2 rounded-full border border-[#DCE3F0] bg-slate-50 px-5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              >
                <FaArrowLeft className="h-4 w-4" />
                Back to Nexus
              </Link>
            )}
          </div>
        </div>

        {step === "prompt" && (
          <div className="grid gap-6 lg:grid-cols-[1fr_344px]">
            <div className="space-y-6">
              <AcademicProfilePanel
                university={selectedUniversity?.college_profile?.university_name || form.university}
                program={selectedProgram?.program || form.program}
                creditsCompleted={form.completedCredits}
              />

              <div className="rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
                <label className="flex items-center gap-3 text-lg font-semibold text-slate-900" htmlFor="pathfinder-prompt">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#EEF4FF] text-[#4F46E5]">
                    <FaMagic className="h-4 w-4" />
                  </span>
                  What should PathFinder help you plan?
                </label>
                <div className="mt-5 rounded-[18px] border border-[#C8D4EA] bg-slate-50 p-4 transition focus-within:border-[#1668DC] focus-within:bg-white">
                  <textarea
                    id="pathfinder-prompt"
                    value={prompt}
                    onChange={(event) => setPrompt(event.target.value)}
                    className="min-h-[150px] w-full resize-none bg-transparent text-base leading-7 text-slate-800 outline-none"
                    placeholder="Example: Create a four-year Computer Science plan that keeps my workload balanced and respects prerequisites."
                    maxLength={1500}
                  />
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <div className="flex items-center gap-3">
                      <FaMagic className="h-4 w-4" />
                      <FaBookmark className="h-4 w-4" />
                    </div>
                    <span>{prompt.length} / 1500</span>
                  </div>
                </div>
                <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center">
                  <button
                    type="button"
                    onClick={runPrompt}
                    disabled={!prompt.trim()}
                    className="inline-flex h-12 items-center justify-center gap-2 rounded-[8px] bg-gradient-to-r from-[#4F46E5] to-[#1668DC] px-7 text-sm font-semibold text-white shadow-sm transition hover:brightness-105 disabled:cursor-not-allowed disabled:bg-none disabled:bg-slate-300 disabled:shadow-none"
                  >
                    <FaBolt className="h-4 w-4" />
                    Run Prompt
                  </button>
                  <p className="text-sm text-slate-500">PathFinder AI will analyze your request and generate a tailored plan.</p>
                </div>
              </div>

              <div className="rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <FaBolt className="h-4 w-4 text-[#4F46E5]" />
                  <h2 className="text-lg font-semibold text-slate-900">Prompt Suggestions</h2>
                </div>
                <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  {promptSuggestions.map((suggestion, index) => (
                    <PromptSuggestionCard key={suggestion} suggestion={suggestion} index={index} onSelect={setPrompt} />
                  ))}
                </div>
              </div>
            </div>

            <PathfinderAssistantPanel completedCredits={Number(form.completedCredits) || 0} selectedProgram={selectedProgram} />
          </div>
        )}

        {step === "details" && (
          <form onSubmit={generatePlan} className="rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-sm font-semibold text-[#1668DC]">Prompt accepted</p>
                <h2 className="mt-2 text-2xl font-semibold text-slate-900">Add the essential student details</h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{prompt}</p>
              </div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <label className="space-y-2 text-sm font-semibold text-slate-700">
                University
                <select
                  value={form.university}
                  onChange={(event) => handleUniversityChange(event.target.value)}
                  className="h-12 w-full rounded-[14px] border border-[#DCE3F0] bg-slate-50 px-4 text-sm font-medium text-slate-800 outline-none focus:border-[#1668DC]"
                >
                  {universities.map((university) => (
                    <option key={university.university} value={university.university}>
                      {university.college_profile?.university_name || university.university}
                    </option>
                  ))}
                </select>
              </label>

              <label className="space-y-2 text-sm font-semibold text-slate-700">
                Program
                <select
                  value={form.program}
                  onChange={(event) => updateForm("program", event.target.value)}
                  className="h-12 w-full rounded-[14px] border border-[#DCE3F0] bg-slate-50 px-4 text-sm font-medium text-slate-800 outline-none focus:border-[#1668DC]"
                >
                  {programs.map((program) => (
                    <option key={program.program} value={program.program}>
                      {program.degree} in {program.program}
                    </option>
                  ))}
                </select>
              </label>

              <label className="space-y-2 text-sm font-semibold text-slate-700">
                Credits already completed
                <input
                  type="number"
                  min="0"
                  max="60"
                  value={form.completedCredits}
                  onChange={(event) => updateForm("completedCredits", event.target.value)}
                  className="h-12 w-full rounded-[14px] border border-[#DCE3F0] bg-slate-50 px-4 text-sm font-medium text-slate-800 outline-none focus:border-[#1668DC]"
                />
              </label>

              <label className="space-y-2 text-sm font-semibold text-slate-700">
                Hours you can study per day
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={form.hoursPerDay}
                  onChange={(event) => updateForm("hoursPerDay", event.target.value)}
                  className="h-12 w-full rounded-[14px] border border-[#DCE3F0] bg-slate-50 px-4 text-sm font-medium text-slate-800 outline-none focus:border-[#1668DC]"
                />
              </label>

              <label className="space-y-2 text-sm font-semibold text-slate-700">
                Starting semester
                <select
                  value={form.startTerm}
                  onChange={(event) => updateForm("startTerm", event.target.value)}
                  className="h-12 w-full rounded-[14px] border border-[#DCE3F0] bg-slate-50 px-4 text-sm font-medium text-slate-800 outline-none focus:border-[#1668DC]"
                >
                  <option>Fall 2026</option>
                  <option>Spring 2027</option>
                  <option>Fall 2027</option>
                </select>
              </label>

              <label className="space-y-2 text-sm font-semibold text-slate-700">
                Planning goal
                <input
                  type="text"
                  value={form.goal}
                  onChange={(event) => updateForm("goal", event.target.value)}
                  className="h-12 w-full rounded-[14px] border border-[#DCE3F0] bg-slate-50 px-4 text-sm font-medium text-slate-800 outline-none focus:border-[#1668DC]"
                />
              </label>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-[18px] border border-[#E6EAF3] bg-slate-50 p-4">
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Credit Rule</p>
                <p className="mt-3 text-lg font-semibold text-slate-900">8-18 per semester</p>
              </div>
              <div className="rounded-[18px] border border-[#E6EAF3] bg-slate-50 p-4">
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Program Credits</p>
                <p className="mt-3 text-lg font-semibold text-slate-900">{selectedProgram.total_credit_hours}</p>
              </div>
              <div className="rounded-[18px] border border-[#E6EAF3] bg-slate-50 p-4">
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Planned Load</p>
                <p className="mt-3 text-lg font-semibold text-slate-900">Up to {getMaxCredits(form.hoursPerDay)} credits</p>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-4">
              <button
                type="submit"
                disabled={processing}
                className="inline-flex h-12 items-center justify-center gap-2 rounded-full bg-[#1668DC] px-6 text-sm font-semibold text-white transition hover:bg-[#1659c9] disabled:cursor-wait disabled:bg-slate-400"
              >
                <FaCalendarCheck className="h-4 w-4" />
                {processing ? "Loading Education Plans..." : "Generate Education Plans"}
              </button>

              {processing && (
                <div className="inline-flex h-12 min-w-[180px] items-center justify-center rounded-full border border-[#BFD4F7] bg-[#E8F1FF] px-5 text-sm font-semibold text-[#1668DC]">
                  {processingSteps[processingStep]}
                </div>
              )}
            </div>
          </form>
        )}

        {step === "plan" && plan?.options?.length > 0 && (
          <div className="space-y-6">
            <div className="grid gap-5">
              {plan.options.map((option) => (
                <div key={option.id} className="rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div className="max-w-3xl">
                      <p className="text-xs uppercase tracking-[0.3em] text-[#1668DC]">Matched Education Plan</p>
                      <h2 className="mt-2 text-2xl font-semibold text-slate-900">{option.name}</h2>
                      <p className="mt-2 text-sm leading-6 text-slate-600">{option.description}</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <span className="inline-flex h-10 items-center justify-center rounded-full bg-[#E8F1FF] px-4 text-sm font-semibold text-[#1668DC]">
                        Max {option.maxCredits} credits
                      </span>
                      <span className="inline-flex h-10 items-center justify-center rounded-full bg-slate-100 px-4 text-sm font-semibold text-slate-700">
                        {option.semesters.length} semesters
                      </span>
                    </div>
                  </div>

                  <div className="mt-6 grid gap-4">
                    {option.semesters.map((semester) => (
                      <div key={`${option.id}-${semester.title}`} className="rounded-[20px] border border-[#E6EAF3] bg-slate-50 p-4">
                        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                          <div>
                            <h3 className="text-lg font-semibold text-slate-900">{semester.title}</h3>
                            <p className="mt-1 text-sm text-slate-500">{semester.courses.length} courses planned in prerequisite-aware order</p>
                          </div>
                          <span className="inline-flex h-9 items-center justify-center rounded-full bg-white px-4 text-sm font-semibold text-slate-700">
                            {semester.credits} credits
                          </span>
                        </div>

                        <div className="mt-4 grid gap-3 md:grid-cols-2">
                          {semester.courses.map((course) => (
                            <div key={`${option.id}-${semester.title}-${course.code}`} className="rounded-[16px] border border-[#E6EAF3] bg-white p-4">
                              <div className="flex items-start justify-between gap-3">
                                <div>
                                  <p className="font-semibold text-slate-900">{course.code}</p>
                                  <p className="mt-1 text-sm leading-6 text-slate-600">{course.name}</p>
                                </div>
                                <span className="rounded-full bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700">{course.credits} cr</span>
                              </div>
                              <div className="mt-3 grid gap-2 text-xs leading-5 text-slate-500">
                                <p>Prerequisite: {course.prerequisite || "None"}</p>
                                <p>Corequisite: {course.corequisite || "None"}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
              <div className="flex items-start gap-3">
                <FaCheckCircle className="mt-1 h-5 w-5 flex-shrink-0 text-[#059669]" />
                <p className="text-sm leading-6 text-slate-600">
                  PathFinder used the selected program catalog, recommended course order, your completed credits, and daily study capacity to keep each semester within the 8-18 credit planning range.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

const AcademicProfilePanel = ({ university, program, creditsCompleted }) => (
  <div className="overflow-hidden rounded-[24px] border border-[#DCE3F0] bg-white p-5 shadow-sm">
    <div className="grid gap-5 lg:grid-cols-[64px_1fr_140px] lg:items-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#E8F1FF] text-[#1668DC]">
        <FaGraduationCap className="h-7 w-7" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Your Academic Profile</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-4">
          <CompactProfileField label="University" value={university} />
          <CompactProfileField label="Program" value={program} />
          <CompactProfileField label="Academic Year" value="2026 - 2027" />
          <CompactProfileField label="Credits Earned" value={creditsCompleted} />
        </div>
      </div>
      <div className="hidden h-24 rounded-[14px] bg-gradient-to-br from-[#E8F1FF] via-white to-[#FFE9C7] p-4 lg:block">
        <div className="ml-auto h-14 w-16 rounded-t-[8px] border border-[#BFD4F7] bg-white/80" />
        <div className="mt-2 h-3 rounded-full bg-emerald-200" />
      </div>
    </div>
  </div>
);

const CompactProfileField = ({ label, value }) => (
  <div className="border-l border-[#DCE3F0] pl-4 first:border-l-0 first:pl-0">
    <p className="text-xs text-slate-500">{label}</p>
    <p className="mt-2 text-sm font-semibold leading-5 text-slate-900">{value}</p>
  </div>
);

const suggestionMeta = [
  {
    icon: FaGraduationCap,
    detail: "Generate a complete semester-by-semester roadmap to graduate on time.",
    color: "border-violet-100 bg-violet-50 text-violet-600",
  },
  {
    icon: FaChartLine,
    detail: "Build a balanced plan with even credits and manageable workload each semester.",
    color: "border-blue-100 bg-blue-50 text-blue-600",
  },
  {
    icon: FaRocket,
    detail: "Optimize your plan to reduce stress while meeting all degree requirements.",
    color: "border-emerald-100 bg-emerald-50 text-emerald-600",
  },
  {
    icon: FaBookOpen,
    detail: "Create a plan that respects prerequisites and stays within credit limits.",
    color: "border-orange-100 bg-orange-50 text-orange-600",
  },
];

const PromptSuggestionCard = ({ suggestion, index, onSelect }) => {
  const meta = suggestionMeta[index] || suggestionMeta[0];
  const Icon = meta.icon;

  return (
    <button
      type="button"
      onClick={() => onSelect(suggestion)}
      className="min-h-[190px] rounded-[16px] border border-[#DCE3F0] bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-[#BFD4F7] hover:shadow-md"
    >
      <span className={`flex h-12 w-12 items-center justify-center rounded-full border ${meta.color}`}>
        <Icon className="h-5 w-5" />
      </span>
      <span className="mt-5 block text-base font-semibold leading-6 text-slate-900">{suggestion}</span>
      <span className="mt-3 block text-sm leading-6 text-slate-600">{meta.detail}</span>
    </button>
  );
};

const PathfinderAssistantPanel = ({ completedCredits, selectedProgram }) => {
  const totalCredits = Number(selectedProgram?.total_credit_hours) || 120;
  const remainingCredits = Math.max(totalCredits - completedCredits, 0);
  const graduationProgress = Math.min(Math.round((completedCredits / totalCredits) * 100), 100);

  return (
    <aside className="rounded-[24px] border border-[#DCE3F0] bg-white shadow-sm lg:sticky lg:top-6">
      <div className="border-b border-[#E6EAF3] p-5">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-[#E8F1FF] text-[#1668DC]">
            <FaRobot className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">AI Planning Assistant</h2>
            <p className="text-sm text-slate-500">Insights about your academic journey</p>
          </div>
        </div>
      </div>

      <div className="space-y-3 p-5">
        <AssistantMetric
          icon={FaChartLine}
          label="Graduation Progress"
          value={`${graduationProgress}%`}
          helper={`${completedCredits} of ${totalCredits} credits completed`}
          progress={graduationProgress}
        />
        <AssistantMetric icon={FaBookmark} label="Remaining Credits" value={remainingCredits} helper="Credits to graduate" />
        <AssistantMetric icon={FaCalendarAlt} label="Estimated Graduation" value={remainingCredits <= 60 ? "Spring 2028" : "Spring 2030"} helper="Based on current progress" />
        <AssistantMetric icon={FaChartLine} label="Optimal Course Load" value="12 - 15 credits" helper="Recommended per semester" />
      </div>

      <div className="border-t border-[#E6EAF3] p-5">
        <h3 className="font-semibold text-slate-900">PathFinder AI Capabilities</h3>
        <div className="mt-4 space-y-4">
          <Capability icon={FaCheckCircle} title="Prerequisite Validation" detail="Ensure all course requirements are met" />
          <Capability icon={FaBolt} title="Smart Course Sequencing" detail="Optimize course order for success" />
          <Capability icon={FaChartLine} title="Workload Optimization" detail="Balance credits and difficulty" />
          <Capability icon={FaCalendarCheck} title="Graduation Forecasting" detail="Predict graduation timeline" />
          <Capability icon={FaShieldAlt} title="Credit Rule Compliance" detail="Stay within university guidelines" />
        </div>
      </div>
    </aside>
  );
};

const AssistantMetric = ({ icon: Icon, label, value, helper, progress }) => (
  <div className="rounded-[12px] border border-[#E6EAF3] bg-slate-50 p-4">
    <div className="flex items-start justify-between gap-3">
      <div className="flex items-start gap-3">
        <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-white text-[#1668DC]">
          <Icon className="h-4 w-4" />
        </span>
        <div>
          <p className="text-sm font-semibold text-slate-900">{label}</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
        </div>
      </div>
    </div>
    {typeof progress === "number" && (
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">
        <div className="h-full rounded-full bg-[#1668DC]" style={{ width: `${progress}%` }} />
      </div>
    )}
    <p className="mt-2 text-sm text-slate-500">{helper}</p>
  </div>
);

const Capability = ({ icon: Icon, title, detail }) => (
  <div className="flex gap-3">
    <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
      <Icon className="h-3.5 w-3.5" />
    </span>
    <div>
      <p className="text-sm font-semibold text-slate-900">{title}</p>
      <p className="mt-1 text-xs leading-5 text-slate-500">{detail}</p>
    </div>
  </div>
);

export default PathfinderPage;
