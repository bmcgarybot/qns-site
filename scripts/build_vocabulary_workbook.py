from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"
IMG = ROOT / "img" / "training"
APP = ROOT / "apps" / "my-buddy-demo.html"

NAVY = colors.HexColor("#17313A")
TEAL = colors.HexColor("#2A9D8F")
GOLD = colors.HexColor("#C9A54E")
PAPER = colors.HexColor("#F7F4EC")
MUTED = colors.HexColor("#5D6B70")
GREEN = colors.HexColor("#A8E6A3")
BLUE = colors.HexColor("#A9D6F5")
ORANGE = colors.HexColor("#F7C684")
YELLOW = colors.HexColor("#F5E879")
PINK = colors.HexColor("#F4B6C2")
GRAY = colors.HexColor("#D9DEE0")
WHITE = colors.white


def extract_home_words():
    text = APP.read_text(encoding="utf-8")
    block = text.split("const V=[", 1)[1].split("];", 1)[0]
    found = []
    for match in re.finditer(r'\{w:"([^"]+)",t:"([^"]+)".*?,p:(\d+)\}', block):
        found.append((int(match.group(3)), match.group(1), match.group(2)))
    found.sort()
    if len(found) != 84:
        raise RuntimeError(f"Expected 84 home cells, found {len(found)}")
    return found


def styles(bw=False):
    base = getSampleStyleSheet()
    accent = colors.HexColor("#3F4649") if bw else TEAL
    ink = colors.HexColor("#222222") if bw else NAVY
    callout_bg = colors.HexColor("#F0F0F0") if bw else colors.HexColor("#FFF9E8")
    result = {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=31, leading=34, textColor=WHITE, alignment=TA_LEFT, spaceAfter=12),
        "subtitle": ParagraphStyle("subtitle", parent=base["BodyText"], fontName="Helvetica", fontSize=13, leading=18, textColor=colors.HexColor("#D9E5E7")),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=22, leading=24, textColor=ink, spaceAfter=0),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=accent, spaceBefore=10, spaceAfter=5),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.4, leading=13, textColor=ink, spaceAfter=6),
        "small": ParagraphStyle("small", parent=base["BodyText"], fontName="Helvetica", fontSize=7.7, leading=10, textColor=MUTED),
        "callout": ParagraphStyle("callout", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=10.3, leading=14, textColor=ink, borderColor=colors.HexColor("#555555") if bw else GOLD, borderWidth=1.2, borderPadding=10, backColor=callout_bg, spaceBefore=8, spaceAfter=9),
        "cell": ParagraphStyle("cell", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=6.3, leading=7.2, alignment=TA_CENTER, textColor=NAVY),
        "table": ParagraphStyle("table", parent=base["BodyText"], fontName="Helvetica", fontSize=7.7, leading=9.5, textColor=NAVY),
        "table_bold": ParagraphStyle("table_bold", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.7, leading=9.5, textColor=ink),
        "chip": ParagraphStyle("chip", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=9, textColor=WHITE, alignment=TA_CENTER),
    }
    result["_accent"] = accent
    result["_ink"] = ink
    result["_bw"] = bw
    result["_section"] = 0
    return result


def P(text, style):
    return Paragraph(text, style)


def bullets(items, st):
    return [P("• " + item, st) for item in items]


