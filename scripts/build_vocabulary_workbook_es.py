from pathlib import Path
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_vocabulary_workbook as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"

WORDS = [
    ("yo", "pronoun"), ("nosotros", "pronoun"), ("querer", "verb"), ("gustar", "verb"), ("ir", "verb"), ("ayudar", "verb"), ("ser", "verb"), ("en", "grammar"), ("dentro", "grammar"), ("arriba", "grammar"), ("sentir", "verb"), ("aquí", "grammar"),
    ("tú", "pronoun"), ("ellos", "pronoun"), ("jugar", "verb"), ("comer", "verb"), ("beber", "verb"), ("mirar", "verb"), ("venir", "verb"), ("dar", "verb"), ("hacer", "verb"), ("poder", "verb"), ("hablar", "verb"), ("otra vez", "grammar"),
    ("él", "pronoun"), ("ella", "pronoun"), ("crear", "verb"), ("conseguir", "verb"), ("poner", "verb"), ("abrir", "verb"), ("girar", "verb"), ("leer", "verb"), ("sentarse", "verb"), ("caminar", "verb"), ("correr", "verb"), ("abajo", "grammar"),
    ("eso", "pronoun"), ("dormir", "verb"), ("necesitar", "verb"), ("esto", "grammar"), ("amar", "verb"), ("feliz", "adjective"), ("nunca", "grammar"), ("fuera", "grammar"), ("estar", "verb"), ("triste", "adjective"), ("y", "grammar"), ("el", "grammar"),
    ("sí", "social"), ("más", "adjective"), ("bueno", "adjective"), ("grande", "adjective"), ("caliente", "adjective"), ("algo", "adjective"), ("terminé", "social"), ("pequeño", "adjective"), ("malo", "adjective"), ("no", "social"), ("parar", "social"), ("frío", "adjective"),
    ("mi", "pronoun"), ("por favor", "social"), ("gracias", "social"), ("perdón", "social"), ("qué", "grammar"), ("dónde", "grammar"), ("quién", "grammar"), ("cuándo", "grammar"), ("por qué", "grammar"), ("cómo", "grammar"), ("a", "grammar"), ("gramática", "folder"),
    ("BORRAR", "folder"), ("comida", "folder"), ("gente", "folder"), ("sentimientos", "folder"), ("lugares", "folder"), ("animales", "folder"), ("cosas", "folder"), ("colores", "folder"), ("cuerpo", "folder"), ("ropa", "folder"), ("mis palabras", "folder"), ("ABC", "folder"),
]

LABELS = {"verb": "acción", "adjective": "descripción", "noun": "sustantivo", "pronoun": "pronombre", "social": "social", "grammar": "gramática", "folder": "carpeta"}


def P(text, style):
    return Paragraph(text, style)


def viñetas(items, st):
    return [P("• " + item, st["body"]) for item in items]


