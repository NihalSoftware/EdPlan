import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  compareUniversitiesByIds,
  getUniversityById,
} from "../../services/universityService.js";
import {
  load as loadStorage,
  save as saveStorage,
} from "../../utils/storage.js";
import {
  NOT_REPORTED,
  admissionsMetrics,
  costMetrics,
  enrollmentMetrics,
  getMetricValue,
  hasValue,
  institutionMetrics,
  outcomeMetrics,
  overviewMetrics,
} from "./collegeMetrics.jsx";

const SectionCard = ({ title, children, note }) => (
  <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 space-y-3">
    <div>
      <h3 className="text-[22px] font-bold text-slate-700">{title}</h3>
      {note && <p className="text-xs text-slate-500">{note}</p>}
    </div>
    {children}
  </div>
);

const ComparisonTable = ({ title, metrics, schools, note }) => (
  <SectionCard title={title} note={note}>
    <div className="overflow-x-auto">
      <table className="min-w-full">
        <thead>
          <tr className="uppercase tracking-wide text-slate-600">
            <th className="text-left px-3 py-2 font-bold w-1/4">Metric</th>
            {schools.map((school) => (
              <th
                key={school.unit_id || school.name}
                className="text-left px-3 py-2 font-bold w-3/12"
              >
                <span>{school.name || "Selected college"}</span>
                {school.scorecard_source_url && (
                  <a
                    href={school.scorecard_source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="block normal-case tracking-normal text-xs font-medium text-indigo-600 hover:text-indigo-500"
                  >
                    Scorecard source ↗
                  </a>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {metrics.map((metric) => (
            <tr
              key={metric.key || metric.label}
              className="border-t border-slate-100"
            >
              <td className="px-3 py-2 font-medium text-slate-700">
                {metric.label}
              </td>
              {schools.map((school) => {
                const rawValue = getMetricValue(metric, school);
                let content = NOT_REPORTED;

                if (metric.render) {
                  content = metric.render(rawValue, school);
                } else if (metric.format && hasValue(rawValue)) {
                  content = metric.format(rawValue, school);
                } else if (hasValue(rawValue)) {
                  content = String(rawValue);
                }

                return (
                  <td
                    key={`${metric.key || metric.label}-${
                      school.unit_id || school.name
                    }`}
                    className="px-3 py-2 text-slate-800"
                  >
                    {content}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </SectionCard>
);

const CollegeCompare = () => {
  const [selected, setSelected] = useState([]);
  const [comparison, setComparison] = useState({});
  const [loadingCompare, setLoadingCompare] = useState(false);
  const [error, setError] = useState("");
  const [initializing, setInitializing] = useState(true);
  const navigate = useNavigate();

  const handleBackToFind = () => {
    const tempProgram = loadStorage("SelectedProgram", "");
    const tempDegree = loadStorage("SelectedDegreeLevel", "");

    if (tempProgram) {
      saveStorage("Programname", tempProgram);
      saveStorage("Programnameview", tempProgram);
      saveStorage("SelectedProgram", "");
    }
    if (tempDegree) {
      saveStorage("ProgramDegree", tempDegree);
      saveStorage("SelectedDegreeLevel", tempDegree);
    }

    navigate("/uni");
  };

  useEffect(() => {
    const stored = loadStorage("CompareQueue", []);
    if (Array.isArray(stored)) {
      const unique = [];
      const seen = new Set();
      stored.forEach((entry) => {
        if (entry?.unit_id && !seen.has(entry.unit_id)) {
          seen.add(entry.unit_id);
          unique.push(entry);
        }
      });
      setSelected(unique.slice(0, 3));
    }
    setInitializing(false);
  }, []);

  useEffect(() => {
    if (initializing) return;
    saveStorage("CompareQueue", selected);
  }, [selected, initializing]);

  useEffect(() => {
    if (initializing) return;
    if (selected.length === 0) {
      setComparison({});
      return;
    }

    const fetchComparison = async () => {
      setLoadingCompare(true);
      setError("");
      try {
        const unitIds = selected.map((entry) => entry.unit_id);
        const detail =
          unitIds.length === 1
            ? [await getUniversityById(unitIds[0])]
            : await compareUniversitiesByIds(unitIds);
        const mapped = detail.reduce((result, school) => {
          if (school?.unit_id) result[school.unit_id] = school;
          return result;
        }, {});
        setComparison(mapped);
      } catch (requestError) {
        console.error(requestError);
        setError("Unable to load comparison data.");
      } finally {
        setLoadingCompare(false);
      }
    };

    fetchComparison();
  }, [selected, initializing]);

  const handleRemove = (unitId) => {
    setSelected((previous) =>
      previous.filter((entry) => entry.unit_id !== unitId),
    );
    setComparison((previous) => {
      const next = { ...previous };
      delete next[unitId];
      return next;
    });
  };

  const comparisonOrder = useMemo(
    () => selected.map((entry) => comparison[entry.unit_id] || entry),
    [selected, comparison],
  );

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-3xl font-semibold text-slate-900">
          Compare <span className="text-[#0069e0]">Colleges</span>
        </h1>
        <p className="text-lg text-slate-600">
          <button
            type="button"
            onClick={handleBackToFind}
            className="mt-2 mr-2 inline-flex items-center gap-2 px-3 py-2 rounded-lg text-indigo-700 hover:bg-slate-200 text-sm font-medium"
          >
            ← Go Back
          </button>
          Select up to three colleges from Find University for comparison.
        </p>
      </header>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {selected.length > 0 && (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {selected.map((entry) => (
              <span
                key={entry.unit_id}
                className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-700"
              >
                {entry.name}
                <button
                  type="button"
                  aria-label={`Remove ${entry.name} from comparison`}
                  onClick={() => handleRemove(entry.unit_id)}
                  className="text-indigo-500 hover:text-indigo-700"
                >
                  ×
                </button>
              </span>
            ))}
          </div>

          {loadingCompare ? (
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 text-sm text-slate-500">
              Loading data…
            </div>
          ) : (
            <div className="space-y-4">
              <div className="rounded-xl border border-blue-200 bg-blue-50 px-5 py-4 text-sm text-slate-700">
                Details and comparison use the same latest available College
                Scorecard metrics. Suppressed or unpublished values are marked
                as “Not reported.”
              </div>
              <ComparisonTable
                title="College Overview"
                metrics={overviewMetrics}
                schools={comparisonOrder}
              />
              <ComparisonTable
                title="Institution & Academic Profile"
                metrics={institutionMetrics}
                schools={comparisonOrder}
              />
              <ComparisonTable
                title="Admissions & Student Success"
                metrics={admissionsMetrics}
                schools={comparisonOrder}
              />
              <ComparisonTable
                title="Enrollment Breakdown"
                metrics={enrollmentMetrics}
                schools={comparisonOrder}
              />
              <ComparisonTable
                title="Cost of Attendance"
                metrics={costMetrics}
                schools={comparisonOrder}
                note="Net price is the average annual cost after grants and scholarships."
              />
              <ComparisonTable
                title="Financial Aid & Student Outcomes"
                metrics={outcomeMetrics}
                schools={comparisonOrder}
                note="Debt, repayment, and earnings measures cover the applicable federally aided cohorts."
              />
            </div>
          )}
        </div>
      )}

      {!initializing && selected.length === 0 && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 text-sm text-slate-600">
          No Colleges/Universities are selected.
        </div>
      )}
    </section>
  );
};

export default CollegeCompare;
