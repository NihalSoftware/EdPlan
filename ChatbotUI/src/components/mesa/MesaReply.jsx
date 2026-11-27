import { Link } from "react-router-dom";
import { LuArrowUpRight, LuExternalLink } from "react-icons/lu";

export function MesaTable({ table }) {
  return <div className="mesa-table-scroll" tabIndex={0} role="region" aria-label={table.title}>
    <table className="mesa-table">
      <caption>{table.title}</caption>
      <thead><tr>{table.columns.map((column) => <th scope="col" key={column}>{column}</th>)}</tr></thead>
      <tbody>{table.rows.map((row, index) => <tr key={index}>
        {row.map((value, cell) => <td key={cell}>{value ?? "Unavailable"}</td>)}
      </tr>)}</tbody>
    </table>
  </div>;
}

const safeSource = (value) => {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password ? url.href : null;
  } catch {
    return null;
  }
};

function MarkdownText({ value }) {
  // A deliberately small Markdown subset. React renders every segment as text.
  const inline = (line) => line.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((segment, index) =>
    segment.startsWith("**") && segment.endsWith("**") ? <strong key={index}>{segment.slice(2, -2)}</strong>
      : segment.startsWith("`") && segment.endsWith("`") ? <code key={index}>{segment.slice(1, -1)}</code> : segment);
  return value.split(/\n\n+/).map((paragraph, index) => {
    const lines = paragraph.split("\n");
    const listStart = lines.findIndex((line) => /^\s*(?:[-*]|\d+\.) /.test(line));
    if (listStart === -1) return <p key={index}>{inline(lines.join(" "))}</p>;
    const intro = lines.slice(0, listStart).join(" ");
    const List = /^\s*\d+\./.test(lines[listStart]) ? "ol" : "ul";
    return <div key={index}>{intro && <p>{inline(intro)}</p>}<List>{lines.slice(listStart).map((line, item) =>
      <li key={item}>{inline(line.replace(/^\s*(?:[-*]|\d+\.) /, ""))}</li>)}</List></div>;
  });
}

export default function MesaReply({ answer, current, busy, onChoice, onReview }) {
  const displaySuggestions = current && answer.suggestions.length > 0;
  const destination = /^\/(?:educationplan|schedule-generator|view|compare|uni|career|financial-aid|intake|login)(?:\?[^\s]*)?$/.test(answer.link || "") ? answer.link : null;
  return <div className="mesa-reply">
    <img src="/assets/mesa-avatar.svg" alt="" width="38" height="38" />
    <div className="mesa-reply-body">
      <strong className="mesa-reply-name">Mesa</strong>
      <div className="mesa-prose"><MarkdownText value={answer.text} /></div>
      {answer.tables.filter((table) => table.rows.length).map((table) => <MesaTable key={table.title} table={table} />)}
      {answer.sources.length > 0 && <ul className="mesa-sources" aria-label="Sources">
        {answer.sources.map(({ title, url, observed }) => {
          const href = safeSource(url);
          return <li key={`${title}-${url}`}>{href
            ? <a href={href} target="_blank" rel="noopener noreferrer">{title}<LuExternalLink aria-hidden="true" /></a>
            : title}{observed && <span> · {observed}</span>}</li>;
        })}
      </ul>}
      {destination && <Link className="mesa-resource-link" to={destination}>{answer.link_label || "Open resource"} <LuArrowUpRight aria-hidden="true" /></Link>}
      {answer.clarification && <div className="mesa-clarification">{answer.clarification}</div>}
      {current && answer.choices.length > 0 && <ol className="mesa-result-choices" aria-label="Choices for this reply">
        {answer.choices.map((choice) => <li key={choice.id}>
          <button type="button" onClick={() => onChoice(choice)} disabled={busy}>{choice.label}</button>
        </li>)}
      </ol>}
      {current && answer.action && <button type="button" className="mesa-text-action" disabled={busy} onClick={() => onReview(answer.action)}>Review and save scenario</button>}
      {displaySuggestions && <section className="mesa-suggestion-list" aria-label="Suggested next questions">
        <p>You might also want to ask:</p>
        <div>{answer.suggestions.map((choice) => <button key={choice.id} type="button" disabled={busy} onClick={() => onChoice(choice)}>{choice.label} <LuArrowUpRight aria-hidden="true" /></button>)}</div>
        {answer.follow_more.length > 0 && <details><summary>Show more</summary><div>
          {answer.follow_more.map((choice) => <button key={choice.id} type="button" disabled={busy} onClick={() => onChoice(choice)}>{choice.label}</button>)}
        </div></details>}
      </section>}
    </div>
  </div>;
}
