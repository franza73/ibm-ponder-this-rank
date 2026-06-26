import re
import html
from collections import defaultdict

INPUT_FILE = "./ibm_rank.txt"
TOP_N = 40

# ------------------------------------------------------------------
# 1. EXPLICIT ALIASES (highest priority, exact identity)
# ------------------------------------------------------------------
ALIASES = {
    "william clinton": "Bill Clinton",
    "balakrishnan v" : "Balakrishnan Varadarajan",
    "v balakrishnan" : "Balakrishnan Varadarajan", 
    "franza cavalcante" : "Franciraldo Cavalcante",
    "franza cavalcante jr" : "Franciraldo Cavalcante",
    "franciraldo cavalcante jr" : "Franciraldo Cavalcante",
    "lachezar hristov": "Latchezar Christov",
    "lachezar christov": "Latchezar Christov",
    "harald boegeholz": "Harald Bögeholz",
    "joseph divincentis": "Joseph Devincentis",
    "reichel lorenz": "Lorenz Reichel",
    "gmgerken": "Gary Gerken",
    "gary gerkin": "Gary Gerken",
    "gary m gerkin": "Gary Gerken",
    "andreasstiller": "Andreas Stiller",
    "dan shouky": "Shouky Dan",
    "stephane higueret": "Stéphane Higueret",
    "armin krauß": "Armin Krauss",
}

# ------------------------------------------------------------------
# 2. NICKNAME NORMALIZATION (used only if no explicit alias)
# ------------------------------------------------------------------
NICKNAMES = {
    "joe": "joseph",
    "bill": "william",
    "dave": "david",
}

IGNORED_TOKENS = {}

MONTH_YEAR_RE = re.compile(r'^\s*([A-Za-z]+)\s*(\d{4})\b')

# ------------------------------------------------------------------
# NORMALIZATION UTILITIES
# ------------------------------------------------------------------
def clean_text(s: str) -> str:
    s = html.unescape(s.lower())
    s = s.replace('*', '')
    s = re.sub(r'\b\d+\b', '', s)
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def split_names(text: str):
    for sep in ['&', ' and ', '/', ';', ',', '+']:
        text = text.replace(sep, '|')
    return [n.strip() for n in text.split('|') if n.strip()]

def canonical_from_structure(raw_name: str) -> str:
    s = clean_text(raw_name)
    tokens = [t for t in s.split() if t not in IGNORED_TOKENS]

    if len(tokens) < 2:
        return raw_name.strip()

    surname = tokens[-1]
    given = tokens[0]

    given = NICKNAMES.get(given, given)

    return f"{given.capitalize()} {surname.capitalize()}"

def canonical_name(raw_name: str) -> str:
    norm = clean_text(raw_name)

    # 1) explicit alias wins
    if norm in ALIASES:
        return ALIASES[norm]

    # 2) otherwise structured nickname-based identity
    return canonical_from_structure(raw_name)

# ------------------------------------------------------------------
# RANKING LOGIC
# ------------------------------------------------------------------
def compute_ranking(path):
    solved = defaultdict(set)

    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = MONTH_YEAR_RE.match(line)
            if not m:
                continue

            month, year = m.group(1), int(m.group(2))
            key = (year, month)

            rest =  html.unescape(line[m.end():])
            for raw in split_names(rest):
                canon = canonical_name(raw)
                solved[canon].add(key)

    rows = [(name, len(months)) for name, months in solved.items()]
    rows.sort(key=lambda x: (-x[1], x[0]))

    ranked = []
    rank = 0
    prev = None

    for i, (name, score) in enumerate(rows, start=1):
        if score != prev:
            rank = i
            prev = score
        ranked.append((rank, name, score))

    return ranked

# ------------------------------------------------------------------
# OUTPUT
# ------------------------------------------------------------------
if __name__ == "__main__":
    ranking = compute_ranking(INPUT_FILE)

    print(f"{'Rank':<5} {'Solver Name':<35} {'Months Solved'}")
    print("-" * 60)

    for r, name, score in ranking[:TOP_N]:
        print(f"{r:<5} {name:<35} {score}")
