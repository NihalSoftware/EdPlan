import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FaArrowLeft,
  FaBolt,
  FaBookOpen,
  FaBookmark,
  FaChartLine,
  FaCheckCircle,
  FaCompass,
  FaGraduationCap,
  FaMagic,
  FaRobot,
  FaShieldAlt,
} from "react-icons/fa";

const domainOptions = [
  {
    id: "technology",
    label: "Technology",
    description: "Software, cyber defense, AI systems, cloud platforms, and product engineering.",
    specializations: [
      { id: "cybersecurity", label: "Cybersecurity", description: "Security operations, threat defense, cloud security, and digital forensics." },
      { id: "data-ai", label: "AI & Machine Learning", description: "Machine learning, analytics, intelligent systems, and data products." },
      { id: "software-engineering", label: "Software Engineering", description: "Full-stack development, architecture, testing, and product-ready engineering." },
      { id: "cloud-devops", label: "Cloud & DevOps", description: "Cloud architecture, deployment pipelines, automation, and reliability." },
    ],
  },
  {
    id: "finance",
    label: "Finance & Banking",
    description: "Risk analytics, fintech systems, compliance, payment platforms, and banking operations.",
    specializations: [
      { id: "fintech", label: "FinTech Systems", description: "Digital payments, financial platforms, secure transactions, and product analytics." },
      { id: "risk-analytics", label: "Risk Analytics", description: "Modeling, forecasting, credit risk, fraud detection, and decision support." },
      { id: "banking-compliance", label: "Banking Compliance", description: "Governance, policy, audit readiness, privacy, and secure operations." },
    ],
  },
  {
    id: "business",
    label: "Business Growth",
    description: "Sales strategy, marketing analytics, entrepreneurship, operations, and customer growth.",
    specializations: [
      { id: "sales-ops", label: "Sales Operations", description: "CRM workflows, pipeline analysis, negotiation, and revenue operations." },
      { id: "marketing-analytics", label: "Marketing Analytics", description: "Campaign analysis, customer segmentation, experimentation, and growth metrics." },
      { id: "product-management", label: "Product Management", description: "Roadmaps, user research, market fit, and cross-functional delivery." },
    ],
  },
  {
    id: "healthcare",
    label: "Healthcare & Life Sciences",
    description: "Health informatics, data privacy, clinical systems, and patient-centered operations.",
    specializations: [
      { id: "health-informatics", label: "Health Informatics", description: "Electronic health systems, healthcare data, and clinical decision support." },
      { id: "biomedical-data", label: "Biomedical Data", description: "Biostatistics, research data, modeling, and life-science analytics." },
    ],
  },
  {
    id: "public-service",
    label: "Public Service & Policy",
    description: "Education, government systems, public policy, civic technology, and community impact.",
    specializations: [
      { id: "education-tech", label: "Education Technology", description: "Learning platforms, academic data, student success, and digital classrooms." },
      { id: "public-policy", label: "Public Policy Analytics", description: "Policy research, civic data, communication, and program evaluation." },
    ],
  },
];

