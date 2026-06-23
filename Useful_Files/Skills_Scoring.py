import re
from collections import defaultdict

CATEGORIES = [
    "Technical",
    "Analytical",
    "Agile/Methodology",
    "Broad-Scope",
    "Compliance",
    "Investigative",
    "Law/Regulatory",
    "Legal/Regulatory",
    "Policy-Focused",
]

# =========================
# STRONG PHRASE RULES
# =========================

PHRASE_RULES = {

    "Technical": {
        r"\bcloud\b": 4,
        r"\bapi\b": 4,
        r"\bapis\b": 4,
        r"\bci/cd\b": 5,
        r"\bcicd\b": 5,
        r"\bpipeline\b": 4,
        r"\bpipelines\b": 4,
        r"\bcyber security\b": 5,
        r"\bsecurity tools\b": 5,
        r"\bincident response\b": 5,
        r"\boperational technology\b": 5,
        r"\btechnical terminology\b": 4,
        r"\bhardware\b": 4,
        r"\bsoftware\b": 4,
        r"\bnetwork\b": 4,
        r"\bmonitoring\b": 4,
        r"\bdata quality\b": 4,
        r"\bdata lineage\b": 5,
        r"\buser documentation\b": 4,
        r"\bcoordinate security\b": 4,
        r"\bhealth and safety\b": 3,
    },

    "Analytical": {
        r"\baccounting\b": 5,
        r"\bfinancial statements\b": 5,
        r"\brisk management\b": 4,
        r"\bproblem solving\b": 4,
        r"\bconsult with business clients\b": 5,
        r"\bimprove business processes\b": 5,
        r"\bprocess mapping\b": 5,
        r"\bdata analysis\b": 5,
        r"\banalytical\b": 4,
        r"\breporting\b": 4,
        r"\binsights\b": 4,
        r"\bforecast\b": 4,
    },

    "Compliance": {
        r"\bconduct financial audits\b": 6,
        r"\binternal auditing\b": 6,
        r"\bdevelop audit plan\b": 6,
        r"\baml\b": 6,
        r"\bkyc\b": 6,
        r"\bsanctions\b": 5,
        r"\bcompliance\b": 4,
        r"\baudit\b": 5,
        r"\bcontrols?\b": 3,
    },

    "Investigative": {
        r"\bfraud\b": 5,
        r"\bfraud detection\b": 6,
        r"\binvestigation\b": 5,
        r"\binvestigative\b": 5,
        r"\bforensic\b": 5,
        r"\bcybercrime\b": 6,
        r"\bevidence\b": 4,
        r"\binterview\b": 3,
        r"\bincident\b": 2,
    },

    "Law/Regulatory": {
        r"\blaw\b": 5,
        r"\bcourt\b": 5,
        r"\be-discovery\b": 6,
        r"\bchain of custody\b": 6,
        r"\blegislation\b": 5,
        r"\bprosecution\b": 5,
        r"\bjudicial\b": 5,
    },

    "Legal/Regulatory": {
        r"\blegal\b": 4,
        r"\bregulatory\b": 4,
        r"\bregulations\b": 4,
        r"\bgdpr\b": 5,
        r"\bprivacy\b": 5,
        r"\blegal requirements\b": 5,
        r"\bcompany regulations\b": 5,
        r"\bconfidentiality\b": 5,
    },

    "Policy-Focused": {
        r"\bpolicy\b": 4,
        r"\bpolicies\b": 4,
        r"\binternal risk management policy\b": 7,
        r"\bensure compliance with policies\b": 7,
        r"\bcompany policies\b": 6,
        r"\bdefine security policies\b": 6,
        r"\bprocedures\b": 4,
        r"\bstandards\b": 4,
        r"\bguidelines\b": 4,
        r"\bgovernance\b": 4,
    },

    "Agile/Methodology": {
        r"\bproject management\b": 6,
        r"\bagile\b": 5,
        r"\bscrum\b": 5,
        r"\bkanban\b": 5,
        r"\bcontinuous improvement\b": 4,
        r"\binnovation processes\b": 4,
        r"\bmethodology\b": 5,
        r"\bworkflow\b": 3,
    },

    "Broad-Scope": {
        r"\bcommunication\b": 5,
        r"\buse microsoft office\b": 6,
        r"\bmeet deadlines\b": 5,
        r"\bmultiple tasks\b": 5,
        r"\bmanage personal professional development\b": 6,
        r"\bteamwork\b": 5,
        r"\bsoft skills\b": 5,
        r"\badaptability\b": 5,
        r"\bgeneral\b": 3,
    },
}


PRIORITY = [
    "Compliance",
    "Law/Regulatory",
    "Legal/Regulatory",
    "Investigative",
    "Policy-Focused",
    "Agile/Methodology",
    "Analytical",
    "Technical",
    "Broad-Scope",
]


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def score_skill(skill):

    s = normalize(skill)
    scores = defaultdict(float)

    for cat, rules in PHRASE_RULES.items():
        for pattern, weight in rules.items():
            if re.search(pattern, s):
                scores[cat] += weight

    if not scores:
        scores["Broad-Scope"] = 1

    best = max(scores.values())

    tied = [c for c, v in scores.items() if v == best]

    if len(tied) == 1:
        pred = tied[0]
    else:
        for p in PRIORITY:
            if p in tied:
                pred = p
                break

    return pred, dict(scores)


# Example

skills = [
    "accounting",
    "conduct financial audits",
    "ensure compliance with policies",
    "incident response",
    "cloud platforms",
    "e-discovery",
    "chain of custody",
    "project management",
    "communication",
]

for s in skills:
    print(s, "->", score_skill(s))