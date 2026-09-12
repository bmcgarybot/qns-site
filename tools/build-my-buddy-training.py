#!/usr/bin/env python3
"""Build the public My Buddy AAC training PDF set."""

from io import BytesIO
from pathlib import Path
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph,
    Spacer, Table, TableStyle,
)
from pypdf import PdfReader, PdfWriter

try:
    from svglib.svglib import svg2rlg
except ImportError:
    svg2rlg = None

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)

INK = colors.HexColor("#17313A")
TEAL = colors.HexColor("#2A9D8F")
GOLD = colors.HexColor("#C9A54E")
PALE = colors.HexColor("#F4F1E8")
MUTED = colors.HexColor("#55656A")
YELLOW = colors.HexColor("#F6D55C")
GREEN = colors.HexColor("#7BC96F")
BLUE = colors.HexColor("#8EC5E8")
ORANGE = colors.HexColor("#F2A65A")
PINK = colors.HexColor("#E99AAA")
WHITE = colors.white
GRAY = colors.HexColor("#D9DEE0")
BW_MODE = False
BASE_PRINT_FILLS = (YELLOW, GREEN, BLUE, ORANGE, PINK, WHITE, GRAY)
BASE_PALE = PALE

STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle(name="TitleMB", parent=STYLES["Title"], fontName="Helvetica-Bold", fontSize=26, leading=29, textColor=INK, spaceAfter=12))
STYLES.add(ParagraphStyle(name="SubMB", parent=STYLES["Normal"], fontName="Helvetica", fontSize=12, leading=17, textColor=MUTED, spaceAfter=14))
STYLES.add(ParagraphStyle(name="H1MB", parent=STYLES["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=INK, spaceBefore=4, spaceAfter=10))
STYLES.add(ParagraphStyle(name="H2MB", parent=STYLES["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=TEAL, spaceBefore=8, spaceAfter=6))
STYLES.add(ParagraphStyle(name="BodyMB", parent=STYLES["BodyText"], fontName="Helvetica", fontSize=10, leading=14, textColor=INK, spaceAfter=7))
STYLES.add(ParagraphStyle(name="SmallMB", parent=STYLES["BodyText"], fontName="Helvetica", fontSize=8.4, leading=11, textColor=MUTED, spaceAfter=5))
STYLES.add(ParagraphStyle(name="CalloutMB", parent=STYLES["BodyText"], fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=INK, leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=8))
STYLES.add(ParagraphStyle(name="CellMB", parent=STYLES["Normal"], fontName="Helvetica-Bold", fontSize=7.2, leading=8, alignment=TA_CENTER, textColor=INK))
STYLES.add(ParagraphStyle(name="CheckMB", parent=STYLES["BodyText"], fontName="Helvetica", fontSize=10, leading=18, textColor=INK, leftIndent=4))
STYLES.add(ParagraphStyle(name="BoardCellMB", parent=STYLES["Normal"], fontName="Helvetica-Bold", fontSize=6.6, leading=7.2, alignment=TA_CENTER, textColor=INK))
STYLES.add(ParagraphStyle(name="RouteCellMB", parent=STYLES["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=9, alignment=TA_CENTER, textColor=INK))


def output_path(stem):
    suffix = "-black-and-white" if BW_MODE else ""
    return OUT / f"{stem}{suffix}.pdf"


def enable_bw_theme():
    """Use low-ink gray values that remain distinct without a color printer."""
    global BW_MODE, INK, TEAL, GOLD, PALE, MUTED
    global YELLOW, GREEN, BLUE, ORANGE, PINK, WHITE, GRAY
    BW_MODE = True
    INK = colors.black
    TEAL = colors.HexColor("#666666")
    GOLD = colors.HexColor("#888888")
    PALE = colors.HexColor("#F7F7F7")
    MUTED = colors.HexColor("#444444")
    YELLOW = colors.HexColor("#EEEEEE")
    GREEN = colors.HexColor("#D2D2D2")
    BLUE = colors.HexColor("#E2E2E2")
    ORANGE = colors.HexColor("#BDBDBD")
    PINK = colors.HexColor("#DADADA")
    WHITE = colors.white
    GRAY = colors.HexColor("#A8A8A8")
    for name in ("TitleMB", "H1MB", "BodyMB", "CalloutMB", "CellMB", "CheckMB", "BoardCellMB", "RouteCellMB"):
        STYLES[name].textColor = INK
    STYLES["H2MB"].textColor = INK
    STYLES["SubMB"].textColor = MUTED
    STYLES["SmallMB"].textColor = MUTED


def printable_fill(color):
    """Translate color-board fills to stable gray categories in print mode."""
    if not BW_MODE:
        return color
    replacements = (YELLOW, GREEN, BLUE, ORANGE, PINK, WHITE, GRAY)
    if color == BASE_PALE:
        return PALE
    for original, replacement in zip(BASE_PRINT_FILLS, replacements):
        if color == original:
            return replacement
    return color

HOME_BOARD = [
    [("I",YELLOW),("we",YELLOW),("want",GREEN),("like",GREEN),("go",GREEN),("help",GREEN),("is",GREEN),("on",WHITE),("in",WHITE),("up",WHITE),("feel",GREEN),("here",WHITE)],
    [("you",YELLOW),("they",YELLOW),("play",GREEN),("eat",GREEN),("drink",GREEN),("look",GREEN),("come",GREEN),("give",GREEN),("do",GREEN),("can",GREEN),("talk",GREEN),("again",WHITE)],
    [("he",YELLOW),("she",YELLOW),("make",GREEN),("get",GREEN),("put",GREEN),("open",GREEN),("turn",GREEN),("read",GREEN),("sit",GREEN),("walk",GREEN),("run",GREEN),("down",WHITE)],
    [("it",YELLOW),("sleep",GREEN),("need",GREEN),("that",WHITE),("love",GREEN),("happy",BLUE),("not",WHITE),("out",WHITE),("off",WHITE),("sad",BLUE),("and",WHITE),("the",WHITE)],
    [("yes",PINK),("more",BLUE),("good",BLUE),("big",BLUE),("hot",BLUE),("some",BLUE),("all done",PINK),("little",BLUE),("bad",BLUE),("no",PINK),("stop",PINK),("cold",BLUE)],
    [("my",YELLOW),("please",PINK),("thank you",PINK),("sorry",PINK),("what",WHITE),("where",WHITE),("who",WHITE),("when",WHITE),("why",WHITE),("how",WHITE),("to",WHITE),("grammar",GRAY)],
    [("CLEAR",GRAY),("food",GRAY),("people",GRAY),("feelings",GRAY),("places",GRAY),("animals",GRAY),("things",GRAY),("colors",GRAY),("body",GRAY),("clothes",GRAY),("my words",GRAY),("ABC",GRAY)],
]

SIMPLE_BOARD = [
    [("I",YELLOW),("you",YELLOW),("want",GREEN),("need",GREEN),("help",GREEN),("stop",PINK)],
    [("yes",PINK),("no",PINK),("more",BLUE),("all done",PINK),("please",PINK),("sorry",PINK)],
    [("go",GREEN),("come",GREEN),("eat",GREEN),("drink",GREEN),("to",WHITE),("bathroom",ORANGE)],
    [("happy",BLUE),("sad",BLUE),("angry",BLUE),("scared",BLUE),("tired",BLUE),("hurt",BLUE)],
    [("not",WHITE),("that",WHITE),("in",WHITE),("out",WHITE),("what",WHITE),("where",WHITE)],
    [("my",YELLOW),("people",GRAY),("food",GRAY),("feelings",GRAY),("places",GRAY),("body",GRAY)],
    [("home",ORANGE),("school",ORANGE),("things",GRAY),("clothes",GRAY),("animals",GRAY),("ABC",GRAY)],
    [("can",WHITE),("do",GREEN),("like",GREEN),("play",GREEN),("look",GREEN),("read",GREEN)],
]

ICON = {
    "I":"mulberry/I.svg","we":"mybuddy/we.svg","you":"mybuddy/you.svg","they":"mybuddy/they.svg","he":"mybuddy/he.svg","she":"mybuddy/she.svg","it":"mybuddy/it.svg","my":"mybuddy/my.svg",
    "want":"mulberry/want_,_to.svg","like":"mulberry/thumb.svg","go":"mulberry/go_,_to.svg","help":"mulberry/help_,_to.svg","is":"mybuddy/is.svg","on":"mulberry/on.svg","in":"mulberry/in.svg","up":"mulberry/up.svg","feel":"mybuddy/feel.svg","here":"mybuddy/here.svg",
    "play":"mulberry/play_,_to.svg","eat":"mulberry/eat_,_to.svg","drink":"mulberry/drink_,_to.svg","look":"mulberry/look_,_to.svg","come":"mulberry/come_,_to.svg","give":"mulberry/give_,_to.svg","do":"mybuddy/do.svg","can":"mybuddy/can.svg","talk":"mulberry/talk_1_,_to.svg","again":"mybuddy/again.svg",
    "make":"mulberry/make_,_to.svg","get":"mulberry/get_,_to.svg","put":"mulberry/put_,_to.svg","open":"mulberry/open_,_to.svg","turn":"mulberry/turn_,_to.svg","read":"mulberry/read_book_,_to.svg","sit":"mulberry/sit_,_to.svg","walk":"mulberry/walk_,_to.svg","run":"mulberry/run_,_to.svg","down":"mulberry/down.svg",
    "sleep":"mulberry/sleep_male_,_to.svg","need":"mybuddy/need.svg","that":"mybuddy/that.svg","love":"mulberry/heart.svg","happy":"mulberry/happy_man.svg","not":"mulberry/mistake_no_wrong.svg","out":"mulberry/out.svg","off":"mulberry/off.svg","sad":"mulberry/sad_man.svg",
    "yes":"mulberry/correct.svg","more":"mulberry/more.svg","good":"mulberry/good.svg","big":"mulberry/large.svg","hot":"mulberry/hot.svg","some":"mulberry/some.svg","all done":"mybuddy/all_done.svg","little":"mulberry/little.svg","bad":"mulberry/bad.svg","no":"mybuddy/no.svg","stop":"mybuddy/stop.svg","cold":"mulberry/snow.svg",
    "please":"mybuddy/please.svg","thank you":"mybuddy/thank_you.svg","sorry":"mybuddy/sorry.svg","what":"mulberry/what.svg","where":"mulberry/where.svg","who":"mulberry/who.svg","when":"mybuddy/when.svg","why":"mybuddy/why.svg","how":"mybuddy/how.svg","grammar":"mulberry/what.svg",
    "food":"mulberry/food.svg","people":"mulberry/family_2.svg","feelings":"mybuddy/feelings.svg","places":"mulberry/place_setting.svg","animals":"mulberry/paw.svg","things":"mulberry/place_setting.svg","colors":"mulberry/colour.svg","body":"mulberry/body_outline.svg","clothes":"mulberry/clothes_generic.svg","my words":"mulberry/talk_2_,_to.svg","ABC":"mulberry/computer_keyboard.svg",
    "bathroom":"mulberry/toilet.svg","home":"mulberry/house.svg","school":"mulberry/school.svg","angry":"mulberry/angry_man.svg","scared":"mulberry/afraid_man.svg","tired":"mulberry/yawn_,_to.svg","hurt":"mybuddy/hurt.svg",
    "water":"mulberry/water.svg","wash":"mulberry/wash_hands_,_to.svg","hands":"mulberry/right_hand.svg","shirt":"mulberry/shirt.svg","pants":"mulberry/trousers.svg","shoes":"mulberry/shoe_-_mans.svg","bed":"mulberry/single_bed.svg","blanket":"mulberry/blanket.svg","light":"mulberry/lamp.svg","wake":"mulberry/wake_up_,_to.svg","cereal":"mulberry/cereal.svg","milk":"mulberry/milk.svg","food":"mulberry/food.svg","jacket":"mulberry/jacket.svg","bus":"mulberry/bus.svg","teacher":"mulberry/teacher_1a.svg","book":"mulberry/book_end.svg","break":"mulberry/break_2.svg","outside":"mulberry/outside.svg","ball":"mulberry/ball.svg","TV":"mulberry/flatscreen_tv.svg","watch":"mulberry/watch.svg","sick":"mulberry/headache.svg","pain":"mybuddy/pain.svg","doctor":"mulberry/doctor_1a.svg","store":"mulberry/shop.svg","money":"mulberry/money.svg","calm":"mulberry/relax_,_to.svg","different":"mulberry/change_,_to.svg","mean":"mybuddy/mean.svg","poop":"mybuddy/poop.svg","pee":"mybuddy/pee.svg",
}


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = doc.pagesize
    canvas.setFillColor(TEAL)
    canvas.rect(0, height - 0.16 * inch, width, 0.16 * inch, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    footer = "My Buddy AAC - free, private, and device-based"
    if BW_MODE:
        footer += " - black and white edition"
    canvas.drawString(0.55 * inch, 0.34 * inch, footer)
    canvas.drawRightString(width - 0.55 * inch, 0.34 * inch, f"Page {doc.page}")
    canvas.restoreState()


def doc(path, title, pagesize=LETTER):
    d = BaseDocTemplate(str(path), pagesize=pagesize, title=title,
                        rightMargin=0.55 * inch, leftMargin=0.55 * inch,
                        topMargin=0.55 * inch, bottomMargin=0.58 * inch)
    frame = Frame(d.leftMargin, d.bottomMargin, d.width, d.height, id="main")
    d.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=header_footer)])
    return d


def title_block(title, subtitle, label="MY BUDDY AAC TRAINING"):
    if BW_MODE:
        label += " - BLACK AND WHITE EDITION"
    return [
        Paragraph(label, ParagraphStyle("Label", parent=STYLES["SmallMB"], fontName="Helvetica-Bold", textColor=GOLD, spaceAfter=8)),
        Paragraph(title, STYLES["TitleMB"]),
        Paragraph(subtitle, STYLES["SubMB"]),
        Table([["No account", "No ads", "No cloud profile", "Works offline after loading"]], colWidths=[1.3*inch, 1.05*inch, 1.45*inch, 2.25*inch], style=[
            ("BACKGROUND", (0,0), (-1,-1), INK), ("TEXTCOLOR", (0,0), (-1,-1), WHITE),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8.5),
            ("ALIGN", (0,0), (-1,-1), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ]), Spacer(1, 16)
    ]


def callout(text, color=PALE):
    return Table([[Paragraph(text, STYLES["CalloutMB"])]], colWidths=[7.05*inch], style=[
        ("BACKGROUND", (0,0), (-1,-1), printable_fill(color)), ("BOX", (0,0), (-1,-1), 1, GOLD),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ])


def bullet(text):
    return Paragraph("• " + text, STYLES["BodyMB"])


def checkbox(text):
    return Paragraph("[  ]  " + text, STYLES["CheckMB"])


def grayscale_drawing(node):
    """Convert symbol fills and strokes to grayscale for the print edition."""
    for attr in ("fillColor", "strokeColor"):
        value = getattr(node, attr, None)
        if value is not None and hasattr(value, "red"):
            level = 0.299 * value.red + 0.587 * value.green + 0.114 * value.blue
            setattr(node, attr, colors.Color(level, level, level, alpha=getattr(value, "alpha", 1)))
    children = getattr(node, "contents", None)
    if children:
        for child in children:
            grayscale_drawing(child)


def svg_icon(word, width=0.38*inch, height=0.31*inch):
    if svg2rlg is None:
        return Spacer(1, height)
    rel = ICON.get(word)
    path = ROOT / "apps" / "symbols" / rel if rel else None
    if not path or not path.exists():
        return Spacer(1, height)
    drawing = svg2rlg(str(path))
    if drawing is None or not drawing.width or not drawing.height:
        return Spacer(1, height)
    if BW_MODE:
        grayscale_drawing(drawing)
    scale = min(width / drawing.width, height / drawing.height)
    drawing.scale(scale, scale)
    drawing.width *= scale
    drawing.height *= scale
    return drawing


def symbol_cell(word, style="BoardCellMB", icon_h=0.29*inch):
    if word == "CLEAR":
        return [Spacer(1, icon_h), Paragraph(word, STYLES[style])]
    return [svg_icon(word, 0.43*inch, icon_h), Paragraph(word, STYLES[style])]


def board_table(board, col_width, row_height):
    data = [[symbol_cell(word) for word, _ in row] for row in board]
    table = Table(data, colWidths=[col_width]*len(board[0]), rowHeights=[row_height]*len(board))
    styling = [("GRID",(0,0),(-1,-1),.55,INK),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER"),("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]
    for r, row in enumerate(board):
        for c, (_, color) in enumerate(row):
            styling.append(("BACKGROUND",(c,r),(c,r),printable_fill(color)))
    table.setStyle(TableStyle(styling))
    return table


def color_key():
    entries = [(YELLOW, "Pronouns", "I, you, he, she, we, they"),
               (GREEN, "Actions", "want, go, make, help, feel"),
               (BLUE, "Descriptions", "happy, big, hot, little"),
               (ORANGE, "People & things", "school, food, people, objects"),
               (PINK, "Social words", "yes, no, please, stop, sorry"),
               (WHITE, "Grammar", "to, the, and, in, where, why"),
               (GRAY, "Folders", "food, people, places, body, ABC")]
    rows = []
    for color, name, examples in entries:
        rows.append(["", Paragraph(f"<b>{name}</b>", STYLES["BodyMB"]), Paragraph(examples, STYLES["SmallMB"])])
    t = Table(rows, colWidths=[0.32*inch, 1.6*inch, 4.85*inch], rowHeights=[0.34*inch]*len(rows))
    key_line = colors.HexColor("#BDBDBD") if BW_MODE else colors.HexColor("#BBC4C7")
    style = [("GRID", (0,0), (-1,-1), .5, key_line),
             ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
             ("LEFTPADDING", (1,0), (-1,-1), 8)]
    for i, (color, _, _) in enumerate(entries):
        style.append(("BACKGROUND", (0,i), (0,i), color))
    t.setStyle(TableStyle(style))
    return t


def mini_board():
    words = [
        [("I",YELLOW),("we",YELLOW),("want",GREEN),("like",GREEN),("go",GREEN),("help",GREEN),("is",GREEN),("on",WHITE),("in",WHITE),("up",WHITE),("feel",GREEN),("here",WHITE)],
        [("you",YELLOW),("they",YELLOW),("play",GREEN),("eat",GREEN),("drink",GREEN),("look",GREEN),("come",GREEN),("give",GREEN),("do",GREEN),("can",GREEN),("talk",GREEN),("again",WHITE)],
        [("he",YELLOW),("she",YELLOW),("make",GREEN),("get",GREEN),("put",GREEN),("open",GREEN),("turn",GREEN),("read",GREEN),("sit",GREEN),("walk",GREEN),("run",GREEN),("down",WHITE)],
        [("it",YELLOW),("sleep",GREEN),("need",GREEN),("that",WHITE),("love",GREEN),("happy",BLUE),("not",WHITE),("out",WHITE),("off",WHITE),("sad",BLUE),("and",WHITE),("the",WHITE)],
        [("yes",PINK),("more",BLUE),("good",BLUE),("big",BLUE),("hot",BLUE),("some",BLUE),("all done",PINK),("little",BLUE),("bad",BLUE),("no",PINK),("stop",PINK),("cold",BLUE)],
        [("my",YELLOW),("please",PINK),("thank you",PINK),("sorry",PINK),("what",WHITE),("where",WHITE),("who",WHITE),("when",WHITE),("why",WHITE),("how",WHITE),("to",WHITE),("grammar",GRAY)],
        [("CLEAR",GRAY),("food",GRAY),("people",GRAY),("feelings",GRAY),("places",GRAY),("animals",GRAY),("things",GRAY),("colors",GRAY),("body",GRAY),("clothes",GRAY),("my words",GRAY),("ABC",GRAY)],
    ]
    data = [[Paragraph(word, STYLES["CellMB"]) for word, _ in row] for row in words]
    table = Table(data, colWidths=[0.61*inch]*12, rowHeights=[0.43*inch]*7)
    styles = [("GRID", (0,0), (-1,-1), .55, INK), ("VALIGN", (0,0), (-1,-1), "MIDDLE")]
    for r, row in enumerate(words):
        for c, (_, color) in enumerate(row):
            styles.append(("BACKGROUND", (c,r), (c,r), color))
    table.setStyle(TableStyle(styles))
    return table


def build_caregiver():
    path = output_path("my-buddy-caregiver-guide")
    story = title_block("Caregiver Getting Started Guide",
        "Set up a dependable communication system, teach it without pressure, and keep it ready offline.")
    story += [callout("Give the communicator time, attention, and enough vocabulary to be heard, believed, and able to say something new."),
              Paragraph("1. Set up the device", STYLES["H1MB"])]
    for x in ["Open My Buddy while connected to the internet and wait for “Saved for offline use.”",
              "Add the page to the Home Screen if the browser offers that option.",
              "Open it once more while online after an update, then test it in airplane mode.",
              "Keep another communication method available for emergencies and device failure."]:
        story.append(checkbox(x))
    story += [Paragraph("2. Personalize safety information", STYLES["H1MB"]),
              Paragraph("Use Menu and enter only the information that is useful on this device. It stays in this browser on this device; it is not sent to a QNS account or server.", STYLES["BodyMB"])]
    for x in ["Name", "Phone number", "Address, city, and state", "School", "Emergency information that should be spoken"]:
        story.append(checkbox(x))
    story += [Paragraph("3. Know the three main areas", STYLES["H1MB"]),
              bullet("Sentence strip: selected words collect at the top. Delete removes one; Clear removes all; Speak reads the whole message."),
              bullet("Core board: high-use words stay in fixed positions so the movement can become familiar."),
              bullet("Right-side tools: Quick speaks saved urgent phrases; Find teaches a route; Menu contains setup and editing; History repeats recent words; Simple View makes targets larger."),
              PageBreak(), Paragraph("How to support communication", STYLES["H1MB"]),
              Paragraph("Model, wait, and respond", STYLES["H2MB"])]
    for x in ["Model on the board while you speak. The communicator does not have to copy you.",
              "Use one more word than the person currently uses: model “want drink” after a one-word message.",
              "Pause long enough for the person to plan and move. Silence is processing time.",
              "Honor clear messages, especially no, stop, hurt, help, and bathroom-related messages.",
              "Treat unexpected combinations as possible communication before correcting grammar."]:
        story.append(bullet(x))
    story += [callout("Avoid testing: “Show me ___” turns communication into a quiz. Instead, use the word naturally and let the person see where it is."),
              Paragraph("A 10-minute first session", STYLES["H2MB"]),
              Table([["Minute", "What to do"], ["0-2", "Choose a motivating activity and keep the board within reach."], ["2-5", "Model 3-5 useful words: want, more, help, stop, go."], ["5-8", "Build one sentence without requiring imitation."], ["8-10", "Let the communicator explore; respond to meaningful taps."]], colWidths=[0.8*inch,6.1*inch], style=[("BACKGROUND",(0,0),(-1,0),INK),("TEXTCOLOR",(0,0),(-1,0),WHITE),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),.5,GRAY),("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]),
              Paragraph("Editing and backups", STYLES["H2MB"]),
              bullet("Use Edit board to add personally meaningful words inside the page where they belong."),
              bullet("Use Back up words and settings after personalization and before changing devices."),
              bullet("Photos, custom words, and personal information are stored locally and can disappear if browser data is erased."),
              Paragraph("Before relying on it away from Wi-Fi", STYLES["H2MB"])]
    for x in ["Airplane-mode test passed", "Speech volume is audible", "Charging plan is ready", "Backup file is stored safely", "A second way to communicate is available"]:
        story.append(checkbox(x))
    doc(path, "My Buddy AAC Caregiver Getting Started Guide").build(story)
    return path


def build_core():
    path = output_path("my-buddy-core-board-teaching-guide")
    story = title_block("Core Board Teaching Guide",
        "A visual map of the exact 12 x 7 Full View board, its color system, and repeatable paths for teaching language.", "EXACT BOARD TRAINING")
    story += [mini_board(), Spacer(1, 12),
              callout("A Level 1 word repeats in the same physical location when its related word page opens. Repeating that path helps the movement become familiar."),
              Paragraph("Why the board is organized this way", STYLES["H1MB"]),
              bullet("Rows 1-4 hold pronouns, actions, grammar, and descriptions used across many situations."),
              bullet("Row 5 adds responses and describing words."),
              bullet("Row 6 holds social words, question words, to, and the grammar doorway."),
              bullet("Row 7 contains category doorways. The category is a path to vocabulary, not a spoken sentence."),
              PageBreak(), Paragraph("Color key", STYLES["H1MB"]), color_key(), Spacer(1, 12),
              Paragraph("Teach color as a clue, never as the answer", STYLES["H2MB"]),
              Paragraph("Say “actions are green, so look in the green area” while still naming and modeling the word. A communicator may use location, color, picture, print, or all four.", STYLES["BodyMB"]),
              Paragraph("Useful Level 1 paths", STYLES["H1MB"])]
    rows = [["Goal", "Model", "Why it matters"],
            ["Request", "I want more", "Pronoun + action + description"],
            ["Go somewhere", "I want to go to school", "Includes the grammar word to"],
            ["Reject", "I do not want that", "A complete refusal"],
            ["Ask", "where is my phone", "Question + grammar + possession"],
            ["Comment", "I like that", "Communication beyond requesting"],
            ["Health", "I feel sick and need help", "Describes and requests support"],
            ["Repair", "not that, I want this", "Corrects a misunderstanding"]]
    story += [Table(rows, colWidths=[1.15*inch,2.35*inch,3.45*inch], style=[("BACKGROUND",(0,0),(-1,0),INK),("TEXTCOLOR",(0,0),(-1,0),WHITE),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),.5,GRAY),("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),8.7),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]),
              PageBreak(), Paragraph("Modeling routes", STYLES["H1MB"]),
              Paragraph("Do not move words to make them easier. Repeat the same route until it becomes familiar.", STYLES["BodyMB"])]
    route_rows = [["Message", "Route to model"],
                  ["go to school", "Home: go -> Home: to -> Home: school / Places: school"],
                  ["I need bathroom", "Home: I -> Home: need -> Places/Body vocabulary: bathroom"],
                  ["open the door", "Home: open -> Home: the -> Things: door"],
                  ["my tummy hurts", "Home: my -> Body: tummy -> Health/Body: hurt"],
                  ["what happened", "Home: what -> action page: happened"],
                  ["I want a different game", "Home: I -> want -> Grammar: a -> Descriptions: different -> Things: game"]]
    story += [Table(route_rows, colWidths=[1.7*inch,5.2*inch], style=[("BACKGROUND",(0,0),(-1,0),TEAL),("TEXTCOLOR",(0,0),(-1,0),WHITE),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),.5,GRAY),("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),8.8),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]),
              Paragraph("Use Find as a teaching tool", STYLES["H2MB"]),
              bullet("Type a word and choose a result. The app highlights each press from Home in order."),
              bullet("Watch the path, then return Home and model the same path yourself."),
              bullet("If no exact word appears, add a useful personal word to the most meaningful folder."),
              Paragraph("Simple View", STYLES["H2MB"]),
              Paragraph("Simple View uses a 6 x 8 layout with larger targets for phones and smaller screens. It is a complete communication view, and repeated words keep stable Simple View positions.", STYLES["BodyMB"]),
              callout("Incomplete, unconventional, and multimodal messages still carry meaning. Respond to the message the communicator is trying to share.")]
    doc(path, "My Buddy AAC Core Board Teaching Guide").build(story)
    return path


def build_partner():
    path = output_path("my-buddy-communication-partner-guide")
    story = title_block("Communication Partner Guide",
        "A short training for family, school staff, respite providers, medical teams, and community partners.")
    story += [callout("Presume competence. The device is the person's voice, not a reward, lesson, or behavior-control tool."),
              Paragraph("The six partner habits", STYLES["H1MB"])]
    habits = [("1", "Keep access", "The board stays within reach, charged, and available across settings."),
              ("2", "Model", "Tap a few words while you speak naturally. No copying is required."),
              ("3", "Wait", "Pause after a model or question. Do not rush to fill the silence."),
              ("4", "Respond", "Treat a meaningful tap or combination as communication."),
              ("5", "Confirm", "If uncertain, reflect the message: “You said stop. Do you want this to stop?”"),
              ("6", "Repair together", "Offer Find, yes/no, gestures, writing, or choices without taking over the message.")]
    story.append(Table([[Paragraph(f"<b>{n}</b>", STYLES["H1MB"]), Paragraph(f"<b>{h}</b><br/>{d}", STYLES["BodyMB"])] for n,h,d in habits], colWidths=[0.5*inch,6.35*inch], style=[("BACKGROUND",(0,0),(0,-1),TEAL),("TEXTCOLOR",(0,0),(0,-1),WHITE),("GRID",(0,0),(-1,-1),.5,GRAY),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    story += [Paragraph("Say this / avoid this", STYLES["H1MB"]),
              Table([["Supportive", "Avoid"], ["“I’m listening.”", "“Use your words.”"], ["“Take your time.”", "Repeated prompts or countdowns"], ["“You said no. I hear you.”", "Ignoring no or stop"], ["Modeling “I want music”", "“Find want. Now find music.”"], ["“I’m not sure. Show me another way.”", "Guessing and moving on"]], colWidths=[3.45*inch,3.45*inch], style=[("BACKGROUND",(0,0),(0,0),TEAL),("BACKGROUND",(1,0),(1,0),INK),("TEXTCOLOR",(0,0),(-1,0),WHITE),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),.5,GRAY),("FONTSIZE",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]),
              PageBreak(), Paragraph("Safety, privacy, and dignity", STYLES["H1MB"])]
    for x in ["Never remove access as a consequence.",
              "Do not read private saved information aloud unless the communicator requests it or safety requires it.",
              "Honor stop, no, pain, bathroom, and help immediately enough to establish trust.",
              "Do not photograph, post, or share a person's communication without permission.",
              "Keep a low-tech backup available when charging, updating, or repairing the device."]:
        story.append(checkbox(x))
    story += [Paragraph("Partner practice", STYLES["H1MB"]),
              Paragraph("Practice these before supporting the communicator in a high-pressure moment.", STYLES["BodyMB"])]
    for x in ["Find and model: I want to go home", "Find and model: I do not like that", "Find and model: where is my phone", "Use Find to locate an unfamiliar word", "Switch between Full and Simple View", "Speak a Quick phrase", "Locate My Info without changing it"]:
        story.append(checkbox(x))
    story += [Paragraph("Team agreement", STYLES["H2MB"]),
              Paragraph("We will keep the system available, model without demanding, wait for communication, honor clear refusals, and report vocabulary needs to the person's primary support team.", STYLES["BodyMB"]),
              Spacer(1, 18),
              Table([["Partner name", "Role", "Date"], ["\n\n", "", ""]], colWidths=[3*inch,2.2*inch,1.7*inch], style=[("BACKGROUND",(0,0),(-1,0),PALE),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),.6,GRAY),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]),
              Spacer(1, 16), callout("If the board does not speak, remain calm. Preserve the person's message using pointing, writing, gestures, or a backup board while the device is checked.")]
    doc(path, "My Buddy AAC Communication Partner Guide").build(story)
    return path


def build_practice():
    path = output_path("my-buddy-daily-practice-pack")
    story = title_block("Daily Practice Pack",
        "Seven short printable activities for learning the exact My Buddy AAC board through ordinary communication.")
    story += [callout("Model each activity first. Participation can be watching, pointing, tapping, speaking, signing, or choosing not to continue."),
              Paragraph("Weekly plan", STYLES["H1MB"])]
    rows = [["Day", "Focus", "Model"], ["1", "Requests", "I want more"], ["2", "Actions", "we go / you help / I make"], ["3", "Comments", "I like that / it is good"], ["4", "Refusal", "no / stop / I do not want that"], ["5", "Questions", "where is my ___ / what is that"], ["6", "Feelings & health", "I feel ___ / I need help"], ["7", "Conversation", "Mix comments, questions, and repair"]]
    story += [Table(rows, colWidths=[0.55*inch,1.8*inch,4.6*inch], style=[("BACKGROUND",(0,0),(-1,0),INK),("TEXTCOLOR",(0,0),(-1,0),WHITE),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),.5,GRAY),("FONTSIZE",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]), PageBreak()]
    activities = [
        ("Day 1 - Request without quizzing", ["Place two enjoyable items in view.", "Model “I want” plus one item.", "Wait. Accept any clear selection or refusal.", "Model “more” or “all done” when it naturally fits."], ["I want more", "I want that", "all done"]),
        ("Day 2 - Action hunt", ["During real activities, model one green action word.", "Use go, help, make, open, put, or play.", "Repeat the same location instead of moving the word."], ["we go", "you help", "I make it"]),
        ("Day 3 - Comment, do not only request", ["Notice something interesting together.", "Model like, good, bad, funny, hot, or cold.", "Respond to the comment instead of asking a question."], ["I like that", "it is good", "that is funny"]),
        ("Day 4 - Powerful refusal", ["Create safe opportunities to decline.", "Model no, stop, not, and all done.", "Honor the message so the words remain trustworthy."], ["no", "stop that", "I do not want that"]),
        ("Day 5 - Ask a real question", ["Hide or misplace a familiar item.", "Model where + is + my + item.", "Use Find if the item word is unfamiliar."], ["where is my phone", "what is that", "who is there"]),
        ("Day 6 - Feelings and help", ["Model a true feeling or body state.", "Pair feel with a description.", "Show how and when to ask for help."], ["I feel tired", "I feel sick", "I need help"]),
        ("Day 7 - Conversation and repair", ["Make a comment, then wait for a response.", "If misunderstood, model not that or different.", "Let the communicator change or abandon the message."], ["not that", "I want different", "I mean this"]),
    ]
    for idx, (heading, steps, models) in enumerate(activities):
        story += [Paragraph(heading, STYLES["H1MB"])]
        for step in steps:
            story.append(checkbox(step))
        story += [Spacer(1, 5), Table([[Paragraph("MODEL", STYLES["SmallMB"])] + [Paragraph(m, STYLES["BodyMB"]) for m in models]], colWidths=[0.7*inch,2.05*inch,2.05*inch,2.05*inch], style=[("BACKGROUND",(0,0),(0,0),GOLD),("BACKGROUND",(1,0),(-1,0),PALE),("BOX",(0,0),(-1,-1),.7,GOLD),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]), Spacer(1, 12),
                  Paragraph("What the communicator chose to say:", STYLES["SmallMB"]),
                  Table([[""], [""]], colWidths=[6.85*inch], rowHeights=[0.34*inch,0.34*inch], style=[("LINEBELOW",(0,0),(-1,-1),.5,GRAY)]),
                  Paragraph("Vocabulary we should add or practice:", STYLES["SmallMB"]),
                  Table([[""], [""]], colWidths=[6.85*inch], rowHeights=[0.34*inch,0.34*inch], style=[("LINEBELOW",(0,0),(-1,-1),.5,GRAY)])]
        if idx < len(activities)-1:
            story.append(PageBreak())
    doc(path, "My Buddy AAC Daily Practice Pack").build(story)
    return path


def landscape_title(title, subtitle):
    return [
        Paragraph("MY BUDDY AAC PRINTABLE" + (" - BLACK AND WHITE EDITION" if BW_MODE else ""), ParagraphStyle("LandLabel", parent=STYLES["SmallMB"], fontName="Helvetica-Bold", textColor=GOLD, spaceAfter=4)),
        Paragraph(title, ParagraphStyle("LandTitle", parent=STYLES["TitleMB"], fontSize=21, leading=23, spaceAfter=4)),
        Paragraph(subtitle, ParagraphStyle("LandSub", parent=STYLES["SubMB"], fontSize=9.5, leading=12, spaceAfter=8)),
    ]


def build_backup_board():
    if svg2rlg is None:
        raise RuntimeError("Install tools/requirements-my-buddy-training.txt before building the symbol boards")
    path = output_path("my-buddy-low-tech-backup-board")
    print_note = "Print in black and white" if BW_MODE else "Print in color"
    folder_note = "Darker folder cells open a vocabulary group on the app." if BW_MODE else "Gray cells open a vocabulary group on the app."
    story = landscape_title("Full View Backup Board", print_note + " and keep it with the device. The cell order matches the English 12 x 7 Full View board.")
    story += [Table([[Paragraph("MESSAGE", STYLES["SmallMB"]), ""]], colWidths=[0.75*inch,8.95*inch], rowHeights=[0.42*inch], style=[("BACKGROUND",(0,0),(0,0),INK),("TEXTCOLOR",(0,0),(0,0),WHITE),("BOX",(0,0),(-1,-1),.8,INK),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),8)]), Spacer(1,6), board_table(HOME_BOARD,0.81*inch,0.65*inch), Spacer(1,5), Paragraph("Point to words in order. A partner can repeat the message aloud and write it in the strip. " + folder_note, STYLES["SmallMB"]), PageBreak()]
    story += landscape_title("Simple View Backup Board", "Larger targets for phones, small screens, travel, and times when a reduced display is easier to access.")
    story += [Table([[Paragraph("MESSAGE", STYLES["SmallMB"]), ""]], colWidths=[0.75*inch,8.95*inch], rowHeights=[0.42*inch], style=[("BACKGROUND",(0,0),(0,0),INK),("TEXTCOLOR",(0,0),(0,0),WHITE),("BOX",(0,0),(-1,-1),.8,INK),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),8)]), Spacer(1,6), board_table(SIMPLE_BOARD,1.45*inch,0.66*inch), Spacer(1,5), Paragraph("Keep this board available during charging, updates, travel, and device problems. Continue to honor pointing, gestures, signs, speech, and writing.", STYLES["SmallMB"])]
    doc(path, "My Buddy AAC Low-Tech Backup Board", landscape(LETTER)).build(story)
    return path


HOME_WORDS = {word for row in HOME_BOARD for word, _ in row}
ANCHOR_WORDS = {"I","we","you","they","he","she","it","want","like","go","help","feel","play","eat","drink","look","come","give","do","talk","make","get","put","open","turn","read","sit","walk","run","sleep","need","love"}
SOCIAL_WORDS = {"yes","no","stop","please","sorry","thank you","all done"}
GRAMMAR_WORDS = {"is","on","in","up","here","again","that","not","out","off","and","the","what","where","who","when","why","how","to","am","are","me","this","different"}
DESCRIPTION_WORDS = {"more","good","big","hot","some","little","bad","cold","happy","sad","angry","scared","tired","hurt","sick","ready","quiet","calm"}
FOLDER_FOR = {
    "bathroom":"Places","home":"Places","school":"Places","store":"Places","outside":"Places",
    "water":"Food","cereal":"Food","milk":"Food","food":"Food",
    "shirt":"Clothes","pants":"Clothes","shoes":"Clothes","jacket":"Clothes",
    "hands":"Body","poop":"Body","pee":"Body","pain":"Body","medicine":"Body","tummy":"Body",
    "blanket":"Things","light":"Things","ball":"Things","TV":"TV and media","book":"School words","paper":"School words","teacher":"People","money":"Things","break":"School words",
    "sick":"Feelings","angry":"Feelings","tired":"Feelings","calm":"Feelings","quiet":"describing word page",
}


def word_color(word):
    if word in {"I","we","you","they","he","she","it","my","me"}: return YELLOW
    if word in SOCIAL_WORDS: return PINK
    if word in GRAMMAR_WORDS: return WHITE
    if word in DESCRIPTION_WORDS: return BLUE
    if word in HOME_WORDS and word not in {"CLEAR","grammar"}: return GREEN
    return ORANGE


def sentence_tokens(text):
    raw = text.split()
    out = []
    i = 0
    while i < len(raw):
        pair = " ".join(raw[i:i+2])
        if pair in {"all done","thank you"}:
            out.append(pair); i += 2
        else:
            out.append(raw[i]); i += 1
    return out


def route_for(word):
    if word == "me": return "Home I -> me"
    if word in ANCHOR_WORDS: return f"Home {word} -> {word}"
    if word in HOME_WORDS: return f"Home {word}"
    if word in FOLDER_FOR: return f"Home {FOLDER_FOR[word]} -> {word}"
    if word in GRAMMAR_WORDS: return f"Home Grammar -> {word}"
    return f"Use Find for {word}"


def route_strip(text):
    tokens = sentence_tokens(text)
    cells = [symbol_cell(w, "RouteCellMB", 0.31*inch) for w in tokens]
    widths = [min(1.18, max(.72, .12*len(w)+.5))*inch for w in tokens]
    strip = Table([cells], colWidths=widths, rowHeights=[0.61*inch])
    styling = [("GRID",(0,0),(-1,-1),.55,INK),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER"),("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]
    for i, word in enumerate(tokens): styling.append(("BACKGROUND",(i,0),(i,0),word_color(word)))
    strip.setStyle(TableStyle(styling))
    route = "  |  ".join(route_for(w) for w in tokens)
    return KeepTogether([strip, Spacer(1,3), Paragraph(route, STYLES["SmallMB"]), Spacer(1,9)])


ROUTINES = [
    ("Bathroom", "Keep the board within reach before urgency starts.", ["I need bathroom","I need to pee","I need to poop","help me please"]),
    ("Wash hands", "Model the words during the real sequence at the sink.", ["turn on water","wash my hands","help me wash","turn off water"]),
    ("Get dressed", "Offer choices and leave time for refusal or a request for help.", ["I need shirt","put on pants","where are my shoes","I need help"]),
    ("Bedtime", "Use these words as choices and comments during the routine.", ["I feel tired","I want my blanket","turn off light","I need bathroom"]),
    ("Morning", "Keep language available from waking through leaving home.", ["I need bathroom","put on clothes","I want cereal","I am ready"]),
    ("Breakfast", "Pause naturally so there is room to request, comment, or finish.", ["I want cereal","I want milk","more please","all done"]),
    ("Make food", "Model action words while preparing a real snack or meal.", ["I want to make food","put it in","help me open it","it is hot"]),
    ("Leave home", "Post this near the door and model it during the actual routine.", ["put on shoes","I need my jacket","go to car","I am ready"]),
    ("Go to school", "Practice the route during calm moments and use it again on school days.", ["I want to go to school","where is my teacher","I need a break","I need help"]),
    ("In class", "Make room for questions, help, breaks, and finishing.", ["I want my book","I need paper","can you help","I am all done"]),
    ("Playground", "Use the board for joining, directing, stopping, and leaving.", ["I want to play","go outside","I want ball","stop please"]),
    ("Living room", "Model control of shared activities such as television and music.", ["I want to watch TV","turn it on","turn it up","turn it off"]),
    ("Health and pain", "Respond promptly to health messages and confirm the body area.", ["I feel sick","my tummy hurts","I need medicine","I want doctor"]),
    ("Store and community", "Use comments and choices during real trips.", ["I want to go to store","I want that","how much money","all done"]),
    ("Big feelings", "Keep demands low and allow the communicator to use any reliable method.", ["I feel angry","I need a break","I want quiet","help me calm"]),
    ("Fix a misunderstanding", "Pause and give the communicator time to change the message.", ["no not that","I mean different","I want this","please wait"]),
]


def build_routines():
    path = output_path("my-buddy-routine-teaching-boards")
    story = landscape_title("Everyday Routine Teaching Boards", "Sixteen activity pages for modeling the exact My Buddy word paths during real life.")
    story += [Paragraph("Choose one routine that is already happening. Model one useful message, pause, and respond to whatever the communicator does next. Pointing, tapping, speech, signs, gestures, and looking toward a choice can all carry meaning.", STYLES["BodyMB"]), Spacer(1,8), color_key(), Spacer(1,12), Paragraph("Included routines", STYLES["H1MB"])]
    rows = []
    for i in range(0, len(ROUTINES), 2):
        left = [str(i+1), ROUTINES[i][0]]
        right = [str(i+2), ROUTINES[i+1][0]] if i+1 < len(ROUTINES) else ["", ""]
        rows.append(left + right)
    story += [Table(rows, colWidths=[0.4*inch,4.2*inch,0.4*inch,4.2*inch], style=[("GRID",(0,0),(-1,-1),.4,GRAY),("BACKGROUND",(0,0),(0,-1),TEAL),("BACKGROUND",(2,0),(2,-1),TEAL),("TEXTCOLOR",(0,0),(0,-1),WHITE),("TEXTCOLOR",(2,0),(2,-1),WHITE),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]), PageBreak()]
    for index, (title, note, messages) in enumerate(ROUTINES):
        story += landscape_title(title, note)
        story += [Paragraph("Model these paths", STYLES["H2MB"])]
        for message in messages: story.append(route_strip(message))
        story += [Paragraph("Words the communicator wanted during this routine:", STYLES["SmallMB"]), Table([[""]], colWidths=[9.7*inch], rowHeights=[0.48*inch], style=[("BOX",(0,0),(-1,-1),.6,GRAY)])]
        if index < len(ROUTINES)-1: story.append(PageBreak())
    doc(path, "My Buddy AAC Everyday Routine Teaching Boards", landscape(LETTER)).build(story)
    return path


def kit_page(title, subtitle="", label="MY BUDDY AAC COMPLETE TRAINING KIT", lines=None, pagesize=LETTER):
    """Create one polished portrait or landscape binder page in memory."""
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=pagesize)
    width, height = pagesize
    if BW_MODE:
        label += " - BLACK AND WHITE EDITION"
    c.setFillColor(WHITE if BW_MODE else INK)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#E2E2E2") if BW_MODE else TEAL)
    c.rect(0, height - 0.18 * inch, width, 0.18 * inch, fill=1, stroke=0)
    c.setFillColor(INK if BW_MODE else GOLD)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.72 * inch, height - 0.92 * inch, label)
    c.setFillColor(INK if BW_MODE else WHITE)
    c.setFont("Helvetica-Bold", 27)
    c.drawString(0.72 * inch, height - 1.45 * inch, title)
    if subtitle:
        c.setFillColor(MUTED if BW_MODE else colors.HexColor("#D5E0E2"))
        c.setFont("Helvetica", 11)
        text = c.beginText(0.72 * inch, height - 1.78 * inch)
        text.setLeading(15)
        for line in subtitle.split("\n"):
            text.textLine(line)
        c.drawText(text)
    if lines:
        y = height - 2.45 * inch
        for heading, detail in lines:
            c.setFillColor(colors.HexColor("#D0D0D0") if BW_MODE else TEAL)
            c.roundRect(0.72 * inch, y - 0.07 * inch, 0.31 * inch, 0.31 * inch, 4, fill=1, stroke=0)
            c.setFillColor(INK if BW_MODE else WHITE)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1.18 * inch, y + 0.05 * inch, heading)
            c.setFillColor(MUTED if BW_MODE else colors.HexColor("#CAD5D7"))
            c.setFont("Helvetica", 9.2)
            c.drawString(1.18 * inch, y - 0.13 * inch, detail)
            y -= 0.7 * inch
    c.setFillColor(MUTED if BW_MODE else colors.HexColor("#AFC1C5"))
    c.setFont("Helvetica", 8)
    c.drawString(0.72 * inch, 0.42 * inch, "Free to print and share for My Buddy AAC training")
    c.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]


def kit_contents_page(section_rows, index_page):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=LETTER)
    width, height = LETTER
    c.setFillColor(PALE); c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(TEAL); c.rect(0, height - 0.18*inch, width, 0.18*inch, fill=1, stroke=0)
    edition = " - BLACK AND WHITE EDITION" if BW_MODE else ""
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 9); c.drawString(.72*inch, height-.78*inch, "MY BUDDY AAC COMPLETE TRAINING KIT" + edition)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 27); c.drawString(.72*inch, height-1.25*inch, "Table of Contents")
    y = height - 1.86*inch
    for number, title, detail, start, end in section_rows:
        c.setFillColor(TEAL); c.circle(.91*inch, y+.04*inch, .18*inch, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 10); c.drawCentredString(.91*inch, y, str(number))
        c.setFillColor(INK); c.setFont("Helvetica-Bold", 12); c.drawString(1.28*inch, y+.02*inch, title)
        c.setFillColor(MUTED); c.setFont("Helvetica", 8.5); c.drawString(1.28*inch, y-.2*inch, detail)
        c.setFillColor(INK); c.setFont("Helvetica-Bold", 10); c.drawRightString(width-.72*inch, y, str(start) if start == end else f"{start}-{end}")
        c.setStrokeColor(GRAY); c.line(1.28*inch, y-.31*inch, width-.72*inch, y-.31*inch)
        y -= .78*inch
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 12); c.drawString(1.28*inch, y, "Alphabetical index")
    c.drawRightString(width-.72*inch, y, str(index_page))
    c.setFillColor(MUTED); c.setFont("Helvetica", 8.5); c.drawString(1.28*inch, y-.2*inch, "Topics, routines, communication skills, and setup tasks")
    c.setFont("Helvetica", 8); c.drawString(.72*inch, .42*inch, "Page numbers refer to this complete kit.")
    c.save(); packet.seek(0)
    return PdfReader(packet).pages[0]