const recommendationSets = {
  cybersecurity: {
    confidence: "94%",
    courses: [
      { code: "CYBR 430", name: "Machine Learning", match: "96%", reason: "Strong fit for AI-driven security analytics." },
      { code: "CYBR 410", name: "Cloud Computing", match: "91%", reason: "Supports secure cloud architecture and DevOps workflows." },
      { code: "DATA 340", name: "Data Mining", match: "89%", reason: "Helps build predictive models for threat detection." },
      { code: "CYBR 440", name: "Cyber Threat Intelligence", match: "87%", reason: "Enhances your understanding of adversary behavior." },
      { code: "CYBR 320", name: "Network Security", match: "86%", reason: "Core course for secure infrastructure design." },
      { code: "CYBR 360", name: "Digital Forensics", match: "84%", reason: "Teaches evidence collection and incident response." },
    ],
  },
  "data-ai": {
    confidence: "92%",
    courses: [
      { code: "DATA 340", name: "Data Mining", match: "95%", reason: "Builds pattern discovery skills for large academic and career datasets." },
      { code: "C S 469", name: "Artificial Intelligence", match: "93%", reason: "Supports planning toward intelligent systems and automation work." },
      { code: "STAT 2510", name: "Statistics for Engineers", match: "90%", reason: "Gives the statistical base needed for reliable modeling." },
      { code: "C S 482", name: "Database Management Systems", match: "88%", reason: "Strengthens data storage, querying, and design fundamentals." },
      { code: "C S 477", name: "Algorithms", match: "85%", reason: "Improves model efficiency and technical interview readiness." },
      { code: "C S 456", name: "Computer Networks", match: "81%", reason: "Useful for data platforms that depend on distributed systems." },
    ],
  },
  "software-engineering": {
    confidence: "90%",
    courses: [
      { code: "C S 371", name: "Software Development", match: "96%", reason: "Directly matches product-building, teamwork, and implementation goals." },
      { code: "C S 458", name: "Software Engineering", match: "94%", reason: "Covers scalable process, testing, design, and delivery practices." },
      { code: "C S 482", name: "Database Management Systems", match: "89%", reason: "Important for full-stack apps and production data design." },
      { code: "C S 477", name: "Algorithms", match: "87%", reason: "Improves code quality, performance reasoning, and interviews." },
      { code: "C S 488", name: "Senior Design I", match: "85%", reason: "Turns prior coursework into a portfolio-grade project." },
      { code: "C S 489", name: "Senior Design II", match: "83%", reason: "Completes the capstone sequence with delivery experience." },
    ],
  },
  "cloud-devops": {
    confidence: "91%",
    courses: [
      { code: "CYBR 410", name: "Cloud Computing", match: "96%", reason: "Best foundation for cloud architecture and deployment patterns." },
      { code: "C S 456", name: "Computer Networks", match: "91%", reason: "Strengthens distributed infrastructure and service communication." },
      { code: "C S 474", name: "Operating Systems", match: "88%", reason: "Builds systems knowledge for reliability and automation work." },
      { code: "C S 458", name: "Software Engineering", match: "86%", reason: "Supports production delivery and team-based engineering." },
      { code: "CYBR 320", name: "Network Security", match: "84%", reason: "Adds secure infrastructure practices for cloud environments." },
    ],
  },
  fintech: {
    confidence: "89%",
    courses: [
      { code: "BUS 330", name: "Security Policy", match: "92%", reason: "Relevant for regulated financial products and risk controls." },
      { code: "C S 482", name: "Database Management Systems", match: "90%", reason: "Supports transaction data, reporting, and product backends." },
      { code: "DATA 340", name: "Data Mining", match: "88%", reason: "Useful for customer insights and fraud pattern discovery." },
      { code: "C S 458", name: "Software Engineering", match: "86%", reason: "Helps deliver dependable financial software." },
      { code: "STAT 2510", name: "Statistics for Engineers", match: "83%", reason: "Builds confidence with financial metrics and forecasting." },
    ],
  },
  "risk-analytics": {
    confidence: "91%",
    courses: [
      { code: "STAT 2510", name: "Statistics for Engineers", match: "95%", reason: "Core base for risk modeling and quantitative decision making." },
      { code: "DATA 340", name: "Data Mining", match: "92%", reason: "Supports fraud detection, credit scoring, and anomaly analysis." },
      { code: "C S 469", name: "Artificial Intelligence", match: "88%", reason: "Useful for predictive risk systems." },
      { code: "BUS 330", name: "Security Policy", match: "84%", reason: "Connects analytics decisions to compliance expectations." },
    ],
  },
  "banking-compliance": {
    confidence: "88%",
    courses: [
      { code: "BUS 330", name: "Security Policy", match: "95%", reason: "Strong match for governance, policy, and audit readiness." },
      { code: "CYBR 360", name: "Digital Forensics", match: "87%", reason: "Supports investigation and evidence handling." },
      { code: "CYBR 320", name: "Network Security", match: "85%", reason: "Builds understanding of secure banking infrastructure." },
      { code: "COMM 1115", name: "Introduction to Communication", match: "82%", reason: "Useful for policy documentation and stakeholder communication." },
    ],
  },
  "sales-ops": {
    confidence: "87%",
    courses: [
      { code: "BUS 320", name: "Sales Management", match: "94%", reason: "Builds pipeline, territory, and performance management skills." },
      { code: "DATA 340", name: "Data Mining", match: "88%", reason: "Useful for lead scoring and customer segmentation." },
      { code: "COMM 1115", name: "Introduction to Communication", match: "86%", reason: "Supports persuasion, discovery calls, and client communication." },
      { code: "STAT 2510", name: "Statistics for Engineers", match: "80%", reason: "Helps interpret sales experiments and forecasts." },
    ],
  },
  "marketing-analytics": {
    confidence: "89%",
    courses: [
      { code: "DATA 340", name: "Data Mining", match: "94%", reason: "Strong fit for segmentation and campaign analysis." },
      { code: "STAT 2510", name: "Statistics for Engineers", match: "90%", reason: "Supports A/B testing and performance interpretation." },
      { code: "C S 482", name: "Database Management Systems", match: "85%", reason: "Useful for customer data and reporting workflows." },
      { code: "COMM 1115", name: "Introduction to Communication", match: "83%", reason: "Connects analysis to persuasive messaging." },
    ],
  },
  "product-management": {
    confidence: "88%",
    courses: [
      { code: "C S 371", name: "Software Development", match: "91%", reason: "Helps product managers work fluently with engineering teams." },
      { code: "C S 458", name: "Software Engineering", match: "89%", reason: "Builds delivery and scope management knowledge." },
      { code: "COMM 1115", name: "Introduction to Communication", match: "87%", reason: "Useful for stakeholder alignment and user interviews." },
      { code: "DATA 340", name: "Data Mining", match: "84%", reason: "Supports product metrics and user behavior analysis." },
    ],
  },
  "health-informatics": {
    confidence: "86%",
    courses: [
      { code: "C S 482", name: "Database Management Systems", match: "92%", reason: "Relevant for patient records and health information systems." },
      { code: "BUS 330", name: "Security Policy", match: "88%", reason: "Supports privacy, compliance, and healthcare governance." },
      { code: "DATA 340", name: "Data Mining", match: "86%", reason: "Useful for clinical trends and operational insights." },
      { code: "C S 458", name: "Software Engineering", match: "82%", reason: "Helps build reliable health technology products." },
    ],
  },
  "biomedical-data": {
    confidence: "85%",
    courses: [
      { code: "STAT 2510", name: "Statistics for Engineers", match: "93%", reason: "Core preparation for biomedical research analysis." },
      { code: "DATA 340", name: "Data Mining", match: "90%", reason: "Supports discovery patterns in life-science datasets." },
      { code: "C S 469", name: "Artificial Intelligence", match: "84%", reason: "Useful for biomedical modeling and prediction." },
      { code: "MATH 2530", name: "Calculus III", match: "80%", reason: "Adds quantitative depth for advanced modeling." },
    ],
  },
  "education-tech": {
    confidence: "87%",
    courses: [
      { code: "C S 371", name: "Software Development", match: "91%", reason: "Useful for building student-facing learning tools." },
      { code: "DATA 340", name: "Data Mining", match: "88%", reason: "Supports student success analytics and personalization." },
      { code: "C S 482", name: "Database Management Systems", match: "85%", reason: "Important for academic records and learning platforms." },
      { code: "COMM 1115", name: "Introduction to Communication", match: "83%", reason: "Helps translate technical ideas for educators and students." },
    ],
  },
  "public-policy": {
    confidence: "84%",
    courses: [
      { code: "STAT 2510", name: "Statistics for Engineers", match: "89%", reason: "Helps evaluate policy outcomes with evidence." },
      { code: "DATA 340", name: "Data Mining", match: "87%", reason: "Useful for civic datasets and program analysis." },
      { code: "BUS 330", name: "Security Policy", match: "84%", reason: "Connects governance, regulation, and operational policy." },
      { code: "COMM 1115", name: "Introduction to Communication", match: "82%", reason: "Supports public-facing policy communication." },
    ],
  },
};

