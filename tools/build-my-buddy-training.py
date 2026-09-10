#!/usr/bin/env python3
"""Build the public My Buddy AAC training PDF set."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph,
    Spacer, Table, TableStyle,
)

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


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = doc.pagesize
    canvas.setFillColor(TEAL)
    canvas.rect(0, height - 0.16 * inch, width, 0.16 * inch, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(0.55 * inch, 0.34 * inch, "My Buddy AAC - free, private, and device-based")
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
        ("BACKGROUND", (0,0), (-1,-1), color), ("BOX", (0,0), (-1,-1), 1, GOLD),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ])


def bullet(text):
    return Paragraph("• " + text, STYLES["BodyMB"])


def checkbox(text):
    return Paragraph("[  ]  " + text, STYLES["CheckMB"])


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
    style = [("GRID", (0,0), (-1,-1), .5, colors.HexColor("#BBC4C7")),
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
    path = OUT / "my-buddy-caregiver-guide.pdf"
    story = title_block("Caregiver Getting Started Guide",
        "Set up a dependable communication system, teach it without pressure, and keep it ready offline.")
    story += [callout("The goal is not perfect tapping. The goal is for the communicator to be heard, believed, and given enough vocabulary to say something new."),
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
    path = OUT / "my-buddy-core-board-teaching-guide.pdf"
    story = title_block("Core Board Teaching Guide",
        "A visual map of the exact 12 x 7 Full View board, its color system, and repeatable paths for teaching language.", "EXACT BOARD TRAINING")
    story += [mini_board(), Spacer(1, 12),
              callout("Motor planning rule: a Level 1 word stays in the same physical location when its related word page opens. Teach the movement, not just the picture."),
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
              callout("Communication is successful when the message is understood - even if the sentence is incomplete, unconventional, or made with several methods.")]
    doc(path, "My Buddy AAC Core Board Teaching Guide").build(story)
    return path


def build_partner():
    path = OUT / "my-buddy-communication-partner-guide.pdf"
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
    path = OUT / "my-buddy-daily-practice-pack.pdf"
    story = title_block("Daily Practice Pack",
        "Seven short, printable activities for learning the exact My Buddy AAC board without turning communication into a test.")
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


if __name__ == "__main__":
    paths = [build_caregiver(), build_core(), build_partner(), build_practice()]
    for path in paths:
        print(path.relative_to(ROOT))