def kit_index_page(entries):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=LETTER)
    width, height = LETTER
    c.setFillColor(PALE); c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(TEAL); c.rect(0, height-.18*inch, width, .18*inch, fill=1, stroke=0)
    edition = " - BLACK AND WHITE EDITION" if BW_MODE else ""
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 9); c.drawString(.72*inch, height-.78*inch, "MY BUDDY AAC COMPLETE TRAINING KIT" + edition)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 27); c.drawString(.72*inch, height-1.25*inch, "Index")
    half = (len(entries) + 1) // 2
    for col, group in enumerate((entries[:half], entries[half:])):
        x = .72*inch + col*3.65*inch
        y = height - 1.75*inch
        for term, page in group:
            c.setFillColor(INK); c.setFont("Helvetica", 9.2); c.drawString(x, y, term)
            c.setFillColor(MUTED); c.setFont("Helvetica-Bold", 9.2); c.drawRightString(x+3.08*inch, y, str(page))
            c.setStrokeColor(colors.HexColor("#D5D5D5") if BW_MODE else colors.HexColor("#D5DCDD")); c.line(x, y-.07*inch, x+3.08*inch, y-.07*inch)
            y -= .28*inch
    c.setFillColor(MUTED); c.setFont("Helvetica", 8); c.drawString(.72*inch, .42*inch, "Use Find inside the app when a word is not shown in this printed index.")
    c.save(); packet.seek(0)
    return PdfReader(packet).pages[0]


