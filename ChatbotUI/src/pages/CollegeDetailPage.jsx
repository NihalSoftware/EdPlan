import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import CollegeDetail from "../components/university/CollegeDetail.jsx";
import { getUniversityById } from "../services/universityService.js";
import { load as loadStorage, save as saveStorage } from "../utils/storage.js";
import { INSTITUTION, isNorthernNewMexicoCollege } from "../config/institution.js";

const CollegeDetailPage = () => {
  const { unitId } = useParams();
  const location = useLocation();
  const storedCollege = location.state?.college || loadStorage("LastCollegeDetail", null);
  const initialCollege =
    storedCollege &&
    isNorthernNewMexicoCollege(storedCollege.name || storedCollege.university_name)
      ? storedCollege
      : null;
  const [college, setCollege] = useState(initialCollege);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(!initialCollege);

  useEffect(() => {
    if (!unitId) return;
    const fetchDetail = async () => {
      setLoading(true);
      setError("");
      try {
        const detail = await getUniversityById(unitId);
        const candidate = detail || initialCollege || null;
        const resolved =
          candidate &&
          isNorthernNewMexicoCollege(candidate.name || candidate.university_name)
            ? candidate
            : null;
        setCollege(resolved);
        if (resolved) {
          saveStorage("LastCollegeDetail", resolved);
        }
      } catch (err) {
        console.error(err);
        setError("Unable to refresh NNMC details from College Scorecard.");
        setCollege(
          initialCollege &&
            isNorthernNewMexicoCollege(
              initialCollege.name || initialCollege.university_name
            )
            ? initialCollege
            : null
        );
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [unitId]);

  return (
    <section className="p-6 space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">
            NNMC <span className="text-[#0069e0]">College Details</span>
          </h1>
          {college ? (
            <p className="text-lg mt-2 font-semibold text-slate-600">
              {INSTITUTION.name} · {college.city},{" "}
              {college.state}
            </p>
          ) : (
            <p className="text-sm text-slate-600">
              Loading Northern New Mexico College information…
            </p>
          )}
        </div>
      </header>

      {error && (
        <div className="bg-rose-50 text-rose-700 border border-rose-100 rounded-lg px-4 py-3">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-sm text-slate-600 bg-white border border-slate-200 rounded-xl p-4">
          Loading Northern New Mexico College information…
        </div>
      ) : college ? (
        <CollegeDetail college={college} />
      ) : (
        <div className="text-sm text-slate-600 bg-white border border-slate-200 rounded-xl p-4">
          Northern New Mexico College data could not be loaded. Return to the NNMC Overview and try again.
        </div>
      )}
    </section>
  );
};

export default CollegeDetailPage;
