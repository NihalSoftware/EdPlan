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
import LoginPage from "./pages/LoginPage.jsx";
import SignupPage from "./pages/SignupPage.jsx";
import IntakeForm from "./pages/IntakeForm.jsx";
import RecommendationPage from "./pages/RecommendationPage.jsx";

const App = () => (
	<Routes>
		<Route element={<AppLayout />}>
			<Route path="/" element={<Navigate to="/home" replace />} />
			<Route path="/home" element={<HomePage />} />
			<Route path="/intake" element={<IntakeForm />} />
			<Route path="/chatbot" element={<ChatbotPage />} />
			<Route path="/educationplan" element={<EducationPlanEditPage />} />
			<Route path="/career" element={<CareerProgramPage />} />
			<Route path="/view" element={<ViewEducationPlanPage />} />
			<Route path="/uni" element={<FindUniversityPage />} />
			<Route path="/compare" element={<CollegeComparePage />} />
			<Route path="/college/:unitId" element={<CollegeDetailPage />} />
			<Route path="/recommendations" element={<RecommendationPage />} />
		</Route>
		<Route path="/login" element={<LoginPage />} />
		<Route path="/signup" element={<SignupPage />} />
		<Route path="*" element={<Navigate to="/home" replace />} />
	</Routes>
);

export default App;
