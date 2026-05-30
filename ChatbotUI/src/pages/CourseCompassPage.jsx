import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const CourseCompassPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

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

  if (!compass || !summary) {
    return (
      <section className="p-6 min-h-screen bg-slate-50">
        <div className="mx-auto max-w-6xl rounded-3xl bg-white p-10 shadow">Unable to load CourseCompass recommendations.</div>
      </section>
    );
  }

  return (
    <section className="p-6 bg-slate-50 min-h-screen">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="flex flex-col gap-4 rounded-[32px] bg-white p-8 shadow-sm border border-slate-200">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-slate-400">CourseCompass</p>
              <h1 className="text-4xl font-semibold text-slate-900">Recommended Courses</h1>
              <p className="mt-3 max-w-2xl text-slate-600">
                Explore the AI-selected classes that best align to your cybersecurity goals and degree plan.
              </p>
            </div>
            <Link
              to="/nexus"
              className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Back to Nexus
            </Link>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 min-w-0 text-center min-h-[140px]">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Recommendations</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900 break-words">{summary.recommendations}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 min-w-0 text-center min-h-[140px]">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Match Confidence</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900 break-words">{summary.matchConfidence}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 min-w-0 text-center min-h-[140px]">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Focus Area</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900 break-words">{summary.focusArea}</p>
            </div>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {compass.recommendations.map((course) => (
            <div key={course.code} className="flex h-full flex-col rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <p className="text-sm uppercase tracking-[0.22em] text-slate-400">{course.code}</p>
                  <h2 className="mt-2 text-xl font-semibold text-slate-900 break-words">{course.name}</h2>
                </div>
                <div className="rounded-full bg-[#e7f0ff] px-4 py-2 text-sm font-semibold text-[#0f4ba1] whitespace-nowrap">
                  {course.match}
                </div>
              </div>
              <p className="mt-4 text-slate-600 break-words">{course.reason}</p>
              <button className="mt-auto inline-flex w-full items-center justify-center rounded-full bg-[#0069e0] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#0057b8]">
                Add To Plan
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CourseCompassPage;