def page_header(canvas, doc, bw=False):
    page = canvas.getPageNumber()
    canvas.saveState()
    if page == 1:
        canvas.setFillColor(colors.HexColor("#202020") if bw else NAVY)
        canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
        # A field of AAC-style word tiles gives the cover a recognizable visual rhythm.
        tile_colors = [colors.HexColor("#B8B8B8")] * 5 if bw else [YELLOW, GREEN, BLUE, ORANGE, PINK]
        for row in range(3):
            for col in range(5):
                x = 0.58 * inch + col * 0.72 * inch
                y = 0.65 * inch + row * 0.62 * inch
                canvas.setFillColor(tile_colors[(row + col) % len(tile_colors)])
                canvas.roundRect(x, y, .56 * inch, .46 * inch, 5, fill=1, stroke=0)
                canvas.setFillColor(colors.HexColor("#17313A") if not bw else colors.HexColor("#222222"))
                canvas.setFont("Helvetica-Bold", 6.5)
                words = ["I", "want", "go", "help", "more", "stop", "feel", "where", "to", "school"]
                canvas.drawCentredString(x + .28 * inch, y + .20 * inch, words[(row * 5 + col) % len(words)])
        canvas.setFillColor(GOLD if not bw else colors.HexColor("#A0A0A0"))
        canvas.rect(7.88 * inch, 0, .62 * inch, 11 * inch, fill=1, stroke=0)
        canvas.restoreState()
        return

    canvas.setFillColor(colors.HexColor("#FAF8F1") if not bw else colors.HexColor("#FAFAFA"))
    canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#333333") if bw else NAVY)
    canvas.rect(0, 10.58 * inch, 8.5 * inch, .42 * inch, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#707070") if bw else TEAL)
    canvas.rect(0, 0, .14 * inch, 11 * inch, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#BBBBBB") if bw else GOLD)
    canvas.roundRect(7.82 * inch, 9.78 * inch, .34 * inch, .34 * inch, 4, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#D8D8D8") if bw else colors.HexColor("#DCEBE8"))
    canvas.roundRect(7.37 * inch, 9.78 * inch, .34 * inch, .34 * inch, 4, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#999999") if bw else colors.HexColor("#9ECED0"))
    canvas.roundRect(6.92 * inch, 9.78 * inch, .34 * inch, .34 * inch, 4, fill=1, stroke=0)
    if page > 1:
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(WHITE)
        canvas.drawString(0.58 * inch, 10.73 * inch, "MY BUDDY AAC  |  VOCABULARY LEARNING WORKBOOK")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(7.92 * inch, 0.36 * inch, f"{page}")
        canvas.drawString(0.58 * inch, 0.36 * inch, "Free to print and share for My Buddy training")
    canvas.restoreState()


def info_table(rows, st, widths=(1.55 * inch, 5.55 * inch), header=True):
    data = [[P(str(c), st["table_bold"] if r == 0 and header else st["table"]) for c in row] for r, row in enumerate(rows)]
    table = Table(data, colWidths=list(widths), repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C2C5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), st["_ink"]), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE)]
    for r in range(1 if header else 0, len(rows)):
        if r % 2 == 0:
            commands.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#F0F3F3")))
    table.setStyle(TableStyle(commands))
    return table


def blank_lines(count=4):
    data = [[""] for _ in range(count)]
    t = Table(data, colWidths=[7.1 * inch], rowHeights=[0.28 * inch] * count)
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), .6, colors.HexColor("#9BA8AC"))]))
    return t


