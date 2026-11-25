import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import CollegeDetail from "../components/university/CollegeDetail.jsx";
import { getUniversityById } from "../services/universityService.js";
import { load as loadStorage, save as saveStorage } from "../utils/storage.js";

const CollegeDetailPage = () => {
  const { unitId } = useParams();
  const location = useLocation();
  const initialCollege = location.state?.college || loadStorage("LastCollegeDetail", null);
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
        const resolved = detail || initialCollege || null;
        setCollege(resolved);
        if (resolved) {
          saveStorage("LastCollegeDetail", resolved);
        }
      } catch (err) {
        console.error(err);
        setError("Unable to load college details.");
        setCollege(initialCollege || null);
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
            College <span className="text-[#0069e0]">Details</span>
          </h1>
          {college ? (
            <p className="text-lg mt-2 font-semibold text-slate-600">
              {college.name || college.university} · {college.city},{" "}
              {college.state}
            </p>
          ) : (
            <p className="text-sm text-slate-600">
              Loading College/University information…
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
          Loading College/University information…
        </div>
      ) : college ? (
        <CollegeDetail college={college} />
      ) : (
        <div className="text-sm text-slate-600 bg-white border border-slate-200 rounded-xl p-4">
          College not found.
        </div>
      )}
    </section>
  );
};

export default CollegeDetailPage;
