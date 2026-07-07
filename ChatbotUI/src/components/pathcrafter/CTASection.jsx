import { useNavigate } from "react-router-dom";
import { FaRocket } from "react-icons/fa6";
import { INITIAL_PATHCRAFTER_PROMPT } from "./PathCrafterHero.jsx";

const CTASection = () => {
	const navigate = useNavigate();

	return (
		<section className="rounded-[2rem] border border-indigo-200 bg-gradient-to-br from-indigo-600 to-violet-700 p-8 text-white shadow-2xl shadow-indigo-200 lg:p-10">
			<div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
				<div>
					<h2 className="text-3xl font-black tracking-tight">
						Ready to Build Your Academic Journey?
					</h2>
					<p className="mt-3 max-w-3xl text-sm font-semibold leading-7 text-indigo-50 md:text-base">
						Let PathCrafter generate a personalized academic plan and guide every
						semester with clearer requirements, smarter sequencing, and confident next steps.
					</p>
				</div>
				<button
					type="button"
					onClick={() =>
						navigate("/edplan-nexus/workspace", {
							state: {
								initialPrompt: INITIAL_PATHCRAFTER_PROMPT,
								sourceAgent: "PathCrafter",
							},
						})
					}
					className="inline-flex items-center justify-center gap-3 rounded-xl bg-white px-7 py-4 text-sm font-black text-indigo-700 shadow-xl transition hover:-translate-y-0.5 hover:shadow-2xl"
				>
					<FaRocket />
					Launch PathCrafter
				</button>
			</div>
		</section>
	);
};

export default CTASection;
