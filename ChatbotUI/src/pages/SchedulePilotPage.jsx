import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const SchedulePilotPage = () => {
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
          Loading SchedulePilot...
        </div>
      </section>
    );
  }

  const schedule = data?.schedulepilot;
  const summary = schedule?.summary;

  if (!schedule || !summary) {
    return (
      <section className="p-6 min-h-screen bg-slate-50">
        <div className="mx-auto max-w-6xl rounded-3xl bg-white p-10 shadow">Unable to load SchedulePilot content.</div>
      </section>
    );
  }

  return (
    <section className="p-6 bg-slate-50 min-h-screen">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="flex flex-col gap-4 rounded-[32px] bg-white p-8 shadow-sm border border-slate-200">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-slate-400">SchedulePilot</p>
              <h1 className="text-4xl font-semibold text-slate-900">Semester Schedule</h1>
              <p className="mt-3 max-w-2xl text-slate-600">
                View the mock timetable for your selected semester with workload and prerequisites clearly laid out.
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
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Semester</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">{summary.semester}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 text-center min-h-[140px]">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Total Credits</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">{summary.totalCredits}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 text-center min-h-[140px]">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Course Count</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">{summary.courseCount}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 text-center min-h-[140px]">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Workload</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">{summary.workload}</p>
            </div>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
          <div className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-semibold text-slate-900">Weekly Schedule</h2>
            <p className="mt-2 text-slate-600">A clean schedule view for your mock Fall 2026 semester.</p>
            <div className="mt-6 space-y-4">
              {Object.entries(schedule.schedule).map(([day, classes]) => (
                <div key={day} className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-lg font-semibold text-slate-900">{day}</p>
                    <span className="rounded-full bg-white px-3 py-1 text-sm text-slate-600 shadow-sm">{classes.length} class{classes.length > 1 ? "es" : ""}</span>
                  </div>
                  <ul className="mt-3 space-y-2">
                    {classes.map((course) => (
                      <li key={course} className="rounded-2xl bg-white px-4 py-3 text-slate-700 shadow-sm">{course}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-xl font-semibold text-slate-900">Workload Indicator</h3>
              <p className="mt-2 text-slate-600">The current plan balances your credits and weekly effort to keep progress steady.</p>
              <div className="mt-5 rounded-3xl bg-slate-100 p-4">
                <div className="flex items-center justify-between text-sm text-slate-700">
                  <span>Balanced</span>
                  <span>{summary.workload}</span>
                </div>
                <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-200">
                  <div className="h-3 rounded-full bg-[#0069e0]" style={{ width: "70%" }} />
                </div>
              </div>
            </div>

            <div className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-xl font-semibold text-slate-900">Prerequisite Status</h3>
              <p className="mt-3 rounded-3xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
                {summary.prerequisiteStatus}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SchedulePilotPage;
