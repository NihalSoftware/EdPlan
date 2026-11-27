import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { LuArrowRight, LuBookOpen, LuBuilding2, LuCompass, LuGitCompareArrows, LuMapPin,
  LuMessageCircle, LuPanelLeft, LuPlus, LuSend, LuSettings2, LuSquare, LuWallet, LuX } from "react-icons/lu";
import MesaReply, { MesaTable } from "../components/mesa/MesaReply.jsx";
import { load } from "../utils/storage.js";
import { confirmMesaAction, createConversation, deleteConversation, listScenarios,
  openConversation, recentConversations, sendMesaTurn, updateContext, updateHistory } from "../services/mesaService.js";
import "./mesa.css";

const topics = [
  ["Career Discovery", "Explore Career Paths", "Find work that fits your interests.", "Help me explore career paths", LuCompass],
  ["Find Colleges", "Discover Colleges & Programs", "Search New Mexico’s college catalog.", "Find New Mexico colleges and programs", LuBuilding2],
  ["Compare Programs", "Compare My Options", "Look at costs, credits, and outcomes.", "Compare colleges and programs", LuGitCompareArrows],
  ["Education Planning", "Build My Education Plan", "Start with the courses in your program.", "Help me build an education plan", LuBookOpen],
  ["Jobs & Employers", "Explore Local Employers", "See what sources can tell you about local work.", "Show me local employers", LuMapPin],
  ["What If Simulations", "Try a What-If Scenario", "See how a different credit load could change your plan.", "What if I take 12 credits instead of 15?", LuSettings2],
  ["Tuition & Financial Aid", null, null, "Help me understand tuition and financial aid", LuWallet],
];
const starters = ["What is a credit hour?", "Which New Mexico colleges offer nursing?", "How much could college cost?"];
const fields = [["subject", "Subject"], ["campus", "College or campus"], ["city", "City or ZIP"],
  ["education_stage", "Education stage"], ["budget_annual", "Annual budget ($)"],
  ["credits_per_term", "Credits per term"], ["max_drive_minutes", "Maximum drive time (minutes)"]];
const limits = { budget_annual: [0, 1000000], credits_per_term: [1, 40], max_drive_minutes: [1, 600] };

function ContextForm({ context, onSave, busy }) {
  const [draft, setDraft] = useState(context);
  const change = (name, value) => setDraft((previous) => ({ ...previous,
    [name]: value === "" ? null : limits[name] ? Number(value) : value }));
  const select = (name, label, choices) => <label>{label}
    <select value={draft[name] ?? ""} onChange={(event) => change(name, event.target.value)}>
      <option value="">Unspecified</option>{choices.map(([value, name]) => <option key={value} value={value}>{name}</option>)}
    </select>
  </label>;
  return <form className="mesa-context-form" onSubmit={(event) => {
    event.preventDefault();
    const editable = [...fields.map(([key]) => key), "credential", "tuition_category", "budget_basis", "online_only", "public_only", "sort_by"];
    const changes = Object.fromEntries(editable.filter((key) => draft[key] !== context[key]).map((key) => [key, draft[key]]));
    if (Object.keys(changes).length) onSave(changes);
  }}>
    <p>These preferences apply to this conversation.</p>
    {fields.map(([name, label]) => <label key={name}>{label}<input value={draft[name] ?? ""}
      type={limits[name] ? "number" : "text"} min={limits[name]?.[0]} max={limits[name]?.[1]} maxLength={120}
      onChange={(event) => change(name, event.target.value)} /></label>)}
    {select("credential", "Credential", ["certificate", "associate", "bachelor", "master", "doctorate"].map((x) => [x, x]))}
    {select("tuition_category", "Self-reported tuition category", [["resident", "In-state"], ["nonresident", "Out-of-state"], ["international", "International"]])}
    {select("budget_basis", "Annual budget covers", [["tuition", "Published tuition"], ["attendance", "Cost of attendance"]])}
    {select("sort_by", "Comparison priority", [["tuition", "Published tuition"], ["graduation_rate", "Institution graduation rate"], ["credits", "Program credits"]])}
    <label className="mesa-check"><input type="checkbox" checked={Boolean(draft.online_only)} onChange={(e) => setDraft((old) => ({...old, online_only: e.target.checked || null}))} /> Only online programs</label>
    <label className="mesa-check"><input type="checkbox" checked={Boolean(draft.public_only)} onChange={(e) => setDraft((old) => ({...old, public_only: e.target.checked || null}))} /> Only verified public colleges</label>
    {context.scenario && <div className="mesa-clarification">Active What-If assumptions: {Object.entries(context.scenario).filter(([,v]) => v != null)
      .map(([key, value]) => `${key.replaceAll("_", " ")}: ${value}`).join(", ") || "Alternative scenario"}</div>}
    <button className="mesa-primary" disabled={busy}>Save conversation preferences</button>
  </form>;
}