const promptSuggestions = [
  "I want to study cybersecurity and ethical hacking",
  "Recommend courses for AI and machine learning",
  "I am interested in banking, fintech, and risk analytics",
  "I want courses for sales, marketing, and product growth",
  "Show me courses for healthcare data and informatics",
];

const focusKeywordMap = [
  { id: "cybersecurity", keywords: ["cyber", "security", "hacking", "threat", "forensics", "network security"] },
  { id: "data-ai", keywords: ["ai", "artificial intelligence", "machine learning", "ml", "data science", "analytics"] },
  { id: "software-engineering", keywords: ["software", "full stack", "frontend", "backend", "app", "developer", "engineering"] },
  { id: "cloud-devops", keywords: ["cloud", "devops", "aws", "azure", "deployment", "infrastructure"] },
  { id: "fintech", keywords: ["fintech", "payment", "payments", "financial technology", "finance product"] },
  { id: "risk-analytics", keywords: ["risk", "fraud", "credit", "forecast", "bank analytics"] },
  { id: "banking-compliance", keywords: ["banking", "compliance", "audit", "policy", "governance"] },
  { id: "sales-ops", keywords: ["sales", "crm", "revenue", "pipeline", "business development"] },
  { id: "marketing-analytics", keywords: ["marketing", "campaign", "growth", "customer", "segmentation"] },
  { id: "product-management", keywords: ["product", "roadmap", "user research", "market fit"] },
  { id: "health-informatics", keywords: ["healthcare", "health", "clinical", "patient", "informatics"] },
  { id: "biomedical-data", keywords: ["biomedical", "biology", "bio", "life science", "research data"] },
  { id: "education-tech", keywords: ["education", "edtech", "learning", "student success", "teaching"] },
  { id: "public-policy", keywords: ["public", "policy", "government", "civic", "social impact"] },
];