def add_kit_number(page, number):
    packet = BytesIO()
    width = float(page.mediabox.width); height = float(page.mediabox.height)
    c = canvas.Canvas(packet, pagesize=(width, height))
    c.setFillColor(INK); c.roundRect(width-62, height-25, 48, 16, 4, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(width-38, height-20, f"KIT {number}")
    c.save(); packet.seek(0)
    page.merge_page(PdfReader(packet).pages[0])


def build_complete_kit(section_paths):
    """Combine every printable into a tabbed, indexed binder-ready PDF."""
    path = output_path("my-buddy-complete-training-kit")
    sections = [
        ("Caregiver Getting Started", "Device setup, offline checks, personalization, and first-session support."),
        ("Core Board Teaching Guide", "Exact board map, color key, motor planning, Find, and modeling routes."),
        ("Communication Partner Guide", "Access, modeling, wait time, dignity, privacy, and message repair."),
        ("Seven-Day Practice Pack", "One week of short communication activities and reflection pages."),
        ("Low-Tech Backup Boards", "Printable Full View and Simple View boards for outages and travel."),
        ("Everyday Routine Teaching Boards", "Sixteen real-life routines with messages and exact board paths."),
    ]
    counts = [len(PdfReader(str(p)).pages) for p in section_paths]
    starts, cursor = [], 4
    for count in counts:
        starts.append(cursor); cursor += 1 + count
    index_page = cursor
    rows = [(i+1, title, detail, starts[i], starts[i]+counts[i]) for i,(title,detail) in enumerate(sections)]

    writer = PdfWriter()
    cover = kit_page("Complete Training Kit", "A binder-ready guide for setup, teaching, daily practice,\nlow-tech backup, and real-life communication routines.")
    writer.add_page(cover)
    writer.add_page(kit_contents_page(rows, index_page))
    writer.add_page(kit_page("How to Use This Binder", "Start small, use the board during real life, and return to the sections you need.", lines=[
        ("1. Prepare", "Complete the device and offline checklist in Section 1."),
        ("2. Learn the layout", "Use the exact board map and color key in Section 2."),
        ("3. Train partners", "Share the short partner guide with family, school, and care teams."),
        ("4. Practice", "Choose one seven-day activity or one routine that is already happening."),
        ("5. Keep a backup", "Print both low-tech boards and store them with the device."),
        ("6. Record needs", "Write down vocabulary that should be added or practiced."),
    ]))

    for i, ((title, detail), source_path) in enumerate(zip(sections, section_paths)):
        divider = kit_page(f"Section {i+1}", title + "\n" + detail, label="MY BUDDY AAC BINDER DIVIDER")
        writer.add_page(divider)
        for page in PdfReader(str(source_path)).pages:
            writer.add_page(page)

    index_entries = sorted([
        ("AAC partner habits", starts[2]), ("Access to the board", starts[2]), ("Airplane-mode test", starts[0]),
        ("Backup and restore", starts[0]), ("Bathroom routine", starts[5]), ("Bedtime", starts[5]),
        ("Big feelings", starts[5]), ("Board colors", starts[1]), ("Board map - Full View", starts[1]),
        ("Board map - Simple View", starts[4]), ("Caregiver setup", starts[0]), ("Charging plan", starts[0]),
        ("Communication repair", starts[2]), ("Core words", starts[1]), ("Daily practice", starts[3]),
        ("Device personalization", starts[0]), ("Dignity", starts[2]), ("Dressing", starts[5]),
        ("Editing vocabulary", starts[0]), ("Emergency backup", starts[4]), ("Find tool", starts[1]),
        ("Food and meals", starts[5]), ("Getting ready", starts[5]), ("Health and pain", starts[5]),
        ("Home Screen installation", starts[0]), ("Honoring refusal", starts[2]), ("Kitchen", starts[5]),
        ("Language modeling", starts[1]), ("Living room", starts[5]), ("Low-tech boards", starts[4]),
        ("Message repair", starts[5]), ("Motor planning", starts[1]), ("Partner agreement", starts[2]),
        ("Personal safety information", starts[0]), ("Playground", starts[5]), ("Privacy", starts[2]),
        ("Quick phrases", starts[0]), ("Requests", starts[3]), ("School", starts[5]),
        ("Sentence strip", starts[0]), ("Simple View", starts[1]), ("Store and community", starts[5]),
        ("Teaching without testing", starts[0]), ("Voice and speech", starts[0]), ("Wait time", starts[2]),
        ("Washing hands", starts[5]), ("Weekly practice plan", starts[3]), ("Word routes", starts[1]),
    ], key=lambda item: item[0].lower())
    writer.add_page(kit_index_page(index_entries))

    for number, page in enumerate(writer.pages, start=1):
        add_kit_number(page, number)
    writer.add_metadata({"/Title":"My Buddy AAC Complete Training Kit", "/Author":"BMC Luminary Ventures LLC", "/Subject":"Binder-ready My Buddy AAC setup and training materials"})
    with open(path, "wb") as output:
        writer.write(output)
    return path


if __name__ == "__main__":
    if "--black-and-white" in sys.argv:
        enable_bw_theme()
    if "--kit-only" in sys.argv:
        paths = [
            output_path("my-buddy-caregiver-guide"),
            output_path("my-buddy-core-board-teaching-guide"),
            output_path("my-buddy-communication-partner-guide"),
            output_path("my-buddy-daily-practice-pack"),
            output_path("my-buddy-low-tech-backup-board"),
            output_path("my-buddy-routine-teaching-boards"),
        ]
    else:
        paths = [build_caregiver(), build_core(), build_partner(), build_practice(), build_backup_board(), build_routines()]
    paths.append(build_complete_kit(paths))
    for path in paths:
        print(path.relative_to(ROOT))