def word_tiles(words, kinds, st, bw=False, caption=None):
    fills = {"verb": GREEN, "adjective": BLUE, "noun": ORANGE, "pronoun": YELLOW, "social": PINK, "grammar": WHITE, "folder": GRAY}
    shade = {"verb": .88, "adjective": .80, "noun": .72, "pronoun": .94, "social": .84, "grammar": 1.0, "folder": .68}
    cells = []
    for word, kind in zip(words, kinds):
        label = f"<b>{word}</b><br/><font size='6'>{kind.upper()}</font>"
        cells.append(P(label, ParagraphStyle("tile", parent=st["cell"], fontSize=9, leading=10, textColor=st["_ink"])))
    width = min(1.1 * inch, 6.6 * inch / max(len(cells), 1))
    table = Table([cells], colWidths=[width] * len(cells), rowHeights=[.68 * inch], hAlign="LEFT")
    cmds = [("GRID", (0, 0), (-1, -1), 1, st["_ink"]), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
    for i, kind in enumerate(kinds):
        fill = colors.Color(shade.get(kind, 1), shade.get(kind, 1), shade.get(kind, 1)) if bw else fills.get(kind, WHITE)
        cmds.append(("BACKGROUND", (i, 0), (i, 0), fill))
    table.setStyle(TableStyle(cmds))
    items = []
    if caption:
        items += [P(caption, st["small"]), Spacer(1, 4)]
    items.append(table)
    return KeepTogether(items)


def home_map(st, bw=False):
    words = extract_home_words()
    type_fill = {"verb": GREEN, "adjective": BLUE, "noun": ORANGE, "pronoun": YELLOW, "social": PINK, "folder": GRAY, "grammar": WHITE, "util": colors.HexColor("#E7A0A0")}
    rows = []
    types = []
    for r in range(7):
        row, ty = [], []
        for c in range(12):
            _, word, kind = words[r * 12 + c]
            row.append(P(f"{word}<br/><font size='4'>{kind.upper()}</font>", st["cell"]))
            ty.append(kind)
        rows.append(row)
        types.append(ty)
    t = Table(rows, colWidths=[0.61 * inch] * 12, rowHeights=[0.62 * inch] * 7)
    cmds = [("GRID", (0, 0), (-1, -1), .55, NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
    for r in range(7):
        for c in range(12):
            fill = type_fill.get(types[r][c], WHITE)
            if bw:
                shades = {"verb": .90, "adjective": .83, "noun": .76, "pronoun": .94, "social": .86, "folder": .70, "grammar": 1, "util": .80}
                v = shades.get(types[r][c], 1)
                fill = colors.Color(v, v, v)
            cmds.append(("BACKGROUND", (c, r), (c, r), fill))
    t.setStyle(TableStyle(cmds))
    return t


def color_key(st, bw=False):
    rows = [
        ("Green", "Action words", "go, help, make, open"),
        ("Blue", "Describing words", "big, little, hot, different"),
        ("Orange", "People, places and things", "school, teacher, food"),
        ("Yellow", "Pronouns", "I, you, he, she, we, they"),
        ("White", "Grammar and location words", "to, in, on, not, the"),
        ("Pink", "Social and conversation words", "hello, please, sorry"),
        ("Gray", "Folder doorways", "people, places, food, health"),
    ]
    data = [[P("Color", st["table_bold"]), P("Job", st["table_bold"]), P("Examples", st["table_bold"])]]
    for a, b, c in rows:
        data.append([P(a, st["table_bold"]), P(b, st["table"]), P(c, st["table"])])
    t = Table(data, colWidths=[1.05 * inch, 2.4 * inch, 3.7 * inch])
    cmds = [("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#AAB5B8")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, 0), st["_ink"]), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]
    fills = [GREEN, BLUE, ORANGE, YELLOW, WHITE, PINK, GRAY]
    for r in range(1, 8):
        fill = fills[r - 1]
        if bw:
            v = .96 - (r - 1) * .045
            fill = colors.Color(v, v, v)
        cmds.append(("BACKGROUND", (0, r), (0, r), fill))
    t.setStyle(TableStyle(cmds))
    return t


def add_page(story, st, title, intro=None):
    st["_section"] += 1
    heading = Table([[P(f"{st['_section']:02d}", st["chip"]), P(title, st["h1"]) ]], colWidths=[.47 * inch, 6.5 * inch], hAlign="LEFT")
    heading.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), st["_accent"]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (0, 0), 0, st["_accent"]),
        ("LEFTPADDING", (0, 0), (0, 0), 4), ("RIGHTPADDING", (0, 0), (0, 0), 4),
        ("TOPPADDING", (0, 0), (0, 0), 7), ("BOTTOMPADDING", (0, 0), (0, 0), 7),
        ("LEFTPADDING", (1, 0), (1, 0), 12), ("RIGHTPADDING", (1, 0), (1, 0), 0),
    ]))
    story += [heading, Spacer(1, 8), HRFlowable(width="100%", thickness=1.5, color=st["_accent"], spaceAfter=10)]
    if intro:
        story.append(P(intro, st["body"]))


