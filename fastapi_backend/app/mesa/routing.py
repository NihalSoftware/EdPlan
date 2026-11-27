"""Deterministic routing, explicit context edits, and the curated suggestion graph."""

import json
import re
import unicodedata
from pathlib import Path
from uuid import uuid4

from app.mesa.schemas import Choice, Scenario

SPEC = {item["id"]: item for item in json.loads(
    Path(__file__).with_name("intent_spec.json").read_text(encoding="utf-8-sig")
)}

# Order matters: safety and specific actions precede broader discovery terms.
RULES = [
    ("M38", r"suicid|self.harm|kill myself|crisis|immediate danger|should i quit|give up|sensitive"),
    ("M36", r"\bactually\b|\bcorrection\b|\breturn to my actual\b|\bi meant\b|\bchange my\b|make my budget"),
    ("M21", r"advisor (?:review|share)|(?:send|share).*(?:plan|advisor)|saved plans?|download.*pdf|save (?:this|my).*plan|prepare.*advisor"),
    ("M35", r"\b(?:what is|what's|define|meaning of|explain) (?:a |the )?(?:credit.hour|net price|gpa|corequisite|prerequisite|transfer equivalency|retention|cost of attendance)|data (?:quality|source)|how does mesa use"),
    ("M25", r"hiring|vacanc|job postings|job openings|\binternships?\b"),
    ("M26", r"(?:which|what).*degree.*(?:employer|work at|these roles)|(?:employers?).*degrees?"),
    ("M24", r"(?:employer|hospital|facilit).*(?:campus|college|new mexico tech|northern|unm|nmsu)|(?:campus|college).*employer"),
    ("M23", r"employers?|local workplaces|where could.*work near"),
    ("M28", r"fail(?:ed|ing)?(?: a)? (?:class|course|chemistry|math)|retake|repeat a course"),
    ("M29", r"what if.*(?:switch|change my major|transfer|choose.*(?:instead|degree))|switch (?:college|program|major)"),
    ("M30", r"what if.*(?:tuition|lived|live|scholarship|funding|afford)|if i(?:'m| am| were) from|scholarship.*ends|\blive at home\b"),
    ("M31", r"(?:raise|improve|change|estimated|predict|affect|calculate).*gpa|(?:grades?|gpa).*what if"),
    ("M32", r"work.*(?:hours|evenings|schedule)|schedule.*(?:job|work|commute)|commute.*work"),
    ("M33", r"(?:what if|instead).*(?:career|earnings|salary)|compare.*(?:lifetime|earnings paths)"),
    ("M34", r"optim[izs]|best scenario|compare scenarios|fastest.*cheapest|lowest cost.*graduate"),
    ("M27", r"\bwhat if\b.*(?:credit|summer|graduate|graduation|part.time|semester)|\b(?:take|at|with) \d+ credits\b|(?:finish|graduate).*(?:summer|credits per|faster)"),
    ("M20", r"\btransfe(?:r|rring)\b|articulation|equivalen"),
    ("M19", r"transcript|placement|ap credits?|completed courses|prior credit|dual credit|credits? i (?:have|earned)"),
    ("M17", r"prerequi|corequi|course order|take.*before|minimum grade"),
    ("M18", r"schedule|course offerings|class (?:times?|sections?)|available.*fall"),
    ("M22", r"academic progress|graduation audit|remaining credits|on track|tutoring|falling behind|study support"),
    ("M16", r"(?:create|build|draft|make|start|sample).*(?:education plan|course plan|semester|adn plan)|plan my courses"),
    ("M12", r"financial aid|scholarship|fafsa|pell grant|work.study|grant eligibility"),
    ("M13", r"salary|\broi\b|pay after|what.*earn|wages|return on investment|career outcomes"),
    ("M10", r"(?:compare|rank).*(?:program|adn|bsn|tuition|deadline|distance|commute)|under \$|within .*(?:hour|minutes)|cost.*top priority"),
    ("M09", r"\bcompar(?:e|ison)\b|versus|\bvs\b"),
    ("M11", r"tuition|cost per credit|annual cost|how much.*(?:fees|cost)|out.of.state|international.*fees|budget|cost of attendance"),
    ("M14", r"acceptance rate|graduation rate|retention rate|admissions metrics|completion rate"),
    ("M07", r"can i (?:apply|get in)|admission|application deadline|eligible.*apply|entry requirements"),
    ("M15", r"accessib|disabilit|childcare|commut|flexib|evening|lifestyle"),
    ("M08", r"\bcampus (?:life|facts|support)\b|college facts|housing|student services|campus size|student housing"),
    ("M02", r"\bged\b|high.school (?:senior|student)|my profile|my information|returning (?:to school|learner)|remember my|i am an international student|i'm studying part time"),
    ("M06", r"(?:which|best|suit).*(?:degree|program|credential).*fit|right for me|good fit|which pathway"),
    ("M05", r"\b(?:adn|bsn|rn programs?)\b|(?:find|show|offer|study|teach).*(?:program|bachelor|welding|computer science|nursing|psychology)|how many credit hours"),
    ("M03", r"\bcareer|\bjob\b|become a nurse|i like |i enjoy |work in |what should i study"),
    ("M04", r"\b(?:find|show|list|public|which).*\b(?:colleges?|universities|campuses)\b"),
    ("M01", r"\bmesa\b|where to start|help me choose|what can you do|create a plan|^hello[!.]?$|^hi[!.]?$"),
]

