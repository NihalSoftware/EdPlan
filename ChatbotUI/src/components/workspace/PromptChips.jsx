import {
	FaBriefcase,
	FaBuildingColumns,
	FaCalendarDays,
	FaGraduationCap,
	FaWandMagicSparkles,
} from "react-icons/fa6";
import { FaDollarSign } from "react-icons/fa";

const prompts = [
	{ text: "Create a 4-year academic plan", icon: FaGraduationCap },
	{ text: "Compare universities for Computer Science", icon: FaBuildingColumns },
	{ text: "Estimate education costs", icon: FaDollarSign },
	{ text: "Build my class schedule", icon: FaCalendarDays },
	{ text: "Find scholarships for me", icon: FaWandMagicSparkles },
	{ text: "Explore career opportunities", icon: FaBriefcase },
];

const PromptChips = ({ onSelect }) => (
	<div className="flex flex-wrap gap-2.5">
		{prompts.map(({ text, icon: Icon }) => (
			<button
				key={text}
				type="button"
				onClick={() => onSelect(text)}
				className="inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-white px-3.5 py-2 text-sm font-bold text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700 hover:shadow-md"
			>
				<Icon className="text-indigo-500" />
				{text}
			</button>
		))}
	</div>
);

export default PromptChips;