const errorText = (error, fallback) => typeof error.response?.data?.detail === "string" && error.response.status < 500
  ? error.response.data.detail : fallback;

export default function MesaPage() {
  const signedIn = Boolean(load("AuthToken"));
  const [session, setSession] = useState(null);
  const [recent, setRecent] = useState([]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(null);
  const [retry, setRetry] = useState(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [action, setAction] = useState(null);
  const [scenarioList, setScenarioList] = useState(null);
  const [menu, setMenu] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showContext, setShowContext] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const request = useRef(null);
  const composer = useRef(null);
  const bottom = useRef(null);
  const dialog = useRef(null);
  const locked = busy || Boolean(pending);

  useEffect(() => {
    const title = document.title;
    document.title = "Mesa AI · EdPlan";
    const controller = new AbortController();
    if (signedIn) recentConversations(controller.signal).then(setRecent).catch(() => {});
    return () => {
      document.title = title;
      controller.abort();
      request.current?.abort();
    };
  }, [signedIn]);

  useEffect(() => {
    if (session?.turns.length || pending) bottom.current?.scrollIntoView({ block: "nearest" });
  }, [session?.turns.length, pending]);

  useEffect(() => {
    if (action || showDelete) dialog.current?.showModal();
  }, [action, showDelete]);

  const refreshRecent = () => {
    if (signedIn) recentConversations().then(setRecent).catch(() => {});
  };

  const send = async (item) => {
    if (request.current || busy) return;
    const controller = new AbortController();
    request.current = controller;
    setPending(item.label);
    setNotice("");
    setError("");
    setMenu(false);
    setRetry(null);
    try {
      const current = session || await createConversation(controller.signal);
      setSession(current);
      const turn = await sendMesaTurn(current, item.input, controller.signal);
      setSession({ ...current, context: turn.context, turns: [...current.turns, turn] });
      if (item.input.message) setDraft((value) => value.trim() === item.input.message ? "" : value);
      if (current.retain_history) refreshRecent();
    } catch (err) {
      if (controller.signal.aborted) {
        setNotice("Request stopped. Retry to recover the answer if the server finished it.");
        setRetry(item);
      } else {
        setError(errorText(err, "Mesa couldn’t finish this request. Try again."));
        if (err.response?.status !== 409) setRetry(item);
      }
    } finally {
      request.current = null;
      setPending(null);
    }
  };
  const ask = (message) => {
    if (!message.trim()) return;
    send({ label: message.trim(), input: { message: message.trim(), request_id: crypto.randomUUID() } });
  };
  const choose = (choice) => send({ label: choice.label, input: { choice_id: choice.id, request_id: crypto.randomUUID() } });
  const newConversation = () => {
    setSession(null); setDraft(""); setNotice(""); setError(""); setRetry(null);
    setMenu(false); setShowContext(false); setScenarioList(null);
    composer.current?.focus();
  };
  const withSession = async (callback) => {
    if (locked) return;
    setBusy(true); setError("");
    try { await callback(); }
    catch (err) { setError(errorText(err, "Mesa couldn’t update this conversation. Try again.")); }
    finally { setBusy(false); }
  };
  const open = (id) => withSession(async () => {
    const next = await openConversation({ id });
    setSession(next); setRetry(null); setDraft(""); setMenu(false); setShowContext(false);
    setNotice(""); setScenarioList(null);
  });
  const closeDialog = () => { setAction(null); setShowDelete(false); };
  const confirm = () => withSession(async () => {
    if (showDelete) {
      await deleteConversation(session);
      newConversation();
      refreshRecent();
      setNotice("Conversation deleted.");
    } else {
      await confirmMesaAction(session, action.id);
      setSession((current) => ({ ...current, turns: current.turns.map((turn) =>
        turn.answer.action?.id === action.id ? { ...turn, answer: { ...turn.answer, action: null } } : turn) }));
      setNotice("Scenario saved to this conversation.");
      setScenarioList(await listScenarios(session));
    }
    closeDialog();
  });
  const changeHistory = () => withSession(async () => {
    setSession(await updateHistory(session, !session.retain_history));
    refreshRecent();
  });
  const saveContext = (changes) => withSession(async () => {
    const updated = await updateContext(session, changes);
    setSession({ ...updated, guest_token: session.guest_token });
    setNotice("Conversation preferences updated.");
  });
  const turns = session?.turns || [];

  return <div className={sidebarCollapsed ? "mesa-shell mesa-sidebar-collapsed" : "mesa-shell"}>
    <aside id="mesa-conversations" className={`mesa-sidebar${menu ? " mesa-sidebar-open" : ""}`} aria-label="Mesa conversations">
      <div className="mesa-sidebar-title"><img src="/assets/mesa-avatar.svg" alt="" width="34" height="34" /><strong>Mesa AI</strong>
        <button type="button" className="mesa-close-menu" aria-label="Close conversations" onClick={() => setMenu(false)}><LuX /></button></div>
      <button type="button" className="mesa-new" disabled={locked} onClick={newConversation}><LuPlus aria-hidden="true" />New Conversation</button>
      <nav aria-label="Conversation topics">{topics.map(([name, , , question, Icon]) => <button type="button" key={name} disabled={locked} onClick={() => ask(question)}>
        <Icon aria-hidden="true" /><span>{name}</span>
      </button>)}</nav>
      <div className="mesa-history">
        <h2>Recent Conversations</h2>
        {signedIn && recent.length ? recent.map((entry) => <button type="button" key={entry.id} disabled={locked} onClick={() => open(entry.id)}>
          <LuMessageCircle aria-hidden="true" />{entry.title}</button>) : <p>{signedIn ? "Choose “Keep for 30 days” in a conversation to see it here." : "Sign in to keep conversations you want to revisit."}</p>}
        {!signedIn && <Link to="/login?next=%2Fmesa">Sign in <LuArrowRight aria-hidden="true" /></Link>}
      </div>
    </aside>

    <section className="mesa-workspace" aria-label="Mesa education and career guide">
      <header className="mesa-toolbar">
        <button type="button" className="mesa-menu" aria-controls="mesa-conversations" aria-expanded={menu} onClick={() => setMenu(!menu)}><LuPanelLeft aria-hidden="true" /> Conversations</button>
        <button type="button" className="mesa-desktop-menu" aria-controls="mesa-conversations"
          aria-expanded={!sidebarCollapsed} onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
          <LuPanelLeft aria-hidden="true" /> {sidebarCollapsed ? "Show conversations" : "Hide conversations"}
        </button>
        {session && <div className="mesa-tools">
          <button type="button" aria-expanded={showContext} onClick={() => setShowContext(!showContext)}><LuSettings2 aria-hidden="true" /> Preferences</button>
          <details className="mesa-session-menu"><summary>Conversation options</summary><div>
            {signedIn && <button type="button" disabled={locked} onClick={changeHistory}>{session.retain_history ? "Turn off conversation history" : "Keep for 30 days"}</button>}
            {signedIn && <button type="button" disabled={locked} onClick={() => withSession(async () => setScenarioList(await listScenarios(session)))}>View saved scenarios</button>}
            <button type="button" disabled={locked} onClick={() => setShowDelete(true)}>Delete conversation</button>
          </div></details>
        </div>}
      </header>
      {showContext && session && <details className="mesa-context" open>
        <summary>Conversation preferences</summary>
        <ContextForm key={JSON.stringify(session.context)} context={session.context} onSave={saveContext} busy={locked} />
      </details>}
      {scenarioList && <div className="mesa-scenarios">
        <div><h2>Saved What-If scenarios</h2><button type="button" onClick={() => setScenarioList(null)}>Close</button></div>
        {scenarioList.length ? scenarioList.map(({ id, comparison }) => <MesaTable key={id} table={comparison} />) : <p>No saved scenarios in this conversation.</p>}
      </div>}
      {!turns.length && !pending && <div className="mesa-welcome">
        <img src="/assets/mesa-avatar.svg" className="mesa-hero-avatar" alt="" width="76" height="76" />
        <h1>Meet Mesa — Your AI Education Guide</h1>
        <p className="mesa-tagline">Your future starts with a question.</p>
        <p className="mesa-intro">Hi! I’m Mesa, your AI education and career guide. Whether you’re exploring colleges, choosing a program, comparing costs, or planning your future, I’m here to help you every step of the way.</p>
        <h2>What would you like to explore today?</h2>
        <div className="mesa-starters">{topics.filter(([, title]) => title).map(([name, title, help, question, Icon]) =>
          <button key={name} type="button" disabled={locked} onClick={() => ask(question)}>
            <span className="mesa-starter-icon"><Icon aria-hidden="true" /></span>
            <span><strong>{title}</strong><small>{help}</small></span><LuArrowUpRightIcon />
          </button>)}</div>
        <div className="mesa-quick" aria-label="Example questions">{starters.map((question) =>
          <button key={question} type="button" disabled={locked} onClick={() => ask(question)}>{question}</button>)}</div>
      </div>}
      {(turns.length > 0 || pending) && <div className="mesa-messages" role="log" aria-label="Conversation" aria-live="polite">
        {turns.map((turn, index) => <article key={turn.id}>
          <p className="mesa-student-message">{turn.message}</p>
          <MesaReply answer={turn.answer} current={index === turns.length - 1 && !pending} busy={locked} onChoice={choose} onReview={setAction} />
        </article>)}
        {pending && <><p className="mesa-student-message">{pending}</p><p role="status" className="mesa-waiting">Mesa is preparing your answer…</p></>}
        <div ref={bottom} />
      </div>}
      <div className="mesa-compose-area">
        {notice && <p className="mesa-notice" role="status">{notice}</p>}
        {error && <p className="mesa-notice mesa-error" role="alert">{error}</p>}
        {retry && !locked && <button type="button" className="mesa-text-action" onClick={() => send(retry)}>Retry last question</button>}
        <form className="mesa-composer" onSubmit={(event) => { event.preventDefault(); ask(draft); }}>
          <textarea aria-label="Ask Mesa" ref={composer} placeholder="Ask Mesa anything about your education..." value={draft} rows={2} maxLength={2000} onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
                event.preventDefault(); if (!locked) ask(draft);
              }
            }} />
          {pending ? <button type="button" className="mesa-primary" aria-label="Stop waiting for answer" onClick={() => request.current?.abort()}><LuSquare /></button>
            : <button type="submit" className="mesa-primary" disabled={locked || !draft.trim()} aria-label="Send question"><LuSend /></button>}
        </form>
        <footer>Mesa provides educational guidance. Verify important academic, admission, and financial decisions with your college advisor.</footer>
      </div>
    </section>
    {(action || showDelete) && <dialog ref={dialog} className="mesa-dialog" aria-labelledby="mesa-dialog-title" onCancel={closeDialog}>
      <h2 id="mesa-dialog-title">{showDelete ? "Delete conversation?" : "Review What-If scenario"}</h2>
      <p>{showDelete ? "This will remove this chat and its saved scenarios." : action.description}</p>
      {action && <MesaTable table={action.preview} />}
      <div className="mesa-dialog-actions"><button type="button" disabled={busy} onClick={closeDialog}>Cancel</button>
        <button type="button" className="mesa-primary" disabled={busy} onClick={confirm}>{showDelete ? "Delete conversation" : "Confirm and save"}</button></div>
      {error && <p role="alert">{error}</p>}
    </dialog>}
  </div>;
}

function LuArrowUpRightIcon() {
  return <LuArrowRight className="mesa-starter-arrow" aria-hidden="true" />;
}