def build(path, bw=False):
    st = styles(bw=bw)
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=.58 * inch, leftMargin=.66 * inch, topMargin=.70 * inch, bottomMargin=.58 * inch, title="My Buddy AAC Vocabulary Learning Workbook", author="BMC Luminary Ventures LLC")
    S = []

    # 1 Cover
    cover_bg = colors.HexColor("#202020") if bw else NAVY
    cover = Table([[P("MY BUDDY AAC", ParagraphStyle("eyebrow", parent=st["small"], textColor=colors.HexColor("#BDBDBD") if bw else GOLD, fontName="Helvetica-Bold", fontSize=10, leading=13)),], [P("Vocabulary<br/>Learning Workbook", st["title"])], [P("Learn the board. Build original messages. Practice during real life.", st["subtitle"])], [P("For communicators, families, teachers, aides, and care teams", ParagraphStyle("coverSmall", parent=st["small"], textColor=WHITE, fontSize=9.5, leading=13))]], colWidths=[7.15 * inch], rowHeights=[.45 * inch, 2.15 * inch, 1.15 * inch, .8 * inch])
    cover.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), cover_bg), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 28), ("RIGHTPADDING", (0, 0), (-1, -1), 28)]))
    cover_note = ParagraphStyle("coverNote", parent=st["body"], textColor=WHITE, borderColor=GOLD if not bw else colors.HexColor("#BBBBBB"), borderWidth=1.2, borderPadding=11, backColor=colors.HexColor("#23434C") if not bw else colors.HexColor("#303030"), fontName="Helvetica-Bold", alignment=TA_CENTER)
    S += [Spacer(1, .5 * inch), cover, Spacer(1, .35 * inch), P("An original, printer-friendly companion to the free My Buddy communication board", cover_note), Spacer(1, .42 * inch), P("2026 edition  |  quantumneuroshift.com", ParagraphStyle("coverFoot", parent=st["body"], alignment=TA_CENTER, fontName="Helvetica-Bold", textColor=WHITE)), PageBreak()]

    # 2 contents
    add_page(S, st, "How to use this workbook", "Use this beside the live My Buddy board. Point to words on the device while you talk. Let the communicator explore. Practice is for learning, not testing.")
    S.append(P("The goal is communication", st["callout"]))
    S += bullets([
        "Honor every clear message, including no, stop, different, and all done.",
        "Model one or two words beyond the communicator's current message length.",
        "Keep words in stable locations. Repetition helps the movement become familiar.",
        "Do not require perfect tapping, eye contact, imitation, or a spoken response.",
        "Keep the full vocabulary available. Focus Practice can reduce visual distraction without removing access.",
    ], st["body"])
    S.append(P("Contents", st["h2"]))
    S.append(info_table([
        ("Page", "Section"), ("3", "What makes a strong AAC system"), ("4", "The My Buddy home map"), ("5", "Colors and word jobs"), ("6", "Core words and folder words"), ("7", "Stable routes and repeated words"), ("8", "Pronouns and sentence building"), ("9", "Grammar and flexible language"), ("10", "Find and Focus Practice"), ("11", "Practice 1: learn the home board"), ("12", "Practice 2: build new messages"), ("13", "Practice 3: communicate for many reasons"), ("14", "Practice 4: daily routine plan"), ("15", "Communication partner practice"), ("16", "Progress reflection and answer guidance"), ("17", "Useful links and notes"),
    ], st, widths=(.8 * inch, 6.3 * inch)))
    S.append(PageBreak())

    # 3 principles
    add_page(S, st, "What makes a strong AAC system", "My Buddy is organized to support original language, not only stored requests. The board combines frequently useful core words with folders for specific people, places, things, and topics.")
    S.append(info_table([
        ("Design choice", "Why it matters"),
        ("Words, not only phrases", "A person can combine words to say something new, change a message, ask a question, disagree, tell a story, or repair a misunderstanding."),
        ("Stable locations", "A word stays in the same place. The communicator can learn the movement instead of searching a rearranged board."),
        ("Core words first", "Words such as I, want, go, help, not, more, and different work across many activities."),
        ("Specific vocabulary too", "Folders add names, foods, places, health words, school words, dates, and other personally useful language."),
        ("Grammar access", "Pronoun forms, verb forms, endings, question words, articles, and joining words support more complete language."),
        ("Multiple access supports", "Full View, Simple View, Find, Focus Practice, editing, photos, keyboard access, and speech settings serve different needs."),
    ], st, widths=(1.55 * inch, 5.55 * inch)))
    S.append(P("My Buddy is not a medical device and does not replace an individualized AAC assessment. A speech-language pathologist can help match access, vocabulary, and support to the communicator.", st["callout"]))
    S.append(PageBreak())

    # 4 map
    add_page(S, st, "The My Buddy home map", "This is the exact 12 by 7 word order used by the current English Full View board. The small labels show each button's word job. The app also displays a symbol.")
    S.append(home_map(st, bw=bw))
    S.append(Spacer(1, 8))
    S.append(P("Map reading tips", st["h2"]))
    S += bullets(["Rows 1 through 4 hold stable pronouns, actions, grammar, and location words.", "Rows 5 and 6 add responses, descriptions, social language, questions, to, and the grammar doorway.", "Row 7 contains folder doorways. A folder opens more vocabulary while the home position stays unchanged."], st["body"])
    S.append(PageBreak())

    # 5 colors
    add_page(S, st, "Colors show what a word does", "Color is a clue, not a rule the communicator must memorize. Each button also has a written word and a picture. In black-and-white printing, the word-job labels remain visible.")
    S.append(color_key(st, bw=bw))
    S.append(P("Try it", st["h2"]))
    S.append(P("Find one action, one pronoun, one describing word, one grammar word, and one folder doorway on the home map. Circle each one above.", st["body"]))
    S.append(blank_lines(5))
    S.append(P("A color should remain consistent when a word appears on a linked page. Consistency helps the communicator predict the kind of language available.", st["callout"]))
    S.append(PageBreak())

    # 6 core/fringe
    add_page(S, st, "Core words and folder words", "Core words are useful across many settings. Folder words are more specific. Good communication needs both.")
    S.append(info_table([
        ("Core words can...", "Folder words can..."),
        ("request: want, more, different", "name a specific food, toy, person, or place"),
        ("refuse: no, not, stop, all done", "name what hurts or which medicine is needed"),
        ("comment: like, good, funny, big", "talk about a class, holiday, month, or hobby"),
        ("direct: go, come, give, open, put", "identify a caregiver, teacher, pet, or family member"),
        ("ask: what, where, who, why, how", "supply the exact topic of a question"),
    ], st, widths=(3.55 * inch, 3.55 * inch)))
    S.append(P("Build these without using a stored sentence", st["h2"]))
    S.append(info_table([
        ("Meaning", "Possible word-built message"), ("request", "I + want + different + food"), ("refusal", "no + not that"), ("direction", "go + to + school"), ("health", "I + feel + sick"), ("repair", "not that + I mean..."),
    ], st, widths=(1.35 * inch, 5.75 * inch)))
    S.append(P("Messages are made from reusable parts", st["h2"]))
    S.append(word_tiles(["I", "want", "different", "food"], ["pronoun", "verb", "adjective", "noun"], st, bw=bw, caption="A request that can change with the situation"))
    S.append(Spacer(1, 8))
    S.append(word_tiles(["no", "not", "that"], ["social", "grammar", "grammar"], st, bw=bw, caption="A refusal or correction"))
    S.append(PageBreak())

    # 7 routes
    add_page(S, st, "Stable routes and repeated words", "Some home words open an expanded page. The same word appears in the same position on that page, so the first tap opens the family and the second tap speaks the original word.")
    S.append(info_table([
        ("Start on Home", "What the next page provides", "Example"),
        ("make", "make plus related forms and useful action vocabulary", "I + make + food"),
        ("feel", "feel plus feeling words", "I + feel + worried"),
        ("I / you / he / she / we / they", "pronoun forms and predictable sentence starters", "she + wants + more"),
        ("grammar", "endings, articles, joining words, questions, and sentence tools", "walk + ing"),
        ("folder doorway", "specific vocabulary for that topic", "go + to + school"),
    ], st, widths=(1.35 * inch, 3.8 * inch, 1.95 * inch)))
    S.append(P("Practice the movement", st["h2"]))
    S += bullets(["Choose one useful word.", "Start at Home every time.", "Tap the doorway, then the target.", "Say the message naturally and continue the activity.", "Repeat during real moments, but never withhold the desired item or activity until a perfect tap."], st["body"])
    S.append(P("Route I want to practice:", st["h2"]))
    S.append(word_tiles(["HOME: make", "→", "MAKE PAGE: make", "→", "food"], ["verb", "grammar", "verb", "grammar", "noun"], st, bw=bw, caption="Example route: the repeated word remains the anchor"))
    S.append(Spacer(1, 8))
    S.append(blank_lines(5))
    S.append(PageBreak())

    # 8 pronouns
    add_page(S, st, "Pronouns help build complete messages", "The first columns keep pronouns in predictable home locations. Pronoun pages provide forms and common sentence frames without replacing flexible word-by-word language.")
    S.append(info_table([
        ("Person", "Subject", "Object", "Possessive", "Example"),
        ("speaker", "I", "me", "my / mine", "I want my book"),
        ("listener", "you", "you", "your / yours", "you help me"),
        ("another person", "he / she / they", "him / her / them", "they want it"),
        ("group including speaker", "we", "us", "our / ours", "we go together"),
    ], st, widths=(1.25 * inch, 1.05 * inch, 1.05 * inch, 1.35 * inch, 2.4 * inch)))
    S.append(P("Build two messages", st["h2"]))
    S.append(P("1. Start with a person, add an action, then add one more word.<br/>2. Change only the person and notice how the meaning changes.", st["body"]))
    S.append(word_tiles(["she", "wants", "more"], ["pronoun", "verb", "adjective"], st, bw=bw, caption="Person + action + more information"))
    S.append(Spacer(1, 8))
    S.append(blank_lines(8))
    S.append(PageBreak())

    # 9 grammar
    add_page(S, st, "Grammar supports flexible language", "Grammar is available when it helps the communicator say the intended meaning. Do not correct every message. Model a slightly fuller version while responding to the message first.")
    S.append(info_table([
        ("Tool", "Examples", "What it can express"),
        ("negation", "no, not, don't, can't", "refusal, correction, disagreement"),
        ("endings", "-ing, -ed, -s", "ongoing action, past action, plural or third person"),
        ("time", "now, before, later, yesterday", "when something happens"),
        ("questions", "who, what, where, when, why, how", "information and conversation"),
        ("joining words", "and, but, because, if", "longer and more exact ideas"),
        ("articles / helpers", "a, the, am, is, are, was, were", "sentence structure"),
    ], st, widths=(1.25 * inch, 2.15 * inch, 3.7 * inch)))
    S.append(P("Partner modeling examples", st["h2"]))
    S += bullets(["Communicator: go school. Partner: Yes, we will go to school.", "Communicator: not that. Partner: You do not want that. You want different.", "Communicator: she sad. Partner: She is sad. What happened?"], st["body"])
    S.append(word_tiles(["I", "was", "play", "-ing"], ["pronoun", "grammar", "verb", "grammar"], st, bw=bw, caption="Grammar pieces can add time and detail"))
    S.append(PageBreak())

    # 10 tools
    add_page(S, st, "Find and Focus Practice", "Both tools teach the existing board. Neither tool changes the word map.")
    S.append(info_table([
        ("Tool", "Use it when...", "What happens"),
        ("Find", "you know the word but not its location", "My Buddy shows the tap path and can teach the route one step at a time."),
        ("Focus Practice", "a learner or partner is practicing a small target set", "Chosen words and every needed doorway are highlighted. Other buttons remain visible and usable in their normal locations."),
        ("Simple View", "a small phone screen or reduced display is needed", "A smaller meaningful vocabulary remains available. Full View can be restored at any time."),
    ], st, widths=(1.25 * inch, 2.55 * inch, 3.3 * inch)))
    S.append(P("Suggested first Focus Practice set", st["h2"]))
    S.append(P("I, want, more, go, stop, help, no, yes", st["callout"]))
    S.append(P("Add only words that matter in the person's real day. End Focus Practice whenever the person needs the whole board without dimming.", st["body"]))
    S.append(P("Words for our next practice:", st["h2"]))
    S.append(blank_lines(6))
    S.append(PageBreak())

    # 11 practice map
    add_page(S, st, "Practice 1: learn the home board", "Use the map on page 4. This is an open-book activity. The purpose is to notice patterns, not memorize a test.")
    tasks = [
        "1. Write the six home pronouns.", "2. Find four action words that could be used during play.", "3. Find three words that can refuse or stop something.", "4. Find the word that connects an action to a destination in go to school.", "5. Name three folder doorways in the bottom row.", "6. Find two question words.", "7. Circle the button you would use to reach endings and sentence tools.",
    ]
    S += [P(t, st["body"]) for t in tasks]
    S.append(blank_lines(12))
    S.append(PageBreak())

    # 12 build
    add_page(S, st, "Practice 2: build new messages", "There can be more than one correct answer. Use the board to build a message that matches each situation.")
    S.append(info_table([
        ("Situation", "Your word-built message"),
        ("You want to go somewhere different.", ""),
        ("You need someone to stop and listen.", ""),
        ("Something hurts, but the listener misunderstood where.", ""),
        ("You liked an activity and want it again.", ""),
        ("You want to ask who is coming.", ""),
        ("You want to say what happened yesterday.", ""),
        ("You do not know the word, so you describe it.", ""),
    ], st, widths=(3.55 * inch, 3.55 * inch)))
    S.append(P("Make one message longer by adding a person, action, description, place, or time word.", st["callout"]))
    S.append(blank_lines(4))
    S.append(PageBreak())

    # 13 functions
    add_page(S, st, "Practice 3: communicate for many reasons", "AAC is not only for requesting. Plan at least one natural opportunity for each communication function.")
    S.append(info_table([
        ("Reason", "Possible words", "Real opportunity"),
        ("request", "want, more, different", ""),
        ("refuse", "no, stop, not, all done", ""),
        ("comment", "like, funny, good, big", ""),
        ("ask", "what, where, who, why, how", ""),
        ("direct", "go, come, give, put, open", ""),
        ("share feelings", "feel plus a feeling word", ""),
        ("repair", "not that, I mean, show me", ""),
        ("social connection", "hello, please, thank you, sorry", ""),
    ], st, widths=(1.4 * inch, 2.6 * inch, 3.1 * inch)))
    S.append(P("A communication partner should notice and respond to all of these reasons, not only requests for objects.", st["callout"]))
    S.append(PageBreak())

    # 14 routine
    add_page(S, st, "Practice 4: plan one daily routine", "Choose a routine that already happens. Model useful words while the activity continues. Leave room for refusal, questions, comments, and unexpected messages.")
    S.append(info_table([
        ("Plan item", "Write your plan"),
        ("Routine", ""), ("Where and when", ""), ("Core words to model", ""), ("Specific folder words", ""), ("Possible refusal", ""), ("Possible comment", ""), ("Possible question", ""), ("How we will wait and respond", ""),
    ], st, widths=(2.05 * inch, 5.05 * inch)))
    S.append(P("Examples: getting dressed, making food, using the bathroom, washing hands, going to school, taking medicine, playing a game, watching a show, or getting ready for bed.", st["small"]))
    S.append(PageBreak())

    # 15 partner
    add_page(S, st, "Communication partner practice", "The partner's behavior can make communication easier or harder. Practice these habits before a high-pressure moment.")
    S.append(info_table([
        ("Do", "Avoid"),
        ("Keep the device within reach and charged.", "Putting it away because the activity is messy, social, or fast."),
        ("Model words without demanding a copy.", "Turning every model into a quiz or command."),
        ("Pause long enough for a response.", "Answering for the communicator too quickly."),
        ("Believe and act on clear messages.", "Ignoring no, stop, pain, different, or all done."),
        ("Confirm when a message is unclear.", "Pretending to understand or repeatedly guessing."),
        ("Keep a printed backup available.", "Relying on one battery, one browser, or one device."),
    ], st, widths=(3.55 * inch, 3.55 * inch)))
    S.append(P("Write a respectful response to each message", st["h2"]))
    S += [P("1. The communicator taps no when you expected yes.", st["body"]), blank_lines(2), P("2. The message does not make sense to you.", st["body"]), blank_lines(2), P("3. The communicator begins exploring buttons during a routine.", st["body"]), blank_lines(2)]
    S.append(PageBreak())

    # 16 reflection answers
    add_page(S, st, "Progress reflection and answer guidance", "Progress is not a vocabulary score. Look for more autonomy, more reasons to communicate, easier navigation, and better partner response.")
    S.append(info_table([
        ("Reflection", "Notes"),
        ("Messages the communicator initiated", ""), ("New communication reasons noticed", ""), ("Words or folders that were hard to find", ""), ("Vocabulary that should be personalized", ""), ("Access or voice settings to review", ""), ("What partners will model next", ""),
    ], st, widths=(2.75 * inch, 4.35 * inch)))
    S.append(P("Answer guidance for Practice 1", st["h2"]))
    S += bullets([
        "Pronouns: I, we, you, they, he, she.",
        "Possible play actions include play, go, look, come, give, make, get, put, open, turn, read, sit, walk, run, and others.",
        "Possible stopping or refusing words include no, stop, not, don't, all done, and different depending on intent.",
        "The connecting word in go to school is to.",
        "Question words include what, where, who, when, why, and how.",
        "Use the grammar doorway for endings and sentence tools.",
    ], st["small"])
    S.append(PageBreak())

    # 17 links
    add_page(S, st, "Useful links and notes", "These independent resources informed the teaching approach. Links are provided for further learning. My Buddy is not affiliated with these organizations or commercial AAC products.")
    S.append(info_table([
        ("Resource", "What to explore"),
        ("My Buddy training library", "quantumneuroshift.com/apps/my-buddy-training.html"),
        ("ASHA AAC Practice Portal", "asha.org/practice-portal/professional-issues/augmentative-and-alternative-communication"),
        ("ASHA AAC in Early Intervention", "asha.org/practice/early-intervention-provider-support/augmentative-and-alternative-communication-in-early-intervention"),
        ("AAC Language Lab", "aaclanguagelab.com/language-stages and /lesson-plans"),
        ("AssistiveWare Learn AAC", "assistiveware.com/learn-aac/learn-aac-guide"),
        ("AAC & Autism", "aacandautism.com/about/aac-things-to-know"),
    ], st, widths=(2.0 * inch, 5.1 * inch)))
    S.append(P("Implementation notes", st["h2"]))
    S += bullets([
        "My Buddy stores personalization on the local device, not on a My Buddy server.",
        "The app can work offline after it has been installed and loaded successfully as a PWA.",
        "Usage analytics were not added because the project prioritizes local privacy. Progress can be documented voluntarily on page 16.",
        "This workbook uses original text and diagrams. It does not reproduce proprietary symbol libraries or pages from another AAC product.",
    ], st["body"])
    S.append(P("Notes", st["h2"]))
    S.append(blank_lines(9))

    draw_page = lambda canvas, document: page_header(canvas, document, bw=bw)
    doc.build(S, onFirstPage=draw_page, onLaterPages=draw_page)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)
    build(OUT / "my-buddy-vocabulary-learning-workbook.pdf", bw=False)
    build(OUT / "my-buddy-vocabulary-learning-workbook-black-and-white.pdf", bw=True)


if __name__ == "__main__":
    main()