STARTERS = {
    "M03": "Explore career paths", "M05": "Discover colleges and programs",
    "M09": "Compare my options", "M16": "Build my education plan",
    "M23": "Explore local employers", "M27": "Try a What-If scenario",
    "M04": "Find New Mexico colleges", "M11": "Compare tuition and costs",
}


def simplify(message):
    return unicodedata.normalize("NFKC", message).lower().replace("’", "'").strip()


# Support the authored example questions alongside rules for unfamiliar phrasing.
EXAMPLE_INTENTS = {
    simplify(question).rstrip(".?!"): intent
    for intent, item in SPEC.items()
    for question in item["utterances"]
}


def route(message, previous=None, *, authored_examples=True):
    text = simplify(message)
    if re.search(RULES[0][1], text):
        return "M38"
    if "international student" in text and re.search(r"\b(?:cost|tuition|fees)\b", text):
        return "M11"
    if previous in {"M27", "M34"} and re.search(
        r"\b(?:credits (?:left|remaining)|remaining credits|per (?:term|semester)|summer classes|use my saved.*plan)\b", text
    ):
        return previous
    if previous in {"M04", "M05", "M09", "M10", "M11"} and re.search(
        r"^(?:only show|also (?:keep|limit)|(?:published )?tuition only|(?:full|total) annual cost|in.state|out.of.state|nonresident|resident)\b", text
    ):
        return previous
    if previous in {"M17", "M18"} and re.search(r"\b(?:cannot be moved|in its place|same for .* nursing)\b", text):
        return previous
    if previous in {"M19", "M20"} and re.search(r"^i want a .* degree in\b", text):
        return previous
    if previous == "M21" and re.search(r"\bpreview (?:it|the plan)\b", text):
        return previous
    if authored_examples and (intent := EXAMPLE_INTENTS.get(text.rstrip(".?!"))):
        return intent
    if re.search(r"\b(?:show|find|list)\b.*\b(?:associate|bachelor|master)(?:'s)? degrees\b", text):
        return "M05"
    if re.search(r"\b(?:what if|instead)\b.*\b(?:california|scholarship)\b", text):
        return "M30"
    if re.search(r"\bwhat if\b.*\b(?:choose|pick)\b.*\binstead\b", text):
        return "M29"
    if re.search(r"\b(?:move|replace)\s+[a-z]{2,6}\s*\d{3,4}\b|\b(?:why|what|finish|complete).*\bprerequisites?\b", text):
        return "M17"
    if re.search(r"\b(?:student.status categories|what is my tuition|credit.hour.*cost|cost per credit|can i afford)\b", text):
        return "M11"
    if re.search(r"\b(?:give me|list|find).*colleges.*\b(?:rn|nursing) programs\b", text):
        return "M05"
    if re.search(r"\b(?:i have|i passed|i earned|already have).*\bged\b", text):
        return "M02"
    if re.search(r"^(?:only show|only|just) (?:bachelor|associate|master|certificate)", text):
        return previous if previous in {"M04", "M05", "M09", "M10"} else "M05"
    if re.search(r"\bcredit hour\b", text) and re.search(r"\b(?:what (?:is|are)|degree for|mean)\b", text):
        return "M35"
    for intent, pattern in RULES:
        if re.search(pattern, text):
            return intent
    return "M37"


