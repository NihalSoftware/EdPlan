import EducationPlanEditor from '../components/education/EducationPlanEditor.jsx';
import { useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { plannerUniversity } from '../utils/homeNavigation.js';
import { getProgramWithCourses } from '../services/educationPlanService.js';

const EducationPlanEditPage = () => {
  const { search } = useLocation();
  const initialUniversity = plannerUniversity(search);
  const programId = new URLSearchParams(search).get("program_id");
  const [result, setResult] = useState(null);
  useEffect(() => {
    if (!programId) return;
    let active = true;
    if (!/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(programId)) {
      setResult({ id: programId, error: true });
      return;
    }
    getProgramWithCourses(programId)
      .then((program) => { if (active) setResult({ id: programId, program, error: !program }); })
      .catch(() => { if (active) setResult({ id: programId, error: true }); });
    return () => { active = false; };
  }, [programId]);
  if (programId && result?.id !== programId) return <p className="p-6" role="status">Loading the catalog program…</p>;
  if (programId && result?.error) return <p className="p-6" role="alert">The selected catalog program could not be loaded. <a href="/mesa" className="underline">Return to Mesa</a></p>;
  const initialProgram = programId ? result.program : null;
  return (
  <section className="compact-planner-page">
    <EducationPlanEditor key={programId || initialUniversity || 'saved-selection'} initialUniversity={initialProgram?.university || initialUniversity} initialProgram={initialProgram} />
  </section>
  );
};

export default EducationPlanEditPage;