def mapa(st, bw=False):
    fills = {"verb": base.GREEN, "adjective": base.BLUE, "noun": base.ORANGE, "pronoun": base.YELLOW, "social": base.PINK, "folder": base.GRAY, "grammar": base.WHITE}
    shades = {"verb": .90, "adjective": .83, "noun": .76, "pronoun": .94, "social": .86, "folder": .70, "grammar": 1.0}
    data = []
    for row in range(7):
        cells = []
        for col in range(12):
            word, kind = WORDS[row * 12 + col]
            cells.append(P(f"{word}<br/><font size='4'>{LABELS[kind].upper()}</font>", st["cell"]))
        data.append(cells)
    table = Table(data, colWidths=[.61 * inch] * 12, rowHeights=[.62 * inch] * 7)
    commands = [("GRID", (0, 0), (-1, -1), .55, st["_ink"]), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
    for row in range(7):
        for col in range(12):
            kind = WORDS[row * 12 + col][1]
            fill = colors.Color(shades[kind], shades[kind], shades[kind]) if bw else fills[kind]
            commands.append(("BACKGROUND", (col, row), (col, row), fill))
    table.setStyle(TableStyle(commands))
    return table


def clave(st, bw=False):
    rows = [
        ("Verde", "Acciones y verbos", "ir, ayudar, hacer, abrir"),
        ("Azul", "Descripciones", "grande, pequeño, caliente, diferente"),
        ("Naranja", "Personas, lugares y cosas", "escuela, maestra, comida"),
        ("Amarillo", "Pronombres", "yo, tú, él, ella, nosotros, ellos"),
        ("Blanco", "Gramática y ubicación", "a, en, el, nunca, aquí"),
        ("Rosa", "Palabras sociales", "sí, no, gracias, perdón"),
        ("Gris", "Carpetas", "gente, lugares, comida, cuerpo"),
    ]
    data = [[P("Color", st["table_bold"]), P("Función", st["table_bold"]), P("Ejemplos", st["table_bold"])]]
    for a, b, c in rows:
        data.append([P(a, st["table_bold"]), P(b, st["table"]), P(c, st["table"])])
    t = Table(data, colWidths=[1.05 * inch, 2.4 * inch, 3.7 * inch])
    fills = [base.GREEN, base.BLUE, base.ORANGE, base.YELLOW, base.WHITE, base.PINK, base.GRAY]
    cmds = [("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#AAB5B8")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, 0), st["_ink"]), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]
    for r in range(1, 8):
        v = .97 - (r - 1) * .045
        cmds.append(("BACKGROUND", (0, r), (0, r), colors.Color(v, v, v) if bw else fills[r - 1]))
    t.setStyle(TableStyle(cmds))
    return t


def tabla(rows, st, widths):
    return base.info_table(rows, st, widths=widths)


def sección(story, st, title, intro=None):
    base.add_page(story, st, title, intro)