SUBJECTS = {
    "nursing": r"\bnurs\w*\b|\b(?:adn|bsn|rn)\b",
    "computer science": r"computer science|software engineer",
    "engineering": r"\bengineering\b|\bengineer\b",
    "welding": r"\bweld\w*\b",
    "biology": r"\bbiolog\w*\b",
    "psychology": r"\bpsycholog\w*\b",
    "teacher education": r"teacher education|teaching|become a teacher",
    "business": r"\bbusiness\b|accounting",
    "automotive": r"automotive|car repair|vehicle repair",
    "cybersecurity": r"cybersecurity|cyber security",
    "healthcare": r"health ?care|helping people",
}

CAMPUS_ALIASES = {
    "Northern New Mexico College": r"\b(?:northern(?: new mexico college)?|nnmc)\b",
    "University of New Mexico": r"\b(?:unm|university of new mexico)\b",
    "New Mexico State University": r"\b(?:nmsu|new mexico state university)\b",
    "New Mexico Tech": r"\b(?:new mexico tech|nmt)\b",
    "Santa Fe Community College": r"\b(?:sfcc|santa fe community college)\b",
    "Central New Mexico Community College": r"\b(?:cnm|central new mexico community college)\b",
}
TWO_CREDENTIALS = re.compile(r"\b(?:adn|associate\w*)\b.*\b(?:bsn|bachelor\w*)\b|\b(?:bsn|bachelor\w*)\b.*\b(?:adn|associate\w*)\b")


def edits(message, context, intent):
    """Merge only explicitly stated preferences. Hypotheses have their own slots."""
    text = simplify(message)
    if re.search(r"return to (?:my )?actual|reset (?:my |the )?scenario|return to (?:the )?original", text):
        return context.model_copy(update={"scenario": None})
    update = {}
    for subject, pattern in SUBJECTS.items():
        if re.search(pattern, text):
            update["subject"] = subject
            break
    if not TWO_CREDENTIALS.search(text):
        for degree, pattern in {
            "associate": r"\b(?:adn|associates?)\b", "bachelor": r"\b(?:bsn|bachelor\w*)\b",
            "certificate": r"\bcertificate\b", "master": r"\bmaster\w*\b", "doctorate": r"\b(?:doctorate|phd)\b",
        }.items():
            if re.search(pattern, text):
                update["credential"] = degree
                break
    campuses = [name for name, pattern in CAMPUS_ALIASES.items() if re.search(pattern, text)]
    if len(campuses) == 1 and not (intent == "M20" and re.search(r"\b(?:from|at)\b", text) and "sfcc" in text):
        update["campus"] = campuses[0]
    if len(campuses) > 1:
        update["campus"] = None
    if re.search(r"\b(?:i have|i've|passed|earned|already).*\bged\b", text):
        update["education_stage"] = "GED"
    elif re.search(r"\bi(?:'m| am) (?:a )?high.school", text):
        update["education_stage"] = "High school"
    elif re.search(r"\bi(?:'m| am) returning", text):
        update["education_stage"] = "Returning student"
    if re.search(r"\bi(?:'m| am) (?:an )?international student\b", text):
        update["tuition_category"] = "international"
    elif re.search(r"\b(?:i(?:'m| am)|if i were) (?:a |an )?(?:nonresident|out.of.state)\b|if i(?:'m| am| were) from california|(?:what if.*)lived in california", text):
        update["tuition_category"] = "nonresident"
    elif re.search(r"^(?:out.of.state|nonresident)\b", text):
        update["tuition_category"] = "nonresident"
    elif re.search(r"^(?:in.state|resident)\b|\bi(?:'m| am) (?:a |an )?(?:new mexico resident|in.state student)\b", text):
        update["tuition_category"] = "resident"
    budget = re.search(r"(?:budget[^$\d]{0,22}|under\s*|afford\s*(?:college with)?\s*(?:an? )?)\$([\d,]{1,9})", text)
    if re.search(r"\b(?:tuition only|published tuition|tuition (?:budget|under))\b", text):
        update["budget_basis"] = "tuition"
    elif re.search(r"\b(?:total annual cost|full annual cost|cost of attendance|total cost)\b", text):
        update["budget_basis"] = "attendance"
    if budget:
        update["budget_annual"] = min(int(budget[1].replace(",", "") or 0), 1_000_000)
    credits = re.search(r"\b(?:take|only|with|at|to)\s+(\d{1,2})\s+credits?\b", text)
    if credits and 1 <= int(credits[1]) <= 40:
        update["credits_per_term"] = int(credits[1])
    minutes = re.search(r"within\s+(?:a\s+)?(\d{1,3})(?:\s*-\s*|\s+)(minutes?|hours?)", text)
    if minutes:
        update["max_drive_minutes"] = min(600, max(1, int(minutes[1]) * (60 if minutes[2].startswith("hour") else 1)))
    elif re.search(r"within (?:one|an) hour", text):
        update["max_drive_minutes"] = 60
    for city in ("Santa Fe", "Albuquerque", "Española", "Espanola", "Las Cruces", "Socorro", "Farmington", "Taos", "Gallup", "Roswell"):
        if re.search(r"(?:\bnear|\bof|\bfrom|\blive in)\s+" + city.lower() + r"\b", text):
            update["city"] = city
            break
    if re.search(r"\bpublic (?:new mexico )?(?:colleges|universities|institutions)\b", text):
        update["public_only"] = True
    if re.search(r"online (?:only|programs?)|only online", text):
        update["online_only"] = True
    if re.search(r"(?:sort|rank|priority|cheapest|lowest).*(?:tuition|cost)|cheapest", text):
        update["sort_by"] = "tuition"
    elif re.search(r"(?:sort|rank).*graduation", text):
        update["sort_by"] = "graduation_rate"
    if intent in {"M27", "M28", "M29", "M30", "M31", "M32", "M33", "M34"}:
        baseline = re.search(r"instead of (\d{1,2})", text)
        remaining = re.search(r"\b(\d{1,3}) (?:remaining credits|credits (?:left|remaining))\b", text)
        if baseline and 1 <= int(baseline[1]) <= 40:
            update["baseline_credits"] = int(baseline[1])
        if remaining:
            update["remaining_credits"] = int(remaining[1])
        if "summer" in text:
            update["include_summer"] = True
        if "live at home" in text:
            update["live_at_home"] = True
        return context.model_copy(update={"scenario": (context.scenario or Scenario()).model_copy(update=update)})
    if any(field in update and update[field] != getattr(context, field) for field in ("subject", "campus", "credential")):
        update["program_id"] = None
    return context.model_copy(update=update)


