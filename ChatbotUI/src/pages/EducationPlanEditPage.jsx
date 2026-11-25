import EducationPlanEditor from '../components/education/EducationPlanEditor.jsx';
import { useLocation } from 'react-router-dom';
import { plannerUniversity } from '../utils/homeNavigation.js';

const EducationPlanEditPage = () => {
  const { search } = useLocation();
  const initialUniversity = plannerUniversity(search);
  return (
  <section className="compact-planner-page">
    <EducationPlanEditor key={initialUniversity || 'saved-selection'} initialUniversity={initialUniversity} />
  </section>
  );
};

export default EducationPlanEditPage;
