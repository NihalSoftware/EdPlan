import { useState } from "react";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || `${window.location.origin}/api`;

const IntakeForm = () => {
    const navigate = useNavigate();
    const [satTaken, setSatTaken] = useState("no");
    const [actTaken, setActTaken] = useState("no");

    const satDisabled = satTaken !== "yes";
    const actDisabled = actTaken !== "yes";

    const handleSubmit = async (event) => {
        event.preventDefault();
        const formData = new FormData(event.target);
        const payload = {};
        for (const [key, value] of formData.entries()) {
            if (payload[key]) {
                payload[key] = Array.isArray(payload[key])
                    ? [...payload[key], value]
                    : [payload[key], value];
            } else {
                payload[key] = value;
            }
        }

        try {
            const response = await fetch(`${API_BASE_URL}/intake`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                const detail = await response.text();
                throw new Error(detail || "Save failed");
            }
            toast.success("Form saved successfully!");
            navigate("/uni");
        } catch (error) {
            console.error("Intake submit failed", error);
            toast.error(
                "Could not save form. Please try again. If this keeps happening, make sure the backend is running at /api/intake."
            );
        }
    };

    return (
        <section className="bg-slate-50 min-h-screen flex items-center justify-center py-10 px-4">
            <div className="w-full max-w-5xl bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-200 overflow-hidden">
                {/* Header */}
                <header className="px-6 sm:px-8 py-5 border-b border-slate-200 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div>
                        <h1 className="text-xl sm:text-2xl font-bold tracking-tight">
                            Tell us about yourself
                        </h1>
                        <p className="text-xs sm:text-sm text-slate-300 mt-1">
                            This helps us generate a highly personalized education plan for you.
                        </p>
                    </div>
                    <button
                        type="button"
                        className="whitespace-nowrap px-4 py-2 rounded-lg border border-slate-600 text-xs sm:text-sm font-medium text-white hover:bg-slate-700 transition-colors"
                        onClick={() => navigate("/uni")}
                    >
                        Skip for now
                    </button>
                </header>

                <form onSubmit={handleSubmit} className="px-6 sm:px-8 py-6 space-y-8">
                    
                    {/* --- Academic Performance --- */}
                    <section>
                        <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-2">
                            <h2 className="text-lg font-semibold text-slate-800">Academic Performance</h2>
                            <span className="text-xs font-semibold tracking-wide text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
                                REQUIRED
                            </span>
                        </div>
                        
                        <div className="grid gap-x-4 gap-y-4 md:grid-cols-12">
                            {/* Row 1 */}
                            <label className="md:col-span-6 flex flex-col gap-1 text-sm font-medium text-slate-700">
                                <span>High School Name <span className="text-red-500">*</span></span>
                                <input name="high_school_name" type="text" placeholder="e.g. Lincoln High School" required className="input-field" />
                            </label>
                            <label className="md:col-span-3 flex flex-col gap-1 text-sm font-medium text-slate-700">
                                <span>Graduation Year <span className="text-red-500">*</span></span>
                                <select name="graduation_year" required className="input-field bg-white">
                                    <option value="">Select</option>
                                    <option>2025</option><option>2026</option><option>2027</option><option>2028</option>
                                </select>
                            </label>
                            <label className="md:col-span-3 flex flex-col gap-1 text-sm font-medium text-slate-700">
                                <span>State <span className="text-red-500">*</span></span>
                                <input name="state" type="text" placeholder="e.g. CA / Outside US" required className="input-field" />
                            </label>

                            {/* Row 2 */}
                            <label className="md:col-span-3 flex flex-col gap-1 text-sm font-medium text-slate-700">
                                <span>Resident Status <span className="text-red-500">*</span></span>
                                <select name="resident_status" required className="input-field bg-white">
                                    <option value="">Select status</option>
                                    <option>In state</option><option>Out of state</option><option>International</option>
                                </select>
                            </label>
                            <label className="md:col-span-3 flex flex-col gap-1 text-sm font-medium text-slate-700">
                                <span>Student Type <span className="text-red-500">*</span></span>
                                <select name="student_type" required className="input-field bg-white">
                                    <option value="">Select</option>
                                    <option>First Generation</option><option>African-American</option><option>Hispanic</option><option>Low Income</option>
                                </select>
                            </label>
                            <label className="md:col-span-3 flex flex-col gap-1 text-sm font-medium text-slate-700">
                                <span>GPA (4 scale) <span className="text-red-500">*</span></span>
                                <input name="gpa" type="number" placeholder="e.g. 3.5" min="0" max="4" step="0.01" required className="input-field" />
                            </label>
                            <label className="md:col-span-3 flex flex-col gap-1 text-sm font-medium text-slate-700">
                                Class Rank
                                <select name="class_rank" className="input-field bg-white">
                                    <option value="">Not reported</option>
                                    <option>Top 5%</option><option>Top 10%</option><option>Top 25%</option><option>Top 50%</option>
                                </select>
                            </label>

                            {/* Row 3 - File Upload & Core Subjects */}
                            <label className="md:col-span-4 flex flex-col gap-1 text-sm font-medium text-slate-700">
                                <span>12th Grade Marksheet <span className="text-slate-400 font-normal text-xs">(Max 10MB)</span></span>
                                <input name="marksheet_12th" type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" className="input-field py-1.5" />
                            </label>
                            
                            <div className="md:col-span-8 bg-slate-50 p-3 rounded-lg border border-slate-200">
                                <p className="text-[13px] font-semibold text-slate-600 mb-2">Core Subject Grades <span className="font-normal text-slate-500">(A/B/C or %)</span> <span className="text-red-500">*</span></p>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                    {[{ name: "grade_english", label: "English" }, { name: "grade_math", label: "Math" }, { name: "grade_science", label: "Science" }, { name: "grade_social_studies", label: "Social St." }].map((field) => (
                                        <input key={field.name} name={field.name} type="text" placeholder={field.label} required className="input-field" />
                                    ))}
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* --- Standardized Tests --- */}
                    <section>
                        <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-2">
                            <h2 className="text-lg font-semibold text-slate-800">Standardized Tests</h2>
                            <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">Optional</span>
                        </div>
                        
                        {/* Side by side layout for SAT and ACT on Desktop */}
                        <div className="grid md:grid-cols-2 gap-6">
                            {/* SAT Box */}
                            <div className="rounded-xl border border-sky-200 bg-sky-50/30 p-4">
                                <div className="flex items-center justify-between mb-4 border-b border-sky-100 pb-3">
                                    <div className="flex items-center gap-2">
                                        <div className="h-6 w-6 rounded bg-sky-600 text-white flex items-center justify-center text-[10px] font-bold tracking-wider">SAT</div>
                                    </div>
                                    <div className="flex items-center gap-3 text-sm text-slate-700 font-medium">
                                        <label className="flex items-center gap-1 cursor-pointer">
                                            <input type="radio" name="sat_taken" value="no" checked={satTaken === "no"} onChange={() => setSatTaken("no")} className="h-4 w-4 text-sky-600" /> No
                                        </label>
                                        <label className="flex items-center gap-1 cursor-pointer">
                                            <input type="radio" name="sat_taken" value="yes" checked={satTaken === "yes"} onChange={() => setSatTaken("yes")} className="h-4 w-4 text-sky-600" /> Yes
                                        </label>
                                    </div>
                                </div>
                                <div className={`grid grid-cols-2 gap-3 transition-opacity ${satDisabled ? "opacity-40 pointer-events-none" : "opacity-100"}`}>
                                    <label className="flex flex-col gap-1 text-xs font-semibold text-slate-700">Total (1600)
                                        <input name="sat_total" type="number" min="0" max="1600" placeholder="e.g. 1400" disabled={satDisabled} className="input-field-sm focus:ring-sky-500 focus:border-sky-500" />
                                    </label>
                                    <label className="flex flex-col gap-1 text-xs font-semibold text-slate-700">Math (800)
                                        <input name="sat_math" type="number" min="0" max="800" placeholder="e.g. 700" disabled={satDisabled} className="input-field-sm focus:ring-sky-500 focus:border-sky-500" />
                                    </label>
                                    <label className="flex flex-col gap-1 text-xs font-semibold text-slate-700">Reading (800)
                                        <input name="sat_reading" type="number" min="0" max="800" placeholder="e.g. 700" disabled={satDisabled} className="input-field-sm focus:ring-sky-500 focus:border-sky-500" />
                                    </label>
                                    <label className="flex flex-col gap-1 text-xs font-semibold text-slate-700">Test Date
                                        <input name="sat_date" type="date" disabled={satDisabled} className="input-field-sm focus:ring-sky-500 focus:border-sky-500" />
                                    </label>
                                </div>
                            </div>

                            {/* ACT Box */}
                            <div className="rounded-xl border border-emerald-200 bg-emerald-50/30 p-4">
                                <div className="flex items-center justify-between mb-4 border-b border-emerald-100 pb-3">
                                    <div className="flex items-center gap-2">
                                        <div className="h-6 w-6 rounded bg-emerald-600 text-white flex items-center justify-center text-[10px] font-bold tracking-wider">ACT</div>
                                    </div>
                                    <div className="flex items-center gap-3 text-sm text-slate-700 font-medium">
                                        <label className="flex items-center gap-1 cursor-pointer">
                                            <input type="radio" name="act_taken" value="no" checked={actTaken === "no"} onChange={() => setActTaken("no")} className="h-4 w-4 text-emerald-600" /> No
                                        </label>
                                        <label className="flex items-center gap-1 cursor-pointer">
                                            <input type="radio" name="act_taken" value="yes" checked={actTaken === "yes"} onChange={() => setActTaken("yes")} className="h-4 w-4 text-emerald-600" /> Yes
                                        </label>
                                    </div>
                                </div>
                                <div className={`grid grid-cols-3 gap-3 transition-opacity ${actDisabled ? "opacity-40 pointer-events-none" : "opacity-100"}`}>
                                    <label className="flex flex-col gap-1 text-xs font-semibold text-slate-700">Comp. (36)
                                        <input name="act_composite" type="number" min="1" max="36" placeholder="30" disabled={actDisabled} className="input-field-sm focus:ring-emerald-500 focus:border-emerald-500" />
                                    </label>
                                    <label className="flex flex-col gap-1 text-xs font-semibold text-slate-700">English
                                        <input name="act_english" type="number" min="1" max="36" disabled={actDisabled} className="input-field-sm focus:ring-emerald-500 focus:border-emerald-500" />
                                    </label>
                                    <label className="flex flex-col gap-1 text-xs font-semibold text-slate-700">Math
                                        <input name="act_math" type="number" min="1" max="36" disabled={actDisabled} className="input-field-sm focus:ring-emerald-500 focus:border-emerald-500" />
                                    </label>
                                    <label className="flex flex-col gap-1 text-xs font-semibold text-slate-700">Reading
                                        <input name="act_reading" type="number" min="1" max="36" disabled={actDisabled} className="input-field-sm focus:ring-emerald-500 focus:border-emerald-500" />
                                    </label>
                                    <label className="flex flex-col gap-1 text-xs font-semibold text-slate-700">Science
                                        <input name="act_science" type="number" min="1" max="36" disabled={actDisabled} className="input-field-sm focus:ring-emerald-500 focus:border-emerald-500" />
                                    </label>
                                    <label className="flex flex-col gap-1 text-xs font-semibold text-slate-700">Date
                                        <input name="act_date" type="date" disabled={actDisabled} className="input-field-sm focus:ring-emerald-500 focus:border-emerald-500 px-1" />
                                    </label>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* --- Financial Readiness --- */}
                    <section>
                        <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
                            <h2 className="text-lg font-semibold text-slate-800">Financial Readiness</h2>
                        </div>
                        <p className="text-[13px] text-slate-500 mb-4">
                            Helps filter realistic college options based on US study and living costs.
                        </p>

                        <div className="grid md:grid-cols-2 gap-4 mb-5">
                            <label className="flex flex-col gap-1 text-sm font-medium text-slate-700">
                                <span>Estimated Total Budget <span className="text-slate-400 font-normal">(USD/year)</span> <span className="text-red-500">*</span></span>
                                <div className="relative">
                                    <span className="absolute inset-y-0 left-3 flex items-center text-slate-400">$</span>
                                    <input name="budget_total" type="number" min="0" required placeholder="35000" className="input-field pl-7" />
                                </div>
                            </label>
                            <label className="flex flex-col gap-1 text-sm font-medium text-slate-700">
                                <span>Max Tuition You Can Afford <span className="text-slate-400 font-normal">(USD/year)</span> <span className="text-red-500">*</span></span>
                                <div className="relative">
                                    <span className="absolute inset-y-0 left-3 flex items-center text-slate-400">$</span>
                                    <input name="max_tuition" type="number" min="0" required placeholder="22000" className="input-field pl-7" />
                                </div>
                            </label>
                        </div>

                        <div className="grid md:grid-cols-2 gap-6">
                            <div>
                                <p className="text-[13px] font-semibold text-slate-700 mb-2">Need financial aid/scholarships?</p>
                                <div className="flex flex-col gap-2">
                                    {[
                                        { value: "no_aid", label: "No, I can attend without aid" },
                                        { value: "some_aid", label: "Yes, I need some aid" },
                                        { value: "significant_aid", label: "Yes, I need significant aid" },
                                    ].map((opt) => (
                                        <label key={opt.value} className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
                                            <input type="radio" name="need_aid" value={opt.value} className="h-4 w-4 text-emerald-600 focus:ring-emerald-500" />
                                            <span>{opt.label}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                            
                            <div>
                                <p className="text-[13px] font-semibold text-slate-700 mb-2">Expected ways to pay (Select multiple)</p>
                                <div className="flex flex-wrap gap-2">
                                    {["Family savings", "Student loans", "Need-based aid", "Merit scholarships", "Sponsor", "Other"].map((label) => (
                                        <label key={label} className="inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-[13px] cursor-pointer hover:border-emerald-400 transition-colors">
                                            <input type="checkbox" name="pay_options" value={label} className="h-3.5 w-3.5 rounded text-emerald-600 focus:ring-emerald-500" />
                                            <span className="text-slate-700">{label}</span>
                                        </label>
                                    ))}
                                </div>
                                <div className="mt-4 flex items-center gap-3">
                                    <p className="text-[13px] font-semibold text-slate-700">Interested in on-campus work?</p>
                                    <label className="text-sm flex items-center gap-1 cursor-pointer"><input type="radio" name="work_study" value="yes" className="text-emerald-600" /> Yes</label>
                                    <label className="text-sm flex items-center gap-1 cursor-pointer"><input type="radio" name="work_study" value="no" className="text-emerald-600" /> No</label>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* --- Footer & Submit --- */}
                    <section className="border-t border-slate-200 pt-5 flex flex-col md:flex-row md:items-center justify-between gap-4 mt-2">
                        <label className="flex items-start gap-2 text-[13px] text-slate-600 max-w-2xl cursor-pointer">
                            <input name="consent" type="checkbox" required className="mt-0.5 h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 flex-shrink-0" />
                            <span>I confirm the information provided is accurate. EdPlan AI will use this to estimate fit and suggest US colleges.</span>
                        </label>

                        <div className="flex gap-3 shrink-0">
                            <button type="button" onClick={() => navigate("/uni")} className="px-5 py-2.5 rounded-lg border border-slate-300 text-sm font-medium text-slate-700 hover:bg-slate-100 transition-colors">
                                Skip For Now
                            </button>
                            <button type="submit" className="px-6 py-2.5 rounded-lg text-sm font-semibold text-white bg-slate-900 shadow-md hover:bg-slate-800 hover:shadow-lg transition-all">
                                Save Profile
                            </button>
                        </div>
                    </section>
                </form>
            </div>
            
            {/* Injecting basic standard styles for inputs so we don't repeat long tailwind classes */}
            <style>{`
                .input-field {
                    width: 100%;
                    border-radius: 0.5rem;
                    border: 1px solid #cbd5e1;
                    padding: 0.5rem 0.75rem;
                    font-size: 0.875rem;
                    outline: none;
                    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
                    transition: all 0.2s;
                }
                .input-field:focus {
                    border-color: #10b981;
                    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
                }
                .input-field-sm {
                    width: 100%;
                    border-radius: 0.375rem;
                    border: 1px solid #cbd5e1;
                    padding: 0.375rem 0.5rem;
                    font-size: 0.75rem;
                    outline: none;
                    background: white;
                }
            `}</style>
        </section>
    );
};

export default IntakeForm;