def followups(intent, context, current, previous, unavailable):
    related = {
        "M01": ("M03", "M04", "M05", "M16"),
        "M02": ("M05", "M07", "M10", "M17"),
        "M03": ("M05", "M06", "M10", "M17", "M11"),
        "M05": ("M10", "M17", "M11", "M16", "M07"),
        "M10": ("M11", "M17", "M14", "M16", "M35"),
        "M27": ("M34", "M17", "M18", "M35"),
    }
    defaults = related.get(intent, ("M05", "M04", "M10", "M16", "M35"))
    labels = list(SPEC[intent]["suggestions"])
    if context.subject:
        labels += [
            f"Find colleges offering {context.subject}",
            f"Compare {context.subject} tuition",
            f"Show {context.subject} prerequisites",
            f"Build a sample {context.subject} education plan",
        ]
    if context.subject == "nursing":
        labels += ["Show the ADN pathway", "Compare ADN and BSN", "I already have a GED"]
    labels += [STARTERS.get(i, SPEC[i]["utterances"][0]) for i in defaults]
    labels += ["What is a credit hour?", "Show public colleges in New Mexico",
               "How does Mesa use my information?", "Compare colleges and programs"]
    if intent == "M38":
        return []
    seen = {simplify(current), *(simplify(label) for label in previous)}
    ranked = []
    for index, label in enumerate(labels):
        key = simplify(label)
        target = route(label, intent)
        if key in seen or target in unavailable or target in {"M37", "M38"}:
            continue
        if context.education_stage and re.search(r"\b(?:i have|i already|i'm a high.school)\b", key):
            continue
        if re.search(r"\b(?:send|confirm|overwrite|share|save)\b", key):
            continue
        seen.add(key)
        score = 20 if context.subject and context.subject in key else 0
        score += 8 if target in defaults else 0
        score += 3 if target != intent else 0
        ranked.append((score, -index, label, target))
    ranked.sort(reverse=True)
    result, counts = [], {}
    for _, _, label, target in ranked:
        if counts.get(target, 0) >= 2:
            continue
        result.append(Choice(id=uuid4(), label=label, intent=target))
        counts[target] = counts.get(target, 0) + 1
    return result[:8]
