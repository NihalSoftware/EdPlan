import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { LuArrowRight, LuChevronDown, LuMapPin } from "react-icons/lu";
import { load } from "../utils/storage.js";
import { homeActionUrl, NORTHERN_PLANNER_URL } from "../utils/homeNavigation.js";
import "./HomePage.css";

const DISCLAIMER = "edplanAI-29 helps students explore colleges, compare programs, save options, and organize their education plans across 29 campuses throughout New Mexico. We strive to keep information accurate and up to date, but academic requirements and costs may change. Please verify important details with the respective college or academic advisor before making academic decisions.";

const HomePage = () => {
  const [disclaimerOpen, setDisclaimerOpen] = useState(false);
  const authenticated = Boolean(load("AuthToken"));

  useEffect(() => {
    const previousTitle = document.title;
    document.title = "edplanAI-29 | Your New Mexico Education Plan";
    return () => { document.title = previousTitle; };
  }, []);

  return (
    <div className="edplan-home">
      <a className="home-skip-link" href="#home-content">Skip to content</a>
      <section id="home-content" className="home-landscape" tabIndex={-1} aria-label="Explore and plan your education">
        <div className="home-introduction">
          <h1>Your Future in New Mexico Starts Here</h1>
          <p>One platform to explore, compare, and plan your path through New Mexico higher education — built for students, advisors, and families.</p>
        </div>
        <section id="compare-colleges" className="home-comparison-card" aria-labelledby="compare-heading">
          <div className="home-comparison-intro">
            <div>
              <h2 id="compare-heading">Compare New Mexico's 29 Public Colleges</h2>
              <p>Compare real tuition, degrees, and job outcomes — side-by-side, not on 29 different websites.</p>
              <ul className="home-feature-badges" aria-label="College comparison features">
                <li>Tuition &amp; Costs</li><li>Programs &amp; Degrees</li><li>Outcomes &amp; Rankings</li>
              </ul>
            </div>
          </div>
          <Link className="home-primary-action" to={homeActionUrl(authenticated, "/compare")}>
            {authenticated ? "Start Comparing" : "Login to Compare"}<LuArrowRight aria-hidden="true" />
          </Link>
          <p className="home-account-prompt">{authenticated ? (
            <Link to="/uni">Explore colleges to add to your comparison</Link>
          ) : <>New to edplanAI? <Link to="/signup?next=%2Fcompare">Create free account</Link></>}</p>
        </section>
        <section id="college-planner" className="home-planner-section" aria-labelledby="planner-heading">
          <h2 id="planner-heading">Directly make your plan in a pre-chosen college</h2>
          <p className="home-planner-subtitle">Other colleges joining soon</p>
          <article className="home-planner-card" aria-labelledby="northern-heading">
            <span className="home-pin-icon" aria-hidden="true"><LuMapPin /></span>
            <div>
              <h3 id="northern-heading">Northern NM College Planner</h3>
              <p>Build a personalized path for Northern New Mexico students — career, transfer, financial aid, and course planning in one place.</p>
              <Link className="home-planner-action" to={homeActionUrl(authenticated, NORTHERN_PLANNER_URL)}>
                {authenticated ? "Open Planner" : "Login to Planner"}<LuArrowRight aria-hidden="true" />
              </Link>
              <p className="home-planner-note">Northern NM students start here</p>
            </div>
          </article>
        </section>
      </section>
      <footer id="home-about" className="home-footer">
        <p>Serving students across Northern New Mexico <span aria-hidden="true">•</span> Taos <span aria-hidden="true">•</span> Santa Fe <span aria-hidden="true">•</span> Española <span aria-hidden="true">•</span> Farmington <span aria-hidden="true">•</span> Los Alamos</p>
        <button className="home-disclaimer-toggle" type="button" aria-expanded={disclaimerOpen}
          aria-controls="home-disclaimer" onClick={() => setDisclaimerOpen(!disclaimerOpen)}>
          Disclaimer — {disclaimerOpen ? "Know Less" : "Know More"}
          <LuChevronDown aria-hidden="true" className={disclaimerOpen ? "is-expanded" : ""} />
        </button>
        <div id="home-disclaimer" className={`home-disclaimer${disclaimerOpen ? " is-expanded" : ""}`}
          aria-hidden={!disclaimerOpen}>
          <div><p>{DISCLAIMER}</p></div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
