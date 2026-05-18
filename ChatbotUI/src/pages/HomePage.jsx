import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FiBookOpen, FiSearch, FiDollarSign, FiAward } from "react-icons/fi";
import { load } from "../utils/storage.js";

const HomePage = () => {
    const profile = load("UserProfile");
    const firstName =
        typeof profile?.first_name === "string"
            ? profile.first_name
            : typeof profile?.firstName === "string"
            ? profile.firstName
            : "";
    const navigate = useNavigate();
    const [selection, setSelection] = useState("");

    return (
        <section className="min-h-screen bg-[#F8FAFC] text-slate-900">
            <div className="mx-auto max-w-[1100px] px-6 py-10 lg:px-8">
                <div className="rounded-[28px] border border-[#E2E8F0] bg-white p-8 shadow-sm shadow-slate-200/50">
                    <div className="mx-auto max-w-3xl text-center">
                        <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 text-blue-600 shadow-sm">
                            <FiBookOpen className="h-7 w-7" />
                        </div>
                        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">Education planning</p>
                        <h1 className="mt-6 text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
                            Find Your Perfect <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">College</span>
                        </h1>
                        <p className="mt-4 text-xl font-semibold text-slate-800">Plan Your Educational Journey.</p>
                        <p className="mx-auto mt-5 max-w-2xl text-base leading-8 text-slate-600">
                            Explore colleges, compare academic programs, and build a personalized education plan to make informed decisions about your future.
                        </p>
                    </div>

                    <div className="mt-12 grid gap-8">
                        <div className="w-full">
                            <div className="rounded-[28px] border border-[#E2E8F0] bg-white p-5 shadow-sm">
                                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Welcome back</p>
                                <h3 className="mt-3 text-xl font-semibold text-slate-950">{firstName ? `Welcome back, ${firstName} 👋` : "Welcome back 👋"}</h3>
                                <p className="mt-2 text-sm leading-6 text-slate-600">Let's continue building your education plan.</p>
                                <div className="mt-5 rounded-[24px] bg-slate-50 p-4 text-sm text-slate-700">
                                    <p className="font-semibold text-slate-900">Today’s focus</p>
                                    <p className="mt-2 leading-6 text-slate-600">Answer the question above to unlock tailored recommendations and college tools.</p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <div className="rounded-[28px] border border-[#E2E8F0] bg-white p-8 shadow-[0_30px_80px_-40px_rgba(15,23,42,0.18)]">
                                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-50 text-blue-600 shadow-sm mb-6">
                                    <FiBookOpen className="h-7 w-7" />
                                </div>
                                <h2 className="text-2xl font-semibold text-slate-950">Have You Already Chosen a College?</h2>
                                <p className="mt-3 text-sm leading-7 text-slate-600">Your answer helps us personalize your recommendations.</p>

                                <div className="mt-8 grid gap-4 sm:grid-cols-2">
                                    <button
                                        type="button"
                                        onClick={() => setSelection("yes")}
                                        className={`rounded-2xl border px-5 py-4 text-left text-sm font-semibold transition ${
                                            selection === "yes"
                                                ? "border-blue-600 bg-blue-50 text-blue-800 shadow-sm"
                                                : "border-[#E2E8F0] bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50"
                                        }`}
                                    >
                                        Yes, I Have
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setSelection("notYet")}
                                        className={`rounded-2xl border px-5 py-4 text-left text-sm font-semibold transition ${
                                            selection === "notYet"
                                                ? "border-blue-600 bg-blue-50 text-blue-800 shadow-sm"
                                                : "border-[#E2E8F0] bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50"
                                        }`}
                                    >
                                        Not Yet
                                    </button>
                                </div>

                                <button
                                    type="button"
                                    onClick={() => navigate("/uni")}
                                    className="mt-8 w-full rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 text-base font-semibold text-white shadow-[0_18px_45px_-18px_rgba(59,130,246,0.8)] transition hover:shadow-[0_20px_60px_-20px_rgba(59,130,246,0.85)] hover:from-blue-700 hover:to-purple-700"
                                >
                                    Continue
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="mt-10 grid gap-6 md:grid-cols-3">
                        <div
                            role="button"
                            tabIndex={0}
                            onClick={() => navigate("/uni")}
                            onKeyDown={(event) => {
                                if (event.key === "Enter" || event.key === " ") {
                                    event.preventDefault();
                                    navigate("/uni");
                                }
                            }}
                            className="cursor-pointer rounded-[24px] border border-[#E2E8F0] bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                                <FiSearch className="h-6 w-6" />
                            </div>
                            <h4 className="mt-5 text-lg font-semibold text-slate-950">Find University</h4>
                            <p className="mt-3 text-sm leading-6 text-slate-600">Search and compare colleges by tuition, rankings, and academic programs.</p>
                        </div>

                        <div
                            role="button"
                            tabIndex={0}
                            onClick={() => navigate("/intake")}
                            onKeyDown={(event) => {
                                if (event.key === "Enter" || event.key === " ") {
                                    event.preventDefault();
                                    navigate("/intake");
                                }
                            }}
                            className="cursor-pointer rounded-[24px] border border-[#E2E8F0] bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                                <FiDollarSign className="h-6 w-6" />
                            </div>
                            <h4 className="mt-5 text-lg font-semibold text-slate-950">Estimate Costs</h4>
                            <p className="mt-3 text-sm leading-6 text-slate-600">Calculate tuition, housing, and other college expenses.</p>
                        </div>

                        <div
                            role="button"
                            tabIndex={0}
                            onClick={() => navigate("/scholarships")}
                            onKeyDown={(event) => {
                                if (event.key === "Enter" || event.key === " ") {
                                    event.preventDefault();
                                    navigate("/scholarships");
                                }
                            }}
                            className="cursor-pointer rounded-[24px] border border-[#E2E8F0] bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                                <FiAward className="h-6 w-6" />
                            </div>
                            <h4 className="mt-5 text-lg font-semibold text-slate-950">Explore Scholarships</h4>
                            <p className="mt-3 text-sm leading-6 text-slate-600">Discover scholarships, grants, and financial aid opportunities.</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default HomePage;
