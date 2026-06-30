import { Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout.jsx";
import HomePage from "./pages/HomePage.jsx";
import EducationPlanEditPage from "./pages/EducationPlanEditPage.jsx";
import ViewEducationPlanPage from "./pages/ViewEducationPlanPage.jsx";
import FindUniversityPage from "./pages/FindUniversityPage.jsx";
import CollegeComparePage from "./pages/CollegeComparePage.jsx";
import CollegeDetailPage from "./pages/CollegeDetailPage.jsx";
import CareerProgramPage from "./pages/CareerProgramPage.jsx";
import ChatbotPage from "./pages/ChatbotPage.jsx";
import ScheduleGenerator from "./pages/ScheduleGenerator.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import SignupPage from "./pages/SignupPage.jsx";
import IntakeForm from "./pages/IntakeForm.jsx";
import EdPlanNexusPage from "./pages/EdPlanNexusPage.jsx";
import EdPlanNexusWorkspacePage from "./pages/EdPlanNexusWorkspacePage.jsx";
import PathCrafterPage from "./pages/PathCrafterPage.jsx";
import SchedulePilotPage from "./pages/SchedulePilotPage.jsx";
import UniversityAdvisorPage from "./pages/UniversityAdvisorPage.jsx";
import FinanceGuidePage from "./pages/FinanceGuidePage.jsx";
import CareerNavigatorPage from "./pages/CareerNavigatorPage.jsx";
import AcademicSuccessPage from "./pages/AcademicSuccessPage.jsx";

const App = () => (
	<Routes>
		<Route element={<AppLayout />}>
			<Route path="/" element={<Navigate to="/home" replace />} />
			<Route path="/home" element={<HomePage />} />
			<Route path="/intake" element={<IntakeForm />} />
			<Route path="/chatbot" element={<ChatbotPage />} />
			<Route path="/educationplan" element={<EducationPlanEditPage />} />
			<Route path="/career" element={<CareerProgramPage />} />
			<Route path="/schedule-generator" element={<ScheduleGenerator />} />
			<Route path="/view" element={<ViewEducationPlanPage />} />
			<Route path="/edplan-nexus" element={<EdPlanNexusPage />} />
			<Route path="/edplan-nexus/workspace" element={<EdPlanNexusWorkspacePage />} />
			<Route path="/edplan-nexus/pathcrafter" element={<PathCrafterPage />} />
			<Route path="/edplan-nexus/schedulepilot" element={<SchedulePilotPage />} />
			<Route path="/edplan-nexus/universityadvisor" element={<UniversityAdvisorPage />} />
			<Route path="/edplan-nexus/financeguide" element={<FinanceGuidePage />} />
			<Route path="/edplan-nexus/careernavigator" element={<CareerNavigatorPage />} />
			<Route path="/edplan-nexus/academicsuccess" element={<AcademicSuccessPage />} />
			<Route path="/uni" element={<FindUniversityPage />} />
			<Route path="/compare" element={<CollegeComparePage />} />
			<Route path="/college/:unitId" element={<CollegeDetailPage />} />
		</Route>
		<Route path="/login" element={<LoginPage />} />
		<Route path="/signup" element={<SignupPage />} />
		<Route path="*" element={<Navigate to="/home" replace />} />
	</Routes>
);

export default App;