const allFocusOptions = domainOptions.flatMap((domain) =>
  domain.specializations.map((specialization) => ({
    ...specialization,
    domainLabel: domain.label,
  }))
);

const findFocusByPrompt = (prompt) => {
  const normalizedPrompt = prompt.toLowerCase();
  const rankedMatches = focusKeywordMap.map((entry) => ({
    id: entry.id,
    score: entry.keywords.reduce((total, keyword) => (normalizedPrompt.includes(keyword) ? total + 1 : total), 0),
  }));
  const bestMatch = rankedMatches.sort((a, b) => b.score - a.score)[0];
  return bestMatch?.score > 0 ? bestMatch.id : "data-ai";
};

const CourseCompassPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedFocus, setSelectedFocus] = useState("");
  const [domainPrompt, setDomainPrompt] = useState("");
  const [submittedPrompt, setSubmittedPrompt] = useState("");
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetch("/assets/nexus_data.json")
      .then((res) => res.json())
      .then((json) => setData(json))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <section className="p-6 min-h-screen bg-slate-50">
        <div className="mx-auto flex max-w-6xl items-center justify-center py-32 text-slate-500">
          Loading CourseCompass...
        </div>
      </section>
    );
  }

  const compass = data?.coursecompass;
  const summary = compass?.summary;
  const selectedFocusOption = allFocusOptions.find((option) => option.id === selectedFocus);
  const recommendations = selectedFocus ? recommendationSets[selectedFocus] : null;

  if (!compass || !summary) {
    return (
      <section className="p-6 min-h-screen bg-slate-50">
        <div className="mx-auto max-w-6xl rounded-3xl bg-white p-10 shadow">Unable to load CourseCompass recommendations.</div>
      </section>
    );
  }

  const runAgent = (event) => {
    event.preventDefault();
    if (!domainPrompt.trim() || processing) return;

    setProcessing(true);
    setSelectedFocus("");
    window.setTimeout(() => {
      setSelectedFocus(findFocusByPrompt(domainPrompt));
      setSubmittedPrompt(domainPrompt);
      setProcessing(false);
    }, 700);
  };

  return (
    <section className="min-h-screen bg-[#F4F7FC] p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="relative overflow-hidden rounded-[24px] border border-[#DCE3F0] bg-gradient-to-br from-[#F2EAFF] via-white to-[#EAF3FF] p-8 shadow-sm">
          <div className="pointer-events-none absolute right-8 top-7 hidden h-32 w-56 rounded-[50%] border border-[#C4B5FD] opacity-70 lg:block" />
          <div className="pointer-events-none absolute right-14 top-14 hidden h-24 w-48 rotate-[-18deg] rounded-[50%] border border-[#BFD4F7] opacity-70 lg:block" />
          <div className="pointer-events-none absolute right-32 top-20 hidden text-4xl text-[#7C3AED] lg:block">+</div>
          <div className="relative flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div className="flex max-w-3xl gap-5">
              <div className="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-full bg-[#F0E7FF] text-[#7C3AED]">
                <FaCompass className="h-7 w-7" />
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-[0.38em] text-[#7C3AED]">CourseCompass AI</p>
                <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-900">{selectedFocus ? "Recommended Courses" : "Ask for Course Guidance"}</h1>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                  {selectedFocus
                    ? `Matched to ${selectedFocusOption?.domainLabel} - ${selectedFocusOption?.label}.`
                    : "Describe the domain you want to study and CourseCompass will infer the closest academic track, then recommend courses ranked by fit."}
                </p>
              </div>
            </div>
            {selectedFocus ? (
              <button
                type="button"
                onClick={() => {
                  setSelectedFocus("");
                  setSubmittedPrompt("");
                }}
                className="inline-flex h-11 items-center justify-center rounded-full border border-[#DCE3F0] bg-slate-50 px-5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              >
                Ask Again
              </button>
            ) : (
              <Link
                to="/nexus"
                className="inline-flex h-11 items-center justify-center gap-2 rounded-full border border-[#DCE3F0] bg-white/80 px-5 text-sm font-semibold text-slate-700 transition hover:bg-white"
              >
                <FaArrowLeft className="h-4 w-4" />
                Back to Nexus
              </Link>
            )}
          </div>

          {selectedFocus && (
            <div className="mt-7 grid gap-4 md:grid-cols-3">
              <div className="rounded-[20px] border border-[#E6EAF3] bg-slate-50 p-5 min-w-0">
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Recommendations</p>
                <p className="mt-3 text-2xl font-semibold text-slate-900 break-words">{recommendations.courses.length}</p>
              </div>
              <div className="rounded-[20px] border border-[#E6EAF3] bg-slate-50 p-5 min-w-0">
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Match Confidence</p>
                <p className="mt-3 text-2xl font-semibold text-slate-900 break-words">{recommendations.confidence}</p>
              </div>
              <div className="rounded-[20px] border border-[#E6EAF3] bg-slate-50 p-5 min-w-0">
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Selected Track</p>
                <p className="mt-3 text-2xl font-semibold text-slate-900 break-words">{selectedFocusOption?.label || summary.focusArea}</p>
              </div>
            </div>
          )}
        </div>

        {!selectedFocus ? (
          <div className="grid gap-6 lg:grid-cols-[1fr_344px]">
            <div className="space-y-6">
              <CourseCompassProfilePanel summary={summary} />

              <div className="rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-2xl bg-[#F0E7FF] text-[#7C3AED]">
                    <FaRobot className="h-6 w-6" />
                  </div>
                  <div className="w-full">
                    <div className="max-w-3xl rounded-[20px] border border-[#E6EAF3] bg-slate-50 px-5 py-4 text-sm leading-6 text-slate-700">
                      What domain do you want to study? You can type things like cybersecurity, AI, banking, sales, healthcare, public policy, cloud, or product management.
                    </div>

                    <form onSubmit={runAgent} className="mt-5 rounded-[18px] border border-[#C8D4EA] bg-slate-50 p-4 transition focus-within:border-[#7C3AED] focus-within:bg-white">
                      <textarea
                        value={domainPrompt}
                        onChange={(event) => setDomainPrompt(event.target.value)}
                        className="min-h-[150px] w-full resize-none bg-transparent text-base leading-7 text-slate-800 outline-none"
                        placeholder="Example: I want to study AI and machine learning for future data science roles."
                      />
                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <div className="flex items-center gap-3">
                          <FaMagic className="h-4 w-4" />
                          <FaBookmark className="h-4 w-4" />
                        </div>
                        <span>{domainPrompt.length} characters</span>
                      </div>
                      <div className="mt-5 flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
                        <div className="flex flex-wrap gap-2">
                          {promptSuggestions.slice(0, 3).map((suggestion) => (
                            <button
                              key={suggestion}
                              type="button"
                              onClick={() => setDomainPrompt(suggestion)}
                              className="rounded-full border border-[#DCE3F0] bg-white px-3 py-2 text-xs font-semibold text-slate-600 transition hover:border-[#7C3AED] hover:text-[#7C3AED]"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                        <button
                          type="submit"
                          disabled={!domainPrompt.trim() || processing}
                          className="inline-flex h-12 items-center justify-center gap-2 rounded-[8px] bg-gradient-to-r from-[#7C3AED] to-[#1668DC] px-6 text-sm font-semibold text-white shadow-sm transition hover:brightness-105 disabled:cursor-not-allowed disabled:bg-none disabled:bg-slate-300 disabled:shadow-none"
                        >
                          <FaBolt className="h-4 w-4" />
                          {processing ? "Analysing..." : "Recommend Courses"}
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>

              <div className="rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <FaBolt className="h-4 w-4 text-[#7C3AED]" />
                  <h2 className="text-lg font-semibold text-slate-900">Prompt Suggestions</h2>
                </div>
                <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {promptSuggestions.map((suggestion, index) => (
                    <CompassSuggestionCard key={suggestion} suggestion={suggestion} index={index} onSelect={setDomainPrompt} />
                  ))}
                </div>
              </div>
            </div>

            <CourseCompassAssistantPanel summary={summary} />
          </div>
        ) : (
          <div className="space-y-6">
            <div className="rounded-[28px] border border-[#DCE3F0] bg-white p-6 shadow-sm">
              <div className="space-y-4">
                <div className="flex justify-end">
                  <div className="max-w-2xl rounded-[20px] bg-[#7C3AED] px-5 py-4 text-sm font-semibold leading-6 text-white shadow-sm">
                    {submittedPrompt}
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-2xl bg-[#F0E7FF] text-[#7C3AED]">
                    <FaRobot className="h-6 w-6" />
                  </div>
                  <div className="max-w-3xl rounded-[20px] border border-[#E6EAF3] bg-slate-50 px-5 py-4 text-sm leading-6 text-slate-700">
                    I interpreted your interest as <span className="font-semibold text-slate-900">{selectedFocusOption?.label}</span>. Here are the strongest course matches, ranked by fit.
                  </div>
                </div>
              </div>
            </div>
            <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {recommendations.courses.map((course) => (
                <div key={course.code} className="flex h-full flex-col rounded-[24px] border border-[#DCE3F0] bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <h2 className="text-xl font-semibold text-slate-900 break-words">{course.name}</h2>
                    </div>
                    <div className="rounded-full bg-[#E8F1FF] px-4 py-2 text-sm font-semibold text-[#1668DC] whitespace-nowrap">
                      {course.match}
                    </div>
                  </div>
                  <p className="mt-4 flex-1 text-sm leading-6 text-slate-600 break-words">{course.reason}</p>
                  <button className="mt-6 inline-flex w-full items-center justify-center rounded-full bg-[#1668DC] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#1659c9]">
                    Add To Plan
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

const CourseCompassProfilePanel = ({ summary }) => (
  <div className="overflow-hidden rounded-[24px] border border-[#DCE3F0] bg-white p-5 shadow-sm">
    <div className="grid gap-5 lg:grid-cols-[64px_1fr_140px] lg:items-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#F0E7FF] text-[#7C3AED]">
        <FaGraduationCap className="h-7 w-7" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Your Course Matching Profile</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-4">
          <CompassProfileField label="Current Focus" value={summary.focusArea} />
          <CompassProfileField label="Recommendations" value={summary.recommendations} />
          <CompassProfileField label="Match Confidence" value={summary.matchConfidence} />
          <CompassProfileField label="Readiness" value="High" />
        </div>
      </div>
      <div className="hidden h-24 rounded-[14px] bg-gradient-to-br from-[#F0E7FF] via-white to-[#E8F1FF] p-4 lg:block">
        <div className="ml-auto h-14 w-16 rounded-t-[8px] border border-[#C4B5FD] bg-white/80" />
        <div className="mt-2 h-3 rounded-full bg-violet-200" />
      </div>
    </div>
  </div>
);

const CompassProfileField = ({ label, value }) => (
  <div className="border-l border-[#DCE3F0] pl-4 first:border-l-0 first:pl-0">
    <p className="text-xs text-slate-500">{label}</p>
    <p className="mt-2 text-sm font-semibold leading-5 text-slate-900">{value}</p>
  </div>
);

const compassSuggestionMeta = [
  {
    icon: FaShieldAlt,
    detail: "Find courses for security operations, threat defense, and ethical hacking.",
    color: "border-violet-100 bg-violet-50 text-violet-600",
  },
  {
    icon: FaChartLine,
    detail: "Match courses for AI systems, analytics, and machine learning pathways.",
    color: "border-blue-100 bg-blue-50 text-blue-600",
  },
  {
    icon: FaBookmark,
    detail: "Explore fintech, banking, compliance, risk, and product analytics courses.",
    color: "border-emerald-100 bg-emerald-50 text-emerald-600",
  },
  {
    icon: FaBolt,
    detail: "Discover courses for sales operations, marketing analytics, and growth roles.",
    color: "border-orange-100 bg-orange-50 text-orange-600",
  },
  {
    icon: FaBookOpen,
    detail: "Find course matches for health informatics and healthcare data work.",
    color: "border-cyan-100 bg-cyan-50 text-cyan-600",
  },
];

const CompassSuggestionCard = ({ suggestion, index, onSelect }) => {
  const meta = compassSuggestionMeta[index] || compassSuggestionMeta[0];
  const Icon = meta.icon;

  return (
    <button
      type="button"
      onClick={() => onSelect(suggestion)}
      className="min-h-[170px] rounded-[16px] border border-[#DCE3F0] bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-[#C4B5FD] hover:shadow-md"
    >
      <span className={`flex h-12 w-12 items-center justify-center rounded-full border ${meta.color}`}>
        <Icon className="h-5 w-5" />
      </span>
      <span className="mt-5 block text-base font-semibold leading-6 text-slate-900">{suggestion}</span>
      <span className="mt-3 block text-sm leading-6 text-slate-600">{meta.detail}</span>
    </button>
  );
};

const CourseCompassAssistantPanel = ({ summary }) => (
  <aside className="rounded-[24px] border border-[#DCE3F0] bg-white shadow-sm lg:sticky lg:top-6">
    <div className="border-b border-[#E6EAF3] p-5">
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-full bg-[#F0E7FF] text-[#7C3AED]">
          <FaRobot className="h-5 w-5" />
        </span>
        <div>
          <h2 className="text-lg font-semibold text-slate-900">CourseCompass Assistant</h2>
          <p className="text-sm text-slate-500">Course matching intelligence</p>
        </div>
      </div>
    </div>

    <div className="space-y-3 p-5">
      <CompassAssistantMetric
        icon={FaCompass}
        label="Current Focus Area"
        value={summary.focusArea}
        helper="Default profile direction"
      />
      <CompassAssistantMetric
        icon={FaChartLine}
        label="Match Confidence"
        value={summary.matchConfidence}
        helper="Based on goal and track fit"
        progress={Number.parseInt(summary.matchConfidence, 10)}
      />
      <CompassAssistantMetric
        icon={FaBookOpen}
        label="Available Suggestions"
        value={summary.recommendations}
        helper="Courses ready for review"
      />
    </div>

    <div className="border-t border-[#E6EAF3] p-5">
      <h3 className="font-semibold text-slate-900">CourseCompass Capabilities</h3>
      <div className="mt-4 space-y-4">
        <CompassCapability icon={FaCheckCircle} title="Prompt Interpretation" detail="Detects the closest academic focus from plain language" />
        <CompassCapability icon={FaChartLine} title="Ranked Course Fit" detail="Orders courses by match strength and career relevance" />
        <CompassCapability icon={FaShieldAlt} title="Track Alignment" detail="Connects courses to domains like security, AI, finance, and healthcare" />
        <CompassCapability icon={FaBolt} title="Plan Actions" detail="Lets students add recommended courses into their plan" />
      </div>
    </div>
  </aside>
);

const CompassAssistantMetric = ({ icon: Icon, label, value, helper, progress }) => (
  <div className="rounded-[12px] border border-[#E6EAF3] bg-slate-50 p-4">
    <div className="flex items-start gap-3">
      <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-white text-[#7C3AED]">
        <Icon className="h-4 w-4" />
      </span>
      <div className="min-w-0">
        <p className="text-sm font-semibold text-slate-900">{label}</p>
        <p className="mt-1 text-2xl font-semibold text-slate-900 break-words">{value}</p>
      </div>
    </div>
    {typeof progress === "number" && (
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">
        <div className="h-full rounded-full bg-[#7C3AED]" style={{ width: `${progress}%` }} />
      </div>
    )}
    <p className="mt-2 text-sm text-slate-500">{helper}</p>
  </div>
);

const CompassCapability = ({ icon: Icon, title, detail }) => (
  <div className="flex gap-3">
    <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-violet-50 text-violet-600">
      <Icon className="h-3.5 w-3.5" />
    </span>
    <div>
      <p className="text-sm font-semibold text-slate-900">{title}</p>
      <p className="mt-1 text-xs leading-5 text-slate-500">{detail}</p>
    </div>
  </div>
);

export default CourseCompassPage;
