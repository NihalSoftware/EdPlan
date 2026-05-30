import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const PathfinderPage = () => {
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
          Loading PathFinder...
        </div>
      </section>
    );
  }

  const roadmap = data?.pathfinder;
  const metrics = roadmap?.summary;

  if (!roadmap || !metrics) {
    return (
      <section className="p-6 min-h-screen bg-slate-50">
        <div className="mx-auto max-w-6xl rounded-3xl bg-white p-10 shadow">Unable to load PathFinder roadmap.</div>
      </section>
    );
  }

  return (
    <section className="p-6 bg-slate-50 min-h-screen">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="flex flex-col gap-4 rounded-[32px] bg-white p-8 shadow-sm border border-slate-200">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-slate-400">PathFinder</p>
              <h1 className="text-4xl font-semibold text-slate-900">Academic Roadmap</h1>
              <p className="mt-3 max-w-2xl text-slate-600">
                Review your mock semester plan with credit totals, progress, and graduation timeline.
              </p>
            </div>
            <Link
              to="/nexus"
              className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Back to Nexus
            </Link>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 text-center min-h-[140px]">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Total Credits</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">{metrics.totalCredits}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 text-center min-h-[140px]">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Credits Completed</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">{metrics.creditsCompleted}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 text-center min-h-[140px]">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Progress</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">{metrics.progress}%</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 text-center min-h-[140px]">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Target Graduation</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">{metrics.targetGraduation}</p>
            </div>
          </div>

          <div className="rounded-[28px] bg-slate-100 p-5">
            <div className="h-3 overflow-hidden rounded-full bg-slate-200">
              <div className="h-3 rounded-full bg-[#0069e0]" style={{ width: `${metrics.progress}%` }} />
            </div>
            <p className="mt-3 text-sm text-slate-600">Credit completion progress toward your target degree.</p>
          </div>
        </div>

        <div className="grid gap-6">
          {roadmap.semesters.map((semester, index) => (
            <div key={semester.title} className="relative rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
              <div className="absolute left-6 top-6 h-4 w-4 rounded-full bg-[#0069e0]" />
              <div className="ml-8 space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <h2 className="text-xl font-semibold text-slate-900">{semester.title}</h2>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-700">4 courses</span>
                </div>
                <ul className="grid gap-2 sm:grid-cols-2">
                  {semester.courses.map((course) => (
                    <li key={course} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700">
                      {course}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PathfinderPage;