def build(path, bw=False):
    st = base.styles(bw=bw)
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=.58 * inch, leftMargin=.66 * inch, topMargin=.70 * inch, bottomMargin=.58 * inch, title="Cuaderno de aprendizaje de vocabulario My Buddy AAC", author="BMC Luminary Ventures LLC")
    S = []
    cover_bg = colors.HexColor("#202020") if bw else base.NAVY
    cover = Table([
        [P("MY BUDDY AAC EN ESPAÑOL", ParagraphStyle("ce", parent=st["small"], textColor=colors.HexColor("#BDBDBD") if bw else base.GOLD, fontName="Helvetica-Bold", fontSize=10))],
        [P("Cuaderno de aprendizaje<br/>de vocabulario", st["title"])],
        [P("Aprende el tablero. Crea mensajes originales. Practica en la vida diaria.", st["subtitle"])],
        [P("Para comunicadores, familias, docentes, asistentes y equipos de apoyo", ParagraphStyle("cs", parent=st["small"], textColor=colors.white, fontSize=9.5, leading=13))],
    ], colWidths=[7.15 * inch], rowHeights=[.45 * inch, 2.15 * inch, 1.15 * inch, .8 * inch])
    cover.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), cover_bg), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 28), ("RIGHTPADDING", (0, 0), (-1, -1), 28)]))
    note = ParagraphStyle("cn", parent=st["body"], textColor=colors.white, borderColor=colors.HexColor("#BBBBBB") if bw else base.GOLD, borderWidth=1.2, borderPadding=11, backColor=colors.HexColor("#303030") if bw else colors.HexColor("#23434C"), fontName="Helvetica-Bold", alignment=TA_CENTER)
    foot = ParagraphStyle("cf", parent=st["body"], alignment=TA_CENTER, fontName="Helvetica-Bold", textColor=colors.white)
    S += [Spacer(1, .5 * inch), cover, Spacer(1, .35 * inch), P("Un recurso original y listo para imprimir que acompaña al tablero gratuito My Buddy", note), Spacer(1, .42 * inch), P("Edición 2026  |  quantumneuroshift.com", foot), PageBreak()]

    sección(S, st, "Cómo usar este cuaderno", "Úsalo junto al tablero My Buddy en español. Señala palabras en el dispositivo mientras hablas. Permite que la persona explore. La práctica sirve para aprender, no para examinar.")
    S.append(P("La meta es la comunicación", st["callout"]))
    S += viñetas(["Respeta todos los mensajes claros, incluidos no, parar, diferente y terminé.", "Modela una o dos palabras más que la extensión actual del mensaje.", "Mantén las palabras en lugares estables para que el movimiento se vuelva familiar.", "No exijas toques perfectos, contacto visual, imitación ni respuesta oral.", "Mantén disponible todo el vocabulario. La Práctica enfocada reduce la distracción sin quitar acceso."], st)
    S.append(P("Contenido", st["h2"]))
    S.append(tabla([("Página", "Sección"), ("3", "Principios de un sistema de CAA sólido"), ("4", "Mapa principal en español"), ("5", "Colores y funciones"), ("6", "Palabras núcleo y vocabulario específico"), ("7", "Rutas estables y palabras repetidas"), ("8", "Pronombres y conjugación"), ("9", "Gramática del español"), ("10", "Buscar y Práctica enfocada"), ("11-15", "Actividades"), ("16", "Reflexión y orientación de respuestas"), ("17", "Enlaces y notas")], st, (.8 * inch, 6.3 * inch)))
    S.append(PageBreak())

    sección(S, st, "Qué hace sólido a un sistema de CAA", "My Buddy permite crear lenguaje original, no solo pedir con frases guardadas. Combina palabras frecuentes con vocabulario específico para personas, lugares, cosas y temas.")
    S.append(tabla([("Decisión", "Por qué importa"), ("Palabras combinables", "La persona puede pedir, rechazar, preguntar, comentar, contar algo y corregir un malentendido."), ("Ubicaciones estables", "Cada palabra conserva su lugar. La persona aprende el movimiento en vez de buscar en un tablero que cambia."), ("Palabras núcleo", "Yo, querer, ir, ayudar, no, más y diferente sirven en muchas actividades."), ("Vocabulario específico", "Las carpetas ofrecen nombres, comidas, lugares, salud, escuela, fechas y temas personales."), ("Gramática española", "Las conjugaciones, el género, el número, los artículos y las contracciones permiten mensajes más exactos."), ("Apoyos de acceso", "Vista completa, Vista simple, Buscar, Práctica enfocada, edición, fotos, teclado y voz responden a distintas necesidades.")], st, (1.55 * inch, 5.55 * inch)))
    S.append(P("My Buddy no es un dispositivo médico ni sustituye una evaluación individual de CAA. Un profesional de fonoaudiología o logopedia puede ayudar a adaptar el acceso y el vocabulario.", st["callout"]))
    S.append(PageBreak())

    sección(S, st, "Mapa principal de My Buddy en español", "Este es el orden exacto de 12 por 7 que utiliza la Vista completa actual. Las etiquetas pequeñas indican la función de cada palabra. La aplicación también muestra un símbolo.")
    S.append(mapa(st, bw=bw))
    S.append(P("Cómo leer el mapa", st["h2"]))
    S += viñetas(["Las primeras cuatro filas contienen pronombres, verbos y palabras de gramática o ubicación.", "Las filas 5 y 6 añaden respuestas, descripciones, lenguaje social, preguntas, a y la carpeta Gramática.", "La fila 7 contiene carpetas. Cada carpeta abre vocabulario específico sin cambiar la posición de Inicio."], st)
    S.append(PageBreak())

    sección(S, st, "Los colores indican la función", "El color es una pista, no una regla que la persona deba memorizar. Cada botón también tiene palabra escrita, imagen y posición estable.")
    S.append(clave(st, bw=bw))
    S.append(P("Pruébalo", st["h2"]))
    S.append(P("Busca en el mapa una acción, un pronombre, una descripción, una palabra gramatical y una carpeta. Rodea cada una.", st["body"]))
    S.append(base.blank_lines(5))
    S.append(P("El color debe mantenerse cuando una palabra aparece en una página vinculada. La edición en blanco y negro conserva las etiquetas de función.", st["callout"]))
    S.append(PageBreak())

    sección(S, st, "Palabras núcleo y vocabulario específico", "Las palabras núcleo sirven en muchos lugares y actividades. Las carpetas contienen palabras más específicas. La comunicación necesita ambos grupos.")
    S.append(tabla([("Las palabras núcleo permiten...", "Las carpetas permiten..."), ("pedir: querer, más, diferente", "nombrar una comida, juguete, persona o lugar"), ("rechazar: no, nunca, parar, terminé", "indicar qué parte del cuerpo duele"), ("comentar: gustar, bueno, feliz, grande", "hablar de una clase, fecha, fiesta o interés"), ("dirigir: ir, venir, dar, poner, abrir", "identificar a una persona o lugar específico"), ("preguntar: qué, dónde, quién, por qué, cómo", "añadir el tema exacto de la pregunta")], st, (3.55 * inch, 3.55 * inch)))
    S.append(P("Los mensajes se construyen con partes reutilizables", st["h2"]))
    S.append(base.word_tiles(["yo", "quiero", "comida", "diferente"], ["pronoun", "verb", "noun", "adjective"], st, bw=bw, caption="Una petición que puede cambiar según la situación", kind_labels=LABELS))
    S.append(Spacer(1, 8))
    S.append(base.word_tiles(["no", "esto"], ["social", "grammar"], st, bw=bw, caption="Un rechazo o una corrección", kind_labels=LABELS))
    S.append(PageBreak())

    sección(S, st, "Rutas estables y palabras repetidas", "Algunas palabras de Inicio abren una página ampliada. La misma palabra aparece en el mismo lugar físico dentro de esa página. El primer toque abre la familia y el segundo produce la palabra o su forma.")
    S.append(tabla([("Inicio", "La siguiente página ofrece", "Ejemplo"), ("ir", "conjugaciones y acciones relacionadas", "yo + quiero + ir"), ("sentir", "conjugaciones y sentimientos", "yo + me siento + preocupado"), ("yo / tú / él / ella / nosotros / ellos", "formas pronominales e inicios de oración", "ella + quiere + más"), ("gramática", "artículos, contracciones, terminaciones y conectores", "ir + al + baño"), ("carpeta", "vocabulario específico del tema", "ir + a + la + escuela")], st, (1.35 * inch, 3.8 * inch, 1.95 * inch)))
    S.append(P("Ejemplo de una ruta", st["h2"]))
    S.append(base.word_tiles(["INICIO: ir", "→", "PÁGINA IR: ir", "→", "lugares"], ["verb", "grammar", "verb", "grammar", "folder"], st, bw=bw, caption="La palabra repetida funciona como ancla", kind_labels=LABELS))
    S.append(P("Ruta que quiero practicar:", st["h2"]))
    S.append(base.blank_lines(5))
    S.append(PageBreak())

    sección(S, st, "Pronombres y conjugación", "Los pronombres ocupan posiciones previsibles. Sus páginas ofrecen formas de objeto, posesivos y verbos conjugados. Los verbos del Inicio aparecen en infinitivo porque funcionan como puertas hacia su familia.")
    S.append(tabla([("Persona", "Sujeto", "Objeto", "Posesivo", "Ejemplo"), ("quien habla", "yo", "me", "mi / mío", "yo quiero mi libro"), ("quien escucha", "tú", "te", "tu / tuyo", "tú me ayudas"), ("otra persona", "él / ella / ellos", "lo / la / le / se", "su / suyo", "ellos quieren ir"), ("grupo con quien habla", "nosotros", "nos", "nuestro", "nosotros vamos")], st, (1.25 * inch, 1.05 * inch, 1.15 * inch, 1.25 * inch, 2.4 * inch)))
    S.append(P("Construye y compara", st["h2"]))
    S.append(base.word_tiles(["ella", "quiere", "más"], ["pronoun", "verb", "adjective"], st, bw=bw, caption="Persona + acción conjugada + información", kind_labels=LABELS))
    S.append(Spacer(1, 8))
    S.append(P("Cambia solo la persona y observa cómo cambia la forma verbal. Escribe dos mensajes.", st["body"]))
    S.append(base.blank_lines(7))
    S.append(PageBreak())

    sección(S, st, "La gramática del español", "La gramática está disponible cuando ayuda a expresar la intención. Responde primero al significado. Después puedes modelar una forma un poco más completa sin exigir que la persona la copie.")
    S.append(tabla([("Herramienta", "Ejemplos", "Qué expresa"), ("negación", "no, nunca, tampoco", "rechazo, corrección o desacuerdo"), ("conjugación", "quiero, quieres, quiere, queremos", "persona, número, tiempo y modo"), ("género y número", "el / la, bueno / buena, -s / -es", "concordancia y cantidad"), ("contracciones", "a + el = al; de + el = del", "rutas naturales como ir al baño"), ("preguntas", "qué, quién, dónde, cuándo, por qué, cómo", "información y conversación"), ("conectores", "y, pero, porque, si", "ideas más largas y exactas")], st, (1.25 * inch, 2.15 * inch, 3.7 * inch)))
    S.append(P("Modelos respetuosos", st["h2"]))
    S += viñetas(["Comunicador: ir escuela. Compañero: Sí, vamos a ir a la escuela.", "Comunicador: no esto. Compañero: No quieres esto. Quieres algo diferente.", "Comunicador: ella triste. Compañero: Ella está triste. ¿Qué pasó?"], st)
    S.append(base.word_tiles(["yo", "estaba", "jugando"], ["pronoun", "grammar", "verb"], st, bw=bw, caption="La conjugación añade tiempo y detalle", kind_labels=LABELS))
    S.append(PageBreak())

    sección(S, st, "Buscar y Práctica enfocada", "Ambas herramientas enseñan el tablero existente. Ninguna cambia el mapa de palabras.")
    S.append(tabla([("Herramienta", "Cuándo usarla", "Qué ocurre"), ("Buscar", "sabes la palabra pero no su ubicación", "My Buddy muestra la ruta y puede enseñarla paso por paso."), ("Práctica enfocada", "quieres practicar un grupo pequeño", "Resalta las palabras y todas las puertas necesarias. Los demás botones siguen visibles y disponibles."), ("Vista simple", "se necesita una pantalla pequeña o menos botones", "Ofrece vocabulario significativo con botones grandes. Vista completa siempre puede restaurarse.")], st, (1.35 * inch, 2.55 * inch, 3.2 * inch)))
    S.append(P("Primer grupo sugerido", st["h2"]))
    S.append(P("yo, querer, más, ir, parar, ayudar, no, sí", st["callout"]))
    S.append(P("Elige palabras importantes para la vida real de la persona. Termina la Práctica enfocada cuando necesite ver todo el tablero sin atenuación.", st["body"]))
    S.append(P("Palabras para la próxima práctica:", st["h2"]))
    S.append(base.blank_lines(6))
    S.append(PageBreak())

    sección(S, st, "Práctica 1: aprende el Inicio", "Usa el mapa de la página 4. Es una actividad con el mapa abierto. La meta es reconocer patrones, no memorizar un examen.")
    S += viñetas(["1. Escribe los seis pronombres principales.", "2. Busca cuatro acciones útiles durante el juego.", "3. Busca tres palabras para rechazar o detener algo.", "4. Encuentra la palabra que conecta ir con un destino en ir a la escuela.", "5. Nombra tres carpetas de la última fila.", "6. Busca dos palabras interrogativas.", "7. Rodea el botón que lleva a artículos, contracciones y conectores."], st)
    S.append(base.blank_lines(12))
    S.append(PageBreak())

    sección(S, st, "Práctica 2: crea mensajes nuevos", "Puede haber más de una respuesta correcta. Usa el tablero para construir un mensaje que corresponda a cada situación.")
    S.append(tabla([("Situación", "Tu mensaje"), ("Quieres ir a un lugar diferente.", ""), ("Necesitas que alguien pare y escuche.", ""), ("Algo duele, pero la otra persona entendió mal dónde.", ""), ("Te gustó una actividad y quieres repetirla.", ""), ("Quieres preguntar quién viene.", ""), ("Quieres contar lo que pasó ayer.", ""), ("No conoces una palabra y la describes.", "")], st, (3.55 * inch, 3.55 * inch)))
    S.append(P("Alarga un mensaje añadiendo una persona, acción, descripción, lugar o momento.", st["callout"]))
    S.append(base.blank_lines(4))
    S.append(PageBreak())

    sección(S, st, "Práctica 3: comunica por muchas razones", "La CAA no sirve solamente para pedir. Planea una oportunidad natural para cada función.")
    S.append(tabla([("Razón", "Palabras posibles", "Oportunidad real"), ("pedir", "querer, más, diferente", ""), ("rechazar", "no, parar, nunca, terminé", ""), ("comentar", "gustar, feliz, bueno, grande", ""), ("preguntar", "qué, dónde, quién, por qué, cómo", ""), ("dirigir", "ir, venir, dar, poner, abrir", ""), ("expresar sentimientos", "sentir más una emoción", ""), ("reparar", "no esto, quiero decir, mostrar", ""), ("conectar", "hola, por favor, gracias, perdón", "")], st, (1.4 * inch, 2.6 * inch, 3.1 * inch)))
    S.append(P("El compañero debe notar y responder a todas estas razones, no solamente a las peticiones de objetos.", st["callout"]))
    S.append(PageBreak())

    sección(S, st, "Práctica 4: planea una rutina", "Elige una rutina que ya ocurre. Modela palabras útiles mientras la actividad continúa. Deja espacio para rechazar, preguntar, comentar y decir algo inesperado.")
    S.append(tabla([("Parte del plan", "Escribe tu plan"), ("Rutina", ""), ("Lugar y momento", ""), ("Palabras núcleo", ""), ("Vocabulario específico", ""), ("Posible rechazo", ""), ("Posible comentario", ""), ("Posible pregunta", ""), ("Cómo esperaremos y responderemos", "")], st, (2.1 * inch, 5.0 * inch)))
    S.append(P("Ejemplos: vestirse, preparar comida, usar el baño, lavarse las manos, ir a la escuela, tomar medicina, jugar o prepararse para dormir.", st["small"]))
    S.append(PageBreak())

    sección(S, st, "Práctica para compañeros de comunicación", "La conducta de quien acompaña puede facilitar o dificultar la comunicación. Practica estos hábitos antes de una situación urgente.")
    S.append(tabla([("Haz esto", "Evita esto"), ("Mantén el dispositivo al alcance y con carga.", "Guardarlo porque la actividad es rápida, social o desordenada."), ("Modela palabras sin exigir imitación.", "Convertir cada modelo en pregunta o mandato."), ("Espera suficiente tiempo.", "Responder por la persona demasiado pronto."), ("Cree y actúa ante mensajes claros.", "Ignorar no, parar, dolor, diferente o terminé."), ("Confirma cuando no entiendas.", "Fingir que entendiste o seguir adivinando."), ("Mantén un tablero impreso de respaldo.", "Depender de una sola batería o dispositivo.")], st, (3.55 * inch, 3.55 * inch)))
    S.append(P("Escribe una respuesta respetuosa", st["h2"]))
    S += [P("1. La persona toca no cuando esperabas sí.", st["body"]), base.blank_lines(2), P("2. No entiendes el mensaje.", st["body"]), base.blank_lines(2), P("3. La persona explora botones durante una rutina.", st["body"]), base.blank_lines(2)]
    S.append(PageBreak())

    sección(S, st, "Reflexión y orientación de respuestas", "El progreso no es una puntuación de vocabulario. Busca más autonomía, más razones para comunicarse, navegación más fácil y mejores respuestas de los compañeros.")
    S.append(tabla([("Reflexión", "Notas"), ("Mensajes iniciados por la persona", ""), ("Nuevas razones para comunicarse", ""), ("Palabras difíciles de encontrar", ""), ("Vocabulario que debe personalizarse", ""), ("Ajustes de acceso o voz", ""), ("Lo que modelaremos después", "")], st, (2.75 * inch, 4.35 * inch)))
    S.append(P("Orientación para la Práctica 1", st["h2"]))
    S += [P("• Pronombres: yo, nosotros, tú, ellos, él y ella.", st["small"]), P("• Algunas acciones: jugar, ir, mirar, venir, dar, hacer, poner, abrir, leer, caminar y correr.", st["small"]), P("• Para rechazar o detener: no, parar, nunca y terminé, según la intención.", st["small"]), P("• En ir a la escuela, la palabra de enlace es a. Para ir al baño, la contracción correcta es al.", st["small"]), P("• Preguntas: qué, dónde, quién, cuándo, por qué y cómo.", st["small"]), P("• La carpeta Gramática contiene artículos, contracciones y conectores.", st["small"])]
    S.append(PageBreak())

    sección(S, st, "Enlaces útiles y notas", "Estos recursos independientes orientaron el enfoque de enseñanza. My Buddy no está afiliado con estas organizaciones ni con productos comerciales de CAA.")
    S.append(tabla([("Recurso", "Enlace"), ("Biblioteca de My Buddy", "quantumneuroshift.com/apps/my-buddy-training.html"), ("Aula abierta de ARASAAC", "aulaabierta.arasaac.org/comunicacion_aumentativa_y_alternativa_caa"), ("CAA en español de ASHA", "asha.org/public/speech/spanish/los-sistemas-aumentativos-y-alternativos-de-comunicacion"), ("AAC Language Lab", "aaclanguagelab.com/language-stages"), ("AssistiveWare Learn AAC", "assistiveware.com/learn-aac/learn-aac-guide")], st, (2.0 * inch, 5.1 * inch)))
    S.append(P("Notas de implementación", st["h2"]))
    S += viñetas(["My Buddy guarda la personalización en el dispositivo local, no en un servidor de My Buddy.", "La aplicación funciona sin internet después de instalarse y cargarse correctamente como PWA.", "No se añadió seguimiento de uso en un servidor porque el proyecto prioriza la privacidad local.", "Este cuaderno usa texto y diagramas originales. No reproduce bibliotecas de símbolos propietarias.", "El español es neutro y está pensado para un público amplio. Una familia puede personalizar vocabulario regional sin mover las palabras núcleo."], st)
    S.append(P("Notas", st["h2"]))
    S.append(base.blank_lines(9))

    draw = lambda canvas, document: base.page_header(canvas, document, bw=bw, header_text="MY BUDDY AAC  |  CUADERNO DE VOCABULARIO", footer_text="Se puede imprimir y compartir para la capacitación de My Buddy", cover_words=["yo", "quiero", "ir", "ayuda", "más", "parar", "sentir", "dónde", "a", "escuela"])
    doc.build(S, onFirstPage=draw, onLaterPages=draw)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    build(OUT / "my-buddy-vocabulary-learning-workbook-es.pdf", bw=False)
    build(OUT / "my-buddy-vocabulary-learning-workbook-es-black-and-white.pdf", bw=True)


if __name__ == "__main__":
    main()
