"""Builds every HTML page of the site. Run from the repo root:  python3 tools/build_pages.py .
Shared layout (sidebar menu, footer) and all page text live here."""
import os, sys, json, html as H
from urllib.parse import quote_plus

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
SITE = "https://townandcountryplanningltd.co.uk/"
PHONE, PHONE_TEL, EMAIL = "07843 561129", "07843561129", "martin@tcpltd.net"
GOOGLE_REVIEWS = "https://www.google.com/search?q=Town+%26+Country+Planning+Ltd+Cockfosters"  # replace with the Google review link when available

NAV = [("index.html", "Home"), ("projects.html", "Projects and map"), ("services.html", "Services"),
       ("process.html", "How we work"), ("reviews.html", "Reviews"), ("about.html", "About us"), ("faq.html", "FAQ"),
       ("contact.html", "Contact")]

# ---------------- Areas ----------------
# level = how much of our work is there (from our project records): 4 most, 1 least.
# grid = (row, col) on the tile map, laid out roughly geographically.
AREAS = [
  # slug, name, short label, level, (row, col), group, towns, council name, planning portal
  ("barnet", "Barnet", "Barnet", 4, (3, 2), "North London",
   ["Cockfosters", "New Barnet", "East Barnet", "High Barnet", "Hadley Wood", "Whetstone", "Totteridge", "Finchley", "Friern Barnet", "Mill Hill", "Edgware", "Hendon", "Golders Green"],
   "London Borough of Barnet", "https://publicaccess.barnet.gov.uk/online-applications/"),
  ("hertsmere", "Hertsmere", "Hertsmere", 4, (2, 2), "Hertfordshire",
   ["Potters Bar", "Borehamwood", "Elstree", "Radlett", "Bushey", "Shenley"],
   "Hertsmere Borough Council", "https://www6.hertsmere.gov.uk/online-applications/"),
  ("enfield", "Enfield", "Enfield", 3, (3, 3), "North London",
   ["Enfield Town", "Southgate", "Oakwood", "Winchmore Hill", "Grange Park", "Palmers Green", "Bush Hill Park", "Edmonton"],
   "London Borough of Enfield", ""),
  ("welwyn-hatfield", "Welwyn Hatfield", "Welwyn Hatfield", 3, (1, 3), "Hertfordshire",
   ["Hatfield", "Welwyn Garden City", "Brookmans Park", "Welham Green", "Cuffley", "Northaw"],
   "Welwyn Hatfield Borough Council", "https://planning.welhat.gov.uk/"),
  ("haringey", "Haringey", "Haringey", 3, (4, 3), "North London",
   ["Muswell Hill", "Crouch End", "Highgate", "Hornsey", "Wood Green", "Tottenham"],
   "London Borough of Haringey", ""),
  ("watford", "Watford", "Watford", 3, (2, 1), "Hertfordshire",
   ["Watford", "Cassiobury", "Nascot", "Oxhey"],
   "Watford Borough Council", ""),
  ("harrow", "Harrow", "Harrow", 2, (3, 1), "North London",
   ["Harrow on the Hill", "Stanmore", "Pinner", "Harrow Weald", "Hatch End", "Kenton"],
   "London Borough of Harrow", ""),
  ("east-herts", "East Herts", "East Herts", 2, (1, 4), "Hertfordshire",
   ["Hertford", "Ware", "Bishop's Stortford", "Sawbridgeworth"],
   "East Hertfordshire District Council", ""),
  ("broxbourne", "Broxbourne", "Broxbourne", 2, (2, 4), "Hertfordshire",
   ["Cheshunt", "Goffs Oak", "Hoddesdon", "Broxbourne", "Wormley"],
   "Broxbourne Borough Council", ""),
]
OTHER_TILES = [  # areas we have worked in less often, shown on the tile map
  ("North Herts", 1, (0, 2)), ("Stevenage", 1, (0, 3)), ("Dacorum", 1, (1, 1)), ("St Albans", 1, (1, 2)),
  ("Three Rivers", 1, (2, 0)), ("Hillingdon", 0, (3, 0)), ("Waltham Forest", 1, (3, 4)), ("Redbridge", 1, (3, 5)),
  ("Ealing", 1, (4, 0)), ("Brent", 2, (4, 1)), ("Camden", 1, (4, 2)), ("Hackney", 1, (4, 4)),
  ("Hammersmith", 1, (5, 0)), ("Kensington", 1, (5, 1)), ("Westminster", 0, (5, 2)), ("Islington", 1, (5, 3)),
  ("Tower Hamlets", 1, (5, 4)), ("Wandsworth", 1, (6, 1)), ("Lambeth", 0, (6, 2)), ("Southwark", 0, (6, 3)), ("Merton", 2, (7, 1)),
]

# Shading and town lists follow the project data (data/projects.js).
def _projects():
    txt = open(os.path.join(OUT, "data", "projects.js"), encoding="utf-8").read()
    return json.loads(txt[txt.index("= [") + 2:txt.rindex("]") + 1])
PROJECTS = _projects()
COUNTS = {}
TOWNS_SEEN = {}
for _p in PROJECTS:
    COUNTS[_p["borough"]] = COUNTS.get(_p["borough"], 0) + 1
    TOWNS_SEEN.setdefault(_p["borough"], {})
    TOWNS_SEEN[_p["borough"]][_p["town"]] = TOWNS_SEEN[_p["borough"]].get(_p["town"], 0) + 1

def level(n): return 4 if n >= 100 else 3 if n >= 25 else 2 if n >= 8 else 1 if n else 0

def _norm(t): return t.lower().replace("'", "").replace(" town", "")
for _i, _a in enumerate(AREAS):
    seen = sorted(TOWNS_SEEN.get(_a[1], {}).items(), key=lambda kv: -kv[1])
    towns = [t for t, n in seen if t != "London"][:10]
    for t in _a[6]:
        if len(towns) >= 10: break
        if _norm(t) not in {_norm(x) for x in towns}: towns.append(t)
    AREAS[_i] = _a[:3] + (max(1, level(COUNTS.get(_a[1], 0))),) + _a[4:6] + (towns,) + _a[7:]
TILE_BOROUGH = {"Kensington": "Kensington and Chelsea", "Hammersmith": "Hammersmith and Fulham"}
OTHER_TILES = [(n, level(COUNTS.get(TILE_BOROUGH.get(n, n), 0)), rc) for n, _l, rc in OTHER_TILES]

def tilemap():
    cells = {}
    for a in AREAS:
        slug, name, short, lvl, (r, c) = a[0], a[1], a[2], a[3], a[4]
        cells[(r, c)] = f'<a class="lvl-{lvl}" href="area-{slug}.html" style="grid-row:{r+1};grid-column:{c+1}" title="{name}">{short}</a>'
    for name, lvl, (r, c) in OTHER_TILES:
        if not lvl: continue  # only show areas where we have had approved jobs
        cells[(r, c)] = f'<a class="lvl-{lvl}" href="areas.html#further" style="grid-row:{r+1};grid-column:{c+1}" title="{name}">{name}</a>'
    legend = ('<div class="legend"><span>Fewer projects</span><span class="legend-group">'
              + "".join(f'<i class="lvl-{i}"></i>' for i in range(1, 5)) + '</span><span>More projects</span></div>')
    return ('<div><nav class="tilemap" aria-label="Areas we cover, laid out roughly as a map">' + "".join(cells.values()) + '</nav>'
            + legend + '<p class="muted" style="font-size:0.85rem;margin-top:6px">Shading reflects our project records. Hertfordshire to the north, London to the south.</p></div>')

# ---------------- Shared bits ----------------
def esc(s): return H.escape(s, quote=True)

def shell(fname, title, desc, body, extra_head="", scripts=(), canonical=None):
    nav = "\n".join(f'<a href="{h}"{" aria-current=\"page\"" if h == fname else ""}>{t}</a>' for h, t in NAV)
    canon = canonical or (SITE if fname == "index.html" else SITE + fname)
    ld = ""
    if fname == "index.html":
        ld = '<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "ProfessionalService", "name": "Town & Country Planning Ltd",
            "url": SITE, "telephone": "+447843561129", "email": EMAIL, "foundingDate": "2005",
            "address": {"@type": "PostalAddress", "addressLocality": "Cockfosters, Barnet", "postalCode": "EN4", "addressCountry": "GB"},
            "areaServed": [a[1] for a in AREAS],
            "description": "Planning drawings, planning applications and building control drawings for extensions, loft conversions and new homes in North London and Hertfordshire."}) + '</script>'
    footer_areas = "".join(f'<li><a href="area-{a[0]}.html">{a[1]}</a></li>' for a in AREAS[:6])
    sc = "\n".join(f'<script src="{s}"></script>' for s in scripts)
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<link rel="icon" href="img/logo.png">
<meta property="og:image" content="{SITE}img/logo.png">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0F2A3C">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Carlito:ital,wght@0,400;0,700;1,400&amp;display=swap">
<link rel="stylesheet" href="css/site.css">
{extra_head}{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="shell">
<header class="side" id="side">
<a class="brand" href="index.html" aria-label="Town and Country Planning Ltd, home">
<span class="brand-logo"><img src="img/logo.png" alt="" width="190" height="140"></span>
<span class="brand-name">Town &amp; Country<span>Planning Ltd</span></span>
</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="side-nav">Menu</button>
<nav class="side-nav" id="side-nav" aria-label="Main">
{nav}
</nav>
<div class="side-foot">
<a class="phone" href="tel:{PHONE_TEL}">{PHONE}</a>
<a href="mailto:{EMAIL}">{EMAIL}</a>
<small>Cockfosters, Barnet · since 2005</small>
<a class="btn btn-accent" href="contact.html">Arrange a meeting</a>
</div>
</header>
<div class="content">
<main id="main">
{body}
</main>
<footer class="site-footer">
<div class="wrap">
<div><h3>Town &amp; Country Planning Ltd</h3><ul><li>Planning and design consultants</li><li>Cockfosters, Barnet EN4</li><li>[Company number]</li></ul></div>
<div><h3>Explore</h3><ul><li><a href="projects.html">Projects and map</a></li><li><a href="areas.html">Areas we cover</a></li><li><a href="services.html">Services</a></li><li><a href="fees.html">Fees</a></li><li><a href="reviews.html">Reviews</a></li><li><a href="faq.html">FAQ</a></li></ul></div>
<div><h3>Areas</h3><ul>{footer_areas}<li><a href="areas.html">All areas</a></li></ul></div>
<div><h3>Contact</h3><ul><li><a href="tel:{PHONE_TEL}">{PHONE}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li>© <span id="year">2026</span> Town &amp; Country Planning Ltd</li></ul></div>
</div>
</footer>
</div>
</div>
<script src="js/site.js"></script>
{sc}
</body>
</html>
'''

CLOSING = f'''<section class="closing section"><div class="wrap">
<div class="stack"><span class="label">Next step</span><h2>Tell us what you are thinking of doing.</h2><p>A short conversation is the best place to start. We will talk through your property, what is likely to be possible and how we would approach it.</p></div>
<div class="actions"><a class="btn btn-accent" href="tel:{PHONE_TEL}">Call {PHONE}</a><a class="btn btn-ghost" href="contact.html">Send an enquiry</a></div>
</div></section>'''

STEPS = [("Consultation", "We meet you at the property, listen to what you want and tell you honestly what is likely to be possible, including anything you can build without planning permission."),
         ("Measured survey", "We survey the house and plot in detail so every drawing starts from accurate measurements."),
         ("Design", "We draw the existing and proposed plans in CAD and work through options with you until the design is right."),
         ("Planning", "We prepare and submit the application, deal with the planning officer and keep you updated until a decision is issued."),
         ("Building control", "Once approved, we produce the technical drawings and specification your builder and building control need.")]
def timeline():
    return '<ol class="timeline">' + "".join(f'<li><span class="n">{i}</span><strong>{t}</strong><p>{d}</p></li>' for i, (t, d) in enumerate(STEPS, 1)) + '</ol>'

SERVICES = [("extensions", "Extensions", "Rear, side return, wraparound and two storey extensions designed around how you live.", "rear extension"),
            ("lofts", "Loft conversions", "Dormer, hip to gable and mansard lofts that make the most of the roof space.", "loft conversion"),
            ("new-build", "New homes", "Replacement houses, new homes on garden plots and small developments.", "new build"),
            ("conversions", "Conversions and change of use", "Garage, basement and house to flat conversions, and commercial to residential.", "conversion"),
            ("outbuildings", "Garden rooms and outbuildings", "Garden offices, studios, annexes and pool houses, often without a full application.", "garden room"),
            ("consultancy", "Planning advice and appeals", "Pre-application advice, permitted development checks, planning statements and appeals.", "planning advice")]
def service_tiles():
    return '<div class="tiles">' + "".join(
        f'<a class="tile" href="services.html#{a}"><div class="ph"><span>Photo: {p}</span></div><div class="tile-body"><h3>{t}</h3><p>{d}</p><span class="go">Find out more</span></div></a>'
        for a, t, d, p in SERVICES) + '</div>'

Q = [("Following on from a recommendation from a friend and various talks with other architects we decided to instruct Martin to be the architect for our project, which was a single storey L-shape extension and loft conversion. Both myself and my wife had not done this before so it was reassuring Martin was there to listen and make our ideas and dreams into reality, and he closely worked with our builder at all times. I have already recommended Martin and will continue to do so.", "Mr & Mrs B. Jacobs", "Borehamwood"),
     ("Martin at Town & Country Planning Ltd have proven themselves again and again by producing innovative and creative designs and achieving planning consent for our projects. A personal service with a big practice feel.", "Mr Harris, UK Room / Investco Properties", "Mill Hill"),
     ("I first used the services of TCPL some years ago for a substantial extension to my home. From their knowledge and experience they were able to expertly advise and guide me through daunting stages to get the project started. They produced plans of the proposed extension, provided a set of specifications in accordance with regulations and made the required applications to the local authorities. Suffice to say I am currently using them again for a commercial conversion project and again the level of knowledge, advice and support is first class. I would not hesitate in recommending them to anyone embarking on a building project.", "Mr & Mrs Eaves", "Hatfield"),
     ("My wife and I have been delighted with the rear and loft extensions TCP have designed for our house. Both have been sympathetically detailed to suit the property and give a 'wow' factor. The information produced by TCP was accepted and approved on the first occasion by the Local Authority Planning and Building Control departments. This demonstrates TCP have a thorough knowledge and understanding of local building constraints. We had confidence in TCP from start to finish.", "Mr, BEng (Hons) CEng MICE", "Finchley"),
     ("&hellip; Mr McGahon proved to be extremely professional and quickly turned our ideas into reality. He was efficient, yet patient, answering our questions, and offering explanations and suggestions where necessary. As novices, he put us at ease, so when we finally embarked on the build, we were fully prepared and the building works were successfully completed without any problems. We have what we envisaged and more. I would be happy to recommend Town & Country Planning Ltd.", "Ms Hill", "Potters Bar"),
     ("We were recommended to use Martin through a friend which for us was the best route as we knew he was great at his job and trustworthy. Having never carried out work on a property before, he was so helpful and explained everything that needed doing. He didn't only work on drawing up plans. He has a great relationship with the Council so had an insight into what we were and weren't allowed to carry out. Once we received our permission he helped us with everything else that needed carrying out too, which you don't get from all architects. He has helped us create our dream home.", "Mr & Mrs Beresford", "Borehamwood"),
     ("I would just like to say a big thank you for the first class service you provided me with in regards to our loft conversion. From start to finish your knowledge and advice was a huge plus for us in maximising our options and I look forward to working with you in the spring when we commence the garage conversion.", "Mr & Mrs S. Loughlin", "Barnet"),
     ("Martin from Town & Country Planning Ltd had been recommended to us by some local friends. We found Martin incredibly helpful and he spent some time trying to understand our exact requirements. He explained in detail how our plans would be impacted by the council regulations to ensure we were making informed decisions. Martin has extensive experience with the council which enabled us to track progress and make changes that enabled us to secure permission in a timely manner.", "Mr and Mrs Mohammed", "Mill Hill"),
     ("Between me and my next door neighbour we have used this company no more than four times in as many years. This says it all really. Fantastic service, would recommend this company over and over again. Thanks for everything Town & Country Planning Ltd.", "Mr Austin", "Borehamwood"),
     ("Our builder has a long standing work relationship with Martin and introduced us to him. We found Martin to be extremely competent as he drew up our plans quickly and accurately, and offered ideas and suggestions we had not thought of ourselves. Martin has experience and contacts with the local council so was able to guide us in what is acceptable and likely to get planning permission approval. We were so impressed with Martin's work on our first extension that we are now using him to draw up plans for our second!", "Mr & Mrs O'Grady", "Borehamwood")]
# For the carousel: a short heading and a passage copied word for word from each review above (same order as Q).
Q_SHORT = [("Our ideas made real", "&hellip;it was reassuring Martin was there to listen and make our ideas and dreams into reality, and he closely worked with our builder at all times."),
           ("A personal service", "&hellip;producing innovative and creative designs and achieving planning consent for our projects. A personal service with a big practice feel."),
           ("First class support", "&hellip;the level of knowledge, advice and support is first class. I would not hesitate in recommending them to anyone embarking on a building project."),
           ("Approved first time", "The information produced by TCP was accepted and approved on the first occasion by the Local Authority Planning and Building Control departments."),
           ("Put us at ease", "As novices, he put us at ease, so when we finally embarked on the build, we were fully prepared and the building works were successfully completed without any problems."),
           ("So helpful", "Having never carried out work on a property before, he was so helpful and explained everything that needed doing."),
           ("Made the most of our options", "From start to finish your knowledge and advice was a huge plus for us in maximising our options&hellip;"),
           ("Permission in good time", "Martin has extensive experience with the council which enabled us to track progress and make changes that enabled us to secure permission in a timely manner."),
           ("Back again and again", "Between me and my next door neighbour we have used this company no more than four times in as many years. This says it all really."),
           ("Back for a second extension", "We were so impressed with Martin's work on our first extension that we are now using him to draw up plans for our second!")]
for _h, _x in Q_SHORT:
    assert _x.replace("&hellip;", "") in "".join(t for t, _n, _p in Q).replace("&hellip;", ""), _x

def quote_html(i):
    t, n, place = Q[i]
    t = t.replace("&hellip;", "\x00"); t = esc(t).replace("\x00", "&hellip;")
    return f'<figure class="quote" id="review-{i+1}"><span class="stars" aria-label="Five stars">★★★★★</span><blockquote>&ldquo;{t}&rdquo;</blockquote><figcaption>{esc(n)}, {esc(place)}</figcaption></figure>'
def quotes(idx): return '<div class="quotes">' + "".join(quote_html(i) for i in idx) + '</div>'
def reviews_top():
    return f'''<div class="reviews-top"><div><span class="label">Reviews</span><h3>Worked with us? We would value your review.</h3><p class="muted">Most of our work comes from recommendation. A short Google review helps the next homeowner find us.</p></div>
<div class="actions"><a class="btn btn-navy" href="{GOOGLE_REVIEWS}" target="_blank" rel="noopener">Review us on Google</a><a class="btn btn-line" href="{GOOGLE_REVIEWS}" target="_blank" rel="noopener">Read our Google reviews</a></div></div>'''

def filters(full=True):
    selects = ('<label class="fl"><span>Area</span><select id="project-area"><option value="">All areas</option></select></label>'
               '<label class="fl"><span>Year</span><select id="project-year"><option value="">Any year</option></select></label>') if full else ''
    return (f'<div class="filter-panel"><div class="filter-row"><label class="fl fl-search"><span>Search projects</span>'
            f'<input id="project-search" type="search" placeholder="Street, town, or e.g. loft"></label>'
            f'<label class="fl"><span>Type of work</span><select id="project-type"><option value="">All types of work</option></select></label>{selects}'
            f'<button type="button" class="btn btn-line btn-clear" id="project-clear" hidden>Clear</button></div></div>'
            f'<p class="result-count" id="project-count" aria-live="polite"></p>')

HERO_ART = '''<svg viewBox="0 0 480 360" role="img" aria-label="Line drawing of a house with a proposed rear extension and loft dormer">
<g fill="none" stroke="#C9D6E0" stroke-width="2" stroke-linejoin="round">
<path d="M70 300 V170 L170 90 L270 170 V300 Z"/>
<rect x="100" y="200" width="40" height="50"/><rect x="200" y="200" width="40" height="50"/>
<rect x="140" y="250" width="40" height="50"/>
<line x1="40" y1="300" x2="450" y2="300"/>
</g>
<g fill="none" stroke="#9CC3E6" stroke-width="2.5" stroke-dasharray="7 5" stroke-linejoin="round">
<path d="M270 300 V215 H400 V300"/>
<path d="M150 120 H215 V150 H150 Z"/>
<rect x="300" y="245" width="70" height="55"/>
</g>
<g stroke="#C9D6E0" stroke-width="1" fill="#C9D6E0" font-family="Carlito, Calibri, sans-serif" font-size="12">
<line x1="270" y1="325" x2="400" y2="325"/><line x1="270" y1="318" x2="270" y2="332"/><line x1="400" y1="318" x2="400" y2="332"/>
<text x="312" y="345" stroke="none">4000</text>
<line x1="425" y1="215" x2="425" y2="300"/><line x1="418" y1="215" x2="432" y2="215"/><line x1="418" y1="300" x2="432" y2="300"/>
<text x="434" y="262" stroke="none">3000</text>
</g>
<g font-family="Carlito, Calibri, sans-serif" font-size="11" fill="#C9D6E0">
<rect x="40" y="18" width="200" height="44" fill="none" stroke="#C9D6E0" stroke-width="1"/>
<text x="50" y="36">PROPOSED REAR ELEVATION</text><text x="50" y="53">SCALE 1:100</text>
<text x="282" y="206" fill="#9CC3E6">PROPOSED EXTENSION</text>
</g>
</svg>'''

# Homepage slideshow behind the hero. Put photos in img/hero/ and set the file name;
# None shows a placeholder with the caption until the photo is added.
HERO_SLIDES = [
    (None, "Photo to come: finished rear extension"),
    (None, "Photo to come: loft conversion"),
    (None, "Photo to come: new home"),
    (None, "Photo to come: kitchen inside an extension"),
    (None, "Photo to come: garden room"),
]

def hero_slides():
    out = []
    for i, (img, cap) in enumerate(HERO_SLIDES):
        cls = "hero-slide is-on" if i == 0 else "hero-slide"
        if img:
            out.append(f'<div class="{cls}" style="background-image:url(img/hero/{esc(img)})"></div>')
        else:
            out.append(f'<div class="{cls} ph-slide ph-slide-{i % 5}"><span>{esc(cap)}</span></div>')
    return '<div class="hero-slides" aria-hidden="true">' + "".join(out) + '</div>'

def hero(h1, sub, actions, label="Planning and design consultants · since 2005", art=True, slides=False):
    right = f'<div class="hero-art">{HERO_ART}</div>' if art and not slides else ''
    bg = hero_slides() if slides else ''
    cls = "hero hero-photo-bg" if slides else "hero"
    return f'''<section class="{cls}">{bg}<div class="wrap"><div class="hero-copy"><span class="label">{label}</span><h1>{h1}</h1><p>{sub}</p>{actions}</div>{right}</div></section>'''

def page_head(label, h1, lede, cls="band"):
    return f'<section class="{cls} page-head"><div class="wrap stack"><span class="label">{label}</span><h1>{h1}</h1><p class="lede">{lede}</p></div></section>'

# ---------------- Reviews carousel ----------------
# Google reviews shown on the site. Paste each one here as (text, name, place or ""), newest first.
# They appear in the carousel with a Google badge. (Pulling them live from Google needs a
# Google Places API key; until then, copy them in here.)
GOOGLE_REVIEW_LIST = []

def review_slides():
    items = [(None, t, n, p, "Google review", None) for t, n, p in GOOGLE_REVIEW_LIST] + [(Q_SHORT[k][0], Q_SHORT[k][1], n, p, "Client testimonial", k) for k, (t, n, p) in enumerate(Q)]
    total = len(items)
    out = []
    for i, (head, t, n, place, src, k) in enumerate(items):
        t = t.replace("&hellip;", "\x00"); t = esc(t).replace("\x00", "&hellip;")
        head_html = f'<h3 class="rv-head">{esc(head)}</h3>' if head else ''
        more = f' <a class="rv-more" href="reviews.html#review-{k+1}">Read the full review</a>' if k is not None else ''
        who = esc(n) + (f", {esc(place)}" if place else "")
        g = ' rv-google' if src == "Google review" else ''
        out.append(f'<figure class="rv-slide{g}{" is-on" if i == 0 else ""}" role="group" aria-roledescription="slide" aria-label="{i+1} of {total}">'
                   f'<div class="rv-top"><span class="stars" aria-label="Five stars">★★★★★</span><span class="rv-src">{src}</span></div>'
                   f'{head_html}<blockquote>&ldquo;{t}&rdquo;</blockquote><figcaption>{who}{more}</figcaption></figure>')
    return "".join(out), total

def reviews_carousel():
    slides, total = review_slides()
    dots = "".join(f'<button type="button" class="dot" data-go="{i}" aria-label="Show review {i+1}"{" aria-current=\"true\"" if i == 0 else ""}></button>' for i in range(total))
    return f'''<div class="rv-layout">
<div class="rv-google-box">
<span class="g-mark" aria-hidden="true">G</span>
<h3>Reviews on Google</h3>
<p class="muted">Read what clients say about us on Google, or leave a review of your own. Google reviews are added to this page too.</p>
<div class="actions"><a class="btn btn-navy" href="{GOOGLE_REVIEWS}" target="_blank" rel="noopener">Read our Google reviews</a><a class="btn btn-line" href="{GOOGLE_REVIEWS}" target="_blank" rel="noopener">Leave a review</a></div>
</div>
<section class="rv" data-carousel="fade" data-interval="8000" aria-roledescription="carousel" aria-label="Client reviews">
<div class="rv-slides" aria-live="off">{slides}</div>
<div class="car-controls">
<button type="button" class="car-btn" data-prev aria-label="Previous review"><span aria-hidden="true">&#8592;</span></button>
<button type="button" class="car-btn car-pause" data-pause aria-label="Pause reviews"><span aria-hidden="true" class="ico-pause"></span></button>
<button type="button" class="car-btn" data-next aria-label="Next review"><span aria-hidden="true">&#8594;</span></button>
<span class="car-count" data-count>1 / {total}</span>
<div class="dots">{dots}</div>
</div>
</section>
</div>'''

# ---------------- Featured projects ----------------
def _featured():
    txt = open(os.path.join(OUT, "data", "featured.js"), encoding="utf-8").read()
    return json.loads(txt[txt.index("= [") + 2:txt.rindex("]") + 1])
BY_ID = {p["id"]: p for p in PROJECTS}
FEATURED = []
for _f in _featured():
    _p = BY_ID.get(_f["id"]) or next((p for p in PROJECTS if p.get("street") == _f.get("street") and p["town"] == _f.get("town")), None)
    if _p: FEATURED.append((_f, _p))

def feat_url(p): return f'project-{p["id"]}.html'
def feat_place(p): return f'{p["street"]}, {p["town"]}' if p.get("street") else p["town"]
def feat_years(p):
    ys = sorted({a["year"] for a in p.get("approvals", []) if a.get("year")})
    return (str(ys[0]) if len(ys) == 1 else f"{ys[0]}–{ys[-1]}") if ys else str(p.get("year", ""))
def feat_photo(f, cap="Photo to come"):
    if f.get("photos"): return f'<img src="{esc(f["photos"][0])}" alt="{esc(f["title"])}" loading="lazy">'
    return f'<div class="ph"><span>{cap}</span></div>'

def featured_card(f, p, i, total):
    return (f'<article class="fp-card" role="group" aria-roledescription="slide" aria-label="{i+1} of {total}: {esc(f["title"])}">'
            f'<a class="fp-photo" href="{feat_url(p)}" tabindex="-1" aria-hidden="true">{feat_photo(f)}</a>'
            f'<div class="fp-body"><span class="card-type">{esc(p["type"])} · Approved {feat_years(p)}</span>'
            f'<h3><a href="{feat_url(p)}">{esc(f["title"])}</a></h3><p>{esc(f["project"])}</p>'
            f'<a class="more" href="{feat_url(p)}" aria-label="View project: {esc(f["title"])}">View project</a></div></article>')

def featured_carousel():
    total = len(FEATURED)
    cards = "".join(featured_card(f, p, i, total) for i, (f, p) in enumerate(FEATURED))
    return f'''<section class="fp" data-carousel="track" data-interval="5000" aria-roledescription="carousel" aria-label="Featured projects">
<div class="fp-track" tabindex="0" aria-label="Featured projects, scroll sideways">{cards}</div>
<div class="car-controls">
<button type="button" class="car-btn" data-prev aria-label="Previous project"><span aria-hidden="true">&#8592;</span></button>
<button type="button" class="car-btn car-pause" data-pause aria-label="Pause featured projects"><span aria-hidden="true" class="ico-pause"></span></button>
<button type="button" class="car-btn" data-next aria-label="Next project"><span aria-hidden="true">&#8594;</span></button>
<span class="car-count" data-count>1 / {total}</span>
</div>
</section>'''

def featured_page(i):
    f, p = FEATURED[i]
    nf, np_ = FEATURED[(i + 1) % len(FEATURED)]
    pf, pp = FEATURED[i - 1]
    photos = f.get("photos") or []
    if photos:
        gal = "".join(f'<img src="{esc(x)}" alt="{esc(f["title"])}, photo {k+1}"{" loading=\"lazy\"" if k else ""}>' for k, x in enumerate(photos))
    else:
        gal = '<div class="ph"><span>Photos to come</span></div><div class="ph"><span>Photo to come</span></div><div class="ph"><span>Photo to come</span></div>'
    feats = "".join(f"<li>{esc(x)}</li>" for x in f.get("features", []))
    desc = ("".join(f'<p>{esc(x)}</p>' for x in f["description"].split("\n\n")) if f.get("description") else
            f'<p>We designed the scheme and prepared the drawings and planning application for this {esc(p["type"].lower())} on {esc(feat_place(p))}. {esc(p["borough"] if p["borough"] != "Other" else "The council")} approved it in {feat_years(p)}.</p>'
            '<p class="muted"><em>A fuller write-up of the brief, the design and how the application went is to come.</em></p>')
    apps = "".join(
        f'<li><strong>Approved {a.get("year") or ""}</strong><span>{esc(a.get("summary") or a.get("route", ""))}</span>'
        f'<em>{esc(a.get("route", ""))}{" · Ref " + esc(a["ref"]) if a.get("ref") else ""}</em>'
        + (f' <a href="{esc(a["link"])}" target="_blank" rel="noopener">View the council decision<span class="sr-only"> (opens in a new tab)</span></a>' if a.get("link") else "")
        + '</li>' for a in reversed(p.get("approvals", [])))
    council = p["borough"] if p["borough"] != "Other" else "Local council"
    tour = f'<a class="btn btn-line" href="{esc(p["tour"])}" target="_blank" rel="noopener">3D tour</a>' if p.get("tour") else ""
    crumbs = f'<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a> <span aria-hidden="true">›</span> <a href="projects.html">Projects and map</a> <span aria-hidden="true">›</span> <span aria-current="page">{esc(f["title"])}</span></nav>'
    more = [FEATURED[(i + k) % len(FEATURED)] for k in (1, 2, 3)]
    more_html = "".join(featured_card(mf, mp, k, 3).replace(' role="group" aria-roledescription="slide"', '') for k, (mf, mp) in enumerate(more))
    plan_word = {"Extension": "an extension", "Extension and loft": "an extension or loft conversion", "Loft conversion": "a loft conversion", "New homes": "a new home",
                 "Outbuildings and garages": "a garden room or garage conversion", "Flats and change of use": "a conversion to flats", "Porch and front": "a new porch"}.get(p["type"], "something similar")
    body = (page_head(f"Featured project · {esc(p['type'])}", esc(f["title"]), esc(f["project"])).replace('<div class="wrap stack">', '<div class="wrap stack">' + crumbs, 1)
     + f'''<section class="section"><div class="wrap case">
<div class="case-gallery">{gal}</div>
<div class="case-body">
<div class="prose">
<h2>The project</h2>{desc}
<h3>Key features</h3><ul class="case-feats">{feats}</ul>
<h3>Planning decision</h3><ul class="case-apps">{apps}</ul>
</div>
<aside class="case-facts"><dl>
<dt>Location</dt><dd>{esc(feat_place(p))}</dd>
<dt>Council</dt><dd>{esc(council)}</dd>
<dt>Planning decision</dt><dd>Approved {feat_years(p)}</dd>
<dt>Type of work</dt><dd>{esc(p["type"])}</dd>
</dl><a class="btn btn-navy" href="projects.html#{p["id"]}">See it on the map</a>{tour}<a class="btn btn-line" href="contact.html?type={quote_plus(p["type"])}">Talk to us about yours</a></aside>
</div>
<div class="cta-box case-cta"><div><span class="label">Your project</span><h2>Planning {plan_word}?</h2><p>Tell us about your house and what you have in mind. We will tell you honestly what is likely to be approved.</p></div><div class="actions"><a class="btn btn-accent" href="tel:{PHONE_TEL}">Call {PHONE}</a><a class="btn btn-line" href="contact.html?type={quote_plus(p["type"])}">Send an enquiry</a></div></div>
<div><div class="section-head" style="margin-bottom:24px"><h2 style="font-size:1.5rem">More projects</h2><a class="more" href="projects.html">All projects and the map</a></div><div class="fp-grid">{more_html}</div></div>
</div></section>''')
    return shell(feat_url(p), f'{f["title"]} | Town & Country Planning Ltd',
                 f'{f["project"]}. Approved {feat_years(p)}. Design, drawings and planning application by Town & Country Planning Ltd.', body)

# ---------------- "What are you planning?" ----------------
_H = '<path d="M8 72H112"/>'
ICONS = {
 "detached": _H + '<path d="M38 72V38H82V72M34 40L60 18L86 40"/><path d="M54 72V58H66V72M44 46H52V54H44ZM68 46H76V54H68Z"/>',
 "semi": _H + '<path d="M18 72V38H102V72M60 38V72M14 40L36 18H84L106 40"/><path class="new-fill" d="M18 38H60V72H18Z"/><path d="M30 72V60H40V72M80 72V60H90V72"/>',
 "terraced": _H + '<path d="M8 72V38H112V72M45 38V72M78 38V72M6 40L18 22H102L114 40"/><path class="new-fill" d="M45 38H78V72H45Z"/><path d="M22 72V60H31V72M56 72V60H65V72M89 72V60H98V72"/>',
 "bungalow": _H + '<path d="M22 72V48H98V72M14 50L60 26L106 50"/><path d="M54 72V60H66V72M32 56H44V64H32ZM76 56H88V64H76Z"/>',
 "flat": _H + '<path d="M34 72V10H86V72"/><path d="M42 18H52V26H42ZM68 18H78V26H68ZM42 34H52V42H42ZM68 34H78V42H68ZM42 50H52V58H42ZM68 50H78V58H68Z"/><path d="M55 72V62H65V72"/>',
 "commercial": _H + '<path d="M20 72V24H100V72M20 34H100"/><path d="M28 44H74V64H28ZM82 72V44H94V72"/>',
 "f1": _H + '<path d="M34 72V50H86V72M30 52L60 36L90 52"/>',
 "f2": _H + '<path d="M34 72V32H86V72M34 52H86M30 34L60 16L90 34"/>',
 "f3": _H + '<path d="M34 72V22H86V72M34 39H86M34 56H86M30 24L60 6L90 24"/>',
 "rear": _H + '<path d="M18 72V32H62V72M14 34L40 12L66 34"/><path class="new" d="M62 72V48H100V72M62 48L100 44"/><path class="new" d="M74 72V58H90V72"/>',
 "side": _H + '<path d="M18 72V34H66V72M14 36L42 14L70 36"/><path class="new" d="M66 72V46H98V72M66 46L98 50"/>',
 "twostorey": _H + '<path d="M18 72V34H62V72M14 36L40 14L66 36"/><path class="new" d="M62 72V34H96V72M62 53H96M62 34L96 34"/>',
 "loft": _H + '<path d="M26 72V42H94V72M20 44L60 12L100 44"/><path class="new" d="M62 22V40H88V27"/><path class="new" d="M68 28H80V36H68Z"/>',
 "garage": _H + '<path d="M14 72V34H60V72M10 36L37 14L64 36M60 72V46H104V72"/><path class="new" d="M70 52H94V64H70Z"/>',
 "garden": '<path d="M8 72H112"/><path d="M24 72V54M24 54a10 10 0 1 1 0.1 0"/><path class="new" d="M52 72V42H104V72M48 42H108M66 42V72M80 42V72"/>',
 "newhome": _H + '<path class="new" d="M36 72V38H84V72M32 40L60 16L88 40M54 72V58H66V72"/>',
 "flats": _H + '<path d="M30 72V14H90V72"/><path class="new" d="M30 33H90M30 52H90M60 14V72"/><path d="M40 22H50V28H40ZM70 22H80V28H70ZM40 41H50V47H40ZM70 41H80V47H70Z"/>',
 "porch": _H + '<path d="M22 72V34H98V72M18 36L60 12L102 36M30 44H42V54H30ZM78 44H90V54H78Z"/><path class="new" d="M48 72V58H72V72M44 58L60 50L76 58"/>',
 "layout": '<path d="M14 10H106V72H14Z"/><path d="M14 40H50V72M50 52V10"/><path class="new" d="M50 40H106M78 40V72"/>',
 "unsure": _H + '<path d="M36 72V38H84V72M32 40L60 16L88 40"/><path class="new" d="M54 50a6 6 0 1 1 8 6v4M58 66v1"/>',
}
def icon(k): return f'<svg viewBox="0 0 120 80" aria-hidden="true" focusable="false">{ICONS[k]}</svg>'

PROPERTY = [("detached", "Detached house"), ("semi", "Semi-detached house"), ("terraced", "Terraced house"),
            ("bungalow", "Bungalow"), ("flat", "Flat or maisonette"), ("commercial", "Commercial building")]
FLOORS = [("f1", "One floor"), ("f2", "Two floors"), ("f3", "Three or more")]
# plan key, label, icon, projects filter (type of work, search words), not offered for these property types
PLANS = [("rear", "Rear extension", "rear", "", "rear extension", "flat"),
         ("side", "Side or wraparound extension", "side", "", "side extension", "flat terraced"),
         ("twostorey", "Two storey extension", "twostorey", "", "two storey", "flat bungalow"),
         ("loft", "Loft conversion", "loft", "", "loft", "flat commercial"),
         ("garage", "Garage conversion", "garage", "", "garage conversion", "flat commercial"),
         ("garden", "Garden room or outbuilding", "garden", "Outbuildings and garages", "", "commercial"),
         ("porch", "Porch or front changes", "porch", "", "porch", "flat commercial"),
         ("layout", "New layout inside", "layout", "", "internal", ""),
         ("newhome", "New home or replacement house", "newhome", "New homes", "", "flat"),
         ("flats", "Flats or change of use", "flats", "Flats and change of use", "", ""),
         ("unsure", "Not sure yet", "unsure", "", "", "")]

def tiles(step, items):
    return '<div class="pl-tiles">' + "".join(
        f'<button type="button" class="pl-tile" data-step="{step}" data-v="{k}" data-label="{esc(lbl)}"{" data-not=\"" + rest[0] + "\"" if rest else ""}>{icon(rest[1] if len(rest) > 1 else k)}<span>{esc(lbl)}</span></button>'
        for k, lbl, *rest in items) + '</div>'

def planner():
    plans = [(k, lbl, "", ic) for k, lbl, ic, _t, _q, _n in PLANS]
    plan_json = json.dumps({k: {"label": lbl, "type": t, "q": q} for k, lbl, _i, t, q, _n in PLANS})
    return f'''<section class="planner" id="planner" aria-labelledby="pl-h" hidden>
<div class="pl-head"><span class="label">What are you planning?</span><h2 id="pl-h">Find work like yours</h2><p class="muted">A few quick questions and we show you the approved projects most like yours, nearest first. Every house is different, so we talk costs through with you in person.</p></div>
<p class="pl-progress" aria-live="polite"><span data-pl-step>Step 1</span></p>
<fieldset class="pl-step" data-n="plan"><legend>What are you planning?</legend>{tiles("plan", plans)}</fieldset>
<fieldset class="pl-step" data-n="details" hidden><legend>Anything in particular? <span class="pl-sub">Choose any that apply. We will put the closest examples first.</span></legend>
<div class="opts pl-details" data-pl-details></div>
<div class="pl-where"><button type="button" class="btn btn-accent" data-pl-next>Next</button></div></fieldset>
<fieldset class="pl-step" data-n="where" hidden><legend>Where is the property?</legend>
<div class="pl-where"><label class="fl fl-search"><span>Town or postcode</span><input id="pl-place" type="text" autocomplete="postal-code" placeholder="e.g. Potters Bar or EN4"></label>
<button type="button" class="btn btn-accent" data-pl-where>Show projects</button><button type="button" class="pl-back" data-pl-skip>Skip this</button></div>
<p class="pl-hint" data-pl-hint aria-live="polite"></p></fieldset>
<div class="pl-result" hidden tabindex="-1">
<h3 data-pl-summary></h3>
<p data-pl-count class="lede"></p>
<div class="actions"><button type="button" class="btn btn-accent" data-pl-show>Show me these projects</button><a class="btn btn-navy" data-pl-enquire href="contact.html">Talk it through with us</a><a class="btn btn-line" href="tel:{PHONE_TEL}">Call {PHONE}</a></div>
</div>
<div class="pl-nav"><button type="button" class="pl-back" data-pl-back hidden>Back</button><button type="button" class="pl-back" data-pl-restart hidden>Start again</button></div>
<script type="application/json" id="pl-plans">{plan_json}</script>
</section>'''

def planner_teaser():
    return ('<div class="pl-tiles pl-teaser">' + "".join(
        f'<a class="pl-tile" href="projects.html?property={k}#planner">{icon(k)}<span>{esc(lbl)}</span></a>' for k, lbl in PROPERTY) + '</div>')

# ---------------- FAQ ----------------
# (question, answer). Answers may contain links. HOME_FAQ picks the ones shown on the home page.
FAQ = [("Getting started", [
  ("Where do I start?", f"With a phone call or an email. Tell us a little about the property and what you have in mind, and we will arrange to visit. Call <a href=\"tel:{PHONE_TEL}\">{PHONE}</a> or <a href=\"contact.html\">send an enquiry</a>."),
  ("Do you come to the property?", "Yes. The first meeting is at your home, so we can see the house, the garden and the neighbours' properties, listen to what you want and tell you honestly what is likely to be possible."),
  ("What do I need to have ready?", "Nothing formal. It helps to know roughly what you want, what matters most to you and what you would like to spend on the build. Photos of homes or rooms you like are useful too. If you have old plans, deeds or earlier planning decisions for the house, bring those out, but we can find most of what we need ourselves."),
  ("Who will I be working with?", "Martin and our small team. You deal with the same people from the first visit to the final drawing, and you always know who to call."),
  ("How long does the design take?", "It depends on the size of the project and how many options you want to explore. We give you a realistic timetable at the start, once we have seen the property and understood the brief.")]),
 ("Planning permission", [
  ("Do I always need planning permission for an extension?", "Not always. Many extensions can be built under permitted development rights. As a guide, a single storey rear extension can go out 3 metres on a terraced or semi-detached house and 4 metres on a detached house, or up to 6 and 8 metres through the council's prior approval process. These rights are restricted in conservation areas, on listed buildings and where earlier extensions have used them up. We check your position at the start."),
  ("What is a lawful development certificate?", "A certificate from the council confirming that work is permitted development and does not need planning permission. It is not compulsory, but it gives you certainty before you build and is useful when you come to sell. We prepare and submit these regularly."),
  ("How long does planning permission take?", "Councils aim to decide householder applications within eight weeks of validating them, and major applications within 13 weeks. Some councils take longer in busy periods. We follow up with the planning officer for you and keep you updated."),
  ("Will my neighbours be told?", "Yes. The council writes to neighbours or puts up a site notice, and they normally have 21 days to comment. It often helps to tell them about your plans first, and we can advise on how a design affects them."),
  ("What if the council asks for changes?", "That is part of the job. We discuss any concerns with the planning officer and, where it helps, revise the drawings during the application rather than letting it be refused."),
  ("What happens if permission is refused?", "You can appeal to the Planning Inspectorate (for householder applications, within 12 weeks of the decision), revise the design to address the reasons for refusal and apply again, or ask the council for pre-application advice. We will recommend the best route based on the reasons given."),
  ("What is a pre-application enquiry?", "A request to the council for its view on a proposal before a full application is made. It is usually paid. It can be worthwhile for larger or sensitive schemes, and we can tell you whether it is worth it for yours."),
  ("My house is in a conservation area. Does that change things?", "Yes. Permitted development rights are more limited in conservation areas, and some streets have extra controls (called Article 4 directions). Listed buildings also need listed building consent. Design matters even more, and we know the local guidance well."),
  ("How long does planning permission last?", "Normally three years from the date of the decision. Work has to start within that time.")]),
 ("Extensions and lofts", [
  ("Can I extend a semi-detached house?", "Yes. Single storey rear extensions are often possible under permitted development. Side and two storey extensions usually need planning permission. We will go through the options for your property when we meet."),
  ("Do I need planning permission for a loft conversion?", "Many loft conversions are permitted development, provided the extra roof space is no more than 40 cubic metres on a terraced house or 50 cubic metres on a detached or semi-detached house. Dormers facing the road need permission, as do most roof changes in conservation areas."),
  ("Do I need building regulations approval?", "Almost always. Extensions, loft conversions and garage conversions need building regulations approval even when they do not need planning permission. We prepare the building control drawings and specification after planning approval."),
  ("Do I need a party wall agreement?", "If the work involves a shared wall, or digging foundations close to a neighbour's, the Party Wall Act means you must give your neighbours notice before you start: two months for work on a shared wall and one month for excavations. We point out where it applies and can recommend party wall surveyors."),
  ("Do you work with structural engineers?", "Yes. We coordinate the structural design with engineers we work with regularly, so the drawings your builder receives are complete.")]),
 ("Working with us", [
  ("How much will it cost?", f"Every project is different, so we talk fees through with you in person once we understand what you want to do, and then confirm a fixed quote. Council application fees are paid separately. Call <a href=\"tel:{PHONE_TEL}\">{PHONE}</a> for a chat."),
  ("Do you deal with the council for me?", "Yes. We submit the application as your agent and deal with the planning officer from start to finish, so you do not have to."),
  ("Do you prepare building control drawings?", "Yes. After planning approval we prepare the detailed drawings needed for building regulations, including construction details, specification and drainage, and coordinate structural calculations where needed."),
  ("Can you recommend a builder?", "Yes. We have worked with reliable builders across North London and Hertfordshire for many years and are happy to suggest some when you reach the build stage."),
  ("Can I see work you have done near me?", "Yes. Our <a href=\"projects.html\">projects page</a> shows hundreds of approved projects on a map and in a list, each linked to the council's record. Search by street, town or type of work."),
  ("Which areas do you cover?", "Mainly North London and Hertfordshire, and further afield by arrangement. See <a href=\"areas.html\">areas we cover</a>.")])]
# Home page: the questions clients ask most, with short, simple answers (the FAQ page has the detail).
HOME_FAQ = [
  ("Do I need planning permission?", "Not always. Many single storey rear extensions, loft conversions and garden rooms can be built without a full application, under what are called permitted development rights. It depends on your house, any earlier extensions and whether you are in a conservation area. We check this for you at the first visit."),
  ("How do we get started?", f"Call <a href=\"tel:{PHONE_TEL}\">{PHONE}</a> or <a href=\"contact.html\">send us a message</a>. We visit your home, listen to what you want and tell you honestly what is likely to be approved. Then we measure up, draw the plans and submit them."),
  ("How long does planning permission take?", "Usually around eight weeks from when the council registers the application. We deal with the council throughout and keep you updated until the decision."),
  ("How much will it cost?", f"Every project is different, so we talk fees through with you in person and then give you a fixed quote. Call <a href=\"tel:{PHONE_TEL}\">{PHONE}</a> for a chat."),
  ("Do you deal with the council for me?", "Yes. We submit the application on your behalf and deal with the planning officer from start to finish, so you don't have to."),
  ("Do I need building regulations approval too?", "Almost always, yes, even when you don't need planning permission. Once planning is approved, we prepare the building control drawings your builder needs.")]
_FAQ_ALL = {q: a for _g, items in FAQ for q, a in items}
def faq_item(q, a, open_=False): return f'<details{" open" if open_ else ""}><summary>{q}</summary><p>{a}</p></details>'
def faq_list(qs): return '<div class="faq">' + "".join(faq_item(q, _FAQ_ALL[q]) for q in qs) + '</div>'

# The home page figure counts every approval in data/projects.js, rounded down to the nearest 50,
# so it updates by itself whenever the project data is rebuilt.
APPROVAL_COUNT = sum(len(p.get("approvals", [])) for p in PROJECTS) // 50 * 50

pages = {}
LEAFLET = '<link rel="stylesheet" href="css/vendor/leaflet.css">\n<link rel="stylesheet" href="css/vendor/MarkerCluster.css">\n'
MAPJS = ("js/vendor/leaflet.js", "js/vendor/leaflet.markercluster.js", "js/map.js")

# ---------------- Home ----------------
pages["index.html"] = shell("index.html",
 "Town & Country Planning Ltd | Planning drawings and permission, North London and Hertfordshire",
 "Independent planning and design practice in Cockfosters. Extensions, loft conversions and new homes taken from first idea to planning approval and building control since 2005. Call 07843 561129.",
 hero("We design it, draw it and take it through planning.",
      "An independent practice in Cockfosters. Since 2005 we have designed extensions, loft conversions and new homes across North London and Hertfordshire, and taken them through planning.",
      f'<div class="actions"><a class="btn btn-accent" href="projects.html">See our projects</a><a class="btn btn-ghost" href="tel:{PHONE_TEL}">Call {PHONE}</a></div>', slides=True)
 + '''<section class="trust"><div class="wrap">
<div><strong>Since 2005</strong><span>Independent, based in Cockfosters</span></div>
<div><strong>''' + str(APPROVAL_COUNT) + '''+ planning approvals</strong><span>Across London and Hertfordshire</span></div>
<div><strong>One team, start to finish</strong><span>Survey, design, planning, building control</span></div>
<div><strong>Built on recommendation</strong><span>Clients return and refer their friends</span></div>
</div></section>
<section class="section"><div class="wrap">
<div class="section-head"><div class="stack"><span class="label">What are you planning?</span><h2>From a rear extension to a new home</h2></div><a class="more" href="projects.html#planner">Not sure? Find work like yours</a></div>
''' + service_tiles() + '''
</div></section>
<section class="section band"><div class="wrap">
<div class="section-head"><div class="stack"><span class="label">Our work</span><h2>Recent approved projects</h2></div><a class="more" href="projects.html">Search all projects on the map</a></div>
''' + featured_carousel() + '''
</div></section>
<section class="section"><div class="wrap why">
<div class="stack" style="gap:20px"><span class="label">Why us</span><h2>Good design, and the planning knowledge to get it approved.</h2>
<p class="lede">We design something that works for you and suits your house, your street and the council's policies. Then the same small team handles the application, so you always know who you are talking to and where it stands.</p>
<div><a class="more" href="about.html">More about us</a></div>
<a class="press-mini" href="about.html#press"><img src="img/press/essential-kitchen-jan-2017.jpg" alt="" width="490" height="650" loading="lazy"><span><small>As featured in</small><strong>Essential Kitchen Bathroom Bedroom</strong><span>January 2017</span></span></a></div>
<div class="facts"><div><strong>Honest advice</strong><span>What is likely to be approved, before you spend money</span></div><div><strong>Local knowledge</strong><span>Years of applications with the same councils</span></div><div><strong>Clear drawings</strong><span>Produced in CAD for planners and builders</span></div><div><strong>Kept informed</strong><span>Updates at every stage of the application</span></div></div>
</div></section>
<section class="section band-navy"><div class="wrap stack" style="gap:48px">
<div class="section-head" style="margin:0"><div class="stack"><span class="label">How we work</span><h2>Five steps from idea to approval</h2></div><a class="more" href="process.html">How we work</a></div>
''' + timeline() + '''
</div></section>
<section class="section band" id="reviews"><div class="wrap">
<div class="section-head"><div class="stack"><span class="label">Client reviews</span><h2>What our clients say</h2></div><a class="more" href="reviews.html">All reviews</a></div>
''' + reviews_carousel() + '''
</div></section>
<section class="section"><div class="wrap" style="max-width:900px">
<div class="section-head"><div class="stack"><span class="label">Questions</span><h2>Frequently asked questions</h2></div><a class="more" href="faq.html">All questions</a></div>
''' + '<div class="faq">' + "".join(faq_item(q, a, k == 0) for k, (q, a) in enumerate(HOME_FAQ)) + '</div>' + '''
</div></section>
''' + CLOSING,
 scripts=("js/carousel.js",))

# ---------------- Projects and map (one page) ----------------
pages["projects.html"] = shell("projects.html", "Projects and map | Town & Country Planning Ltd",
 "Search hundreds of approved extensions, loft conversions, new homes and conversions across North London and Hertfordshire, on a map or in a list, each linked to the council's decision.",
 page_head("Projects and map", "Projects we have taken through planning", "Every project here received planning approval. Search once and the map and the list both update. Select a pin or Show on map to see each job and its council record.")
 + f'''<section class="section"><div class="wrap">
<div class="pm-head"><p class="pm-help" hidden><button type="button" class="btn btn-line" id="pl-open" aria-expanded="false" aria-controls="planner">Not sure what to search for? Answer a few quick questions</button></p></div>
{planner()}
{filters(True)}
<div class="map-wrap pm-map"><div id="map" role="region" aria-label="Map of the projects listed below"></div></div>
<p class="muted pm-note">Numbers on the map show several projects close together: select one to zoom in.</p>
<div class="grid" id="project-list"></div>
<div class="load-more"><button type="button" class="btn btn-line" id="project-more" hidden>Show more projects</button></div>
</div></section>
<section class="section band"><div class="wrap">
<div class="section-head"><div class="stack"><span class="label">Featured projects</span><h2>A closer look</h2><p class="muted">Photos, the planning decision and the story behind some of our projects.</p></div></div>
{featured_carousel()}
</div></section>''' + CLOSING, extra_head=LEAFLET,
 scripts=("data/projects.js", "data/featured.js", "js/projects.js", "js/planner.js", "js/suggest.js") + MAPJS + ("js/carousel.js",))

# ---------------- Services ----------------
SV = [("extensions", "Extensions", "An extension is the most common way to gain space without moving. We design single and two storey rear extensions, side returns, wraparounds and over-garage extensions that suit the house and stand a strong chance of approval. Many single storey extensions can be built under permitted development; we check that first, because it can save you time and fees.",
       ["Single and two storey rear extensions", "Side return and wraparound extensions", "Over-garage extensions", "Front porches", "Kitchen and open-plan reconfiguration"]),
      ("lofts", "Loft conversions", "A loft conversion can add a bedroom and bathroom with little loss of garden. We design dormer, L-shaped dormer, hip to gable and mansard conversions, and advise where a loft can go ahead under permitted development and where an application is needed.",
       ["Rear dormers and L-shaped dormers", "Hip to gable conversions", "Mansard conversions", "Rooflight conversions", "Combined extension and loft schemes"]),
      ("new-build", "New homes", "We take replacement dwellings, new homes on residential plots and small developments from first sketches to planning consent, including the supporting statements councils expect, and appeals where a scheme has been refused.",
       ["Replacement dwellings", "New homes on garden or infill plots", "Small residential developments", "Design and access statements", "Planning appeals", "Discharge of conditions"]),
      ("conversions", "Conversions and change of use", "Converting existing space is often the most cost-effective way to add a room. We prepare applications for garage and basement conversions, house to flat conversions and changes of use from commercial to residential.",
       ["Garage conversions", "Basement conversions", "House to flat conversions", "Commercial to residential", "Change of use applications"]),
      ("outbuildings", "Garden rooms and outbuildings", "Many garden offices and outbuildings do not need planning permission, depending on their size and position. We confirm what applies to your property and, where permission is needed, for example in a conservation area, we prepare and manage the application.",
       ["Garden offices and studios", "Annexes", "Pool houses", "Stores and workshops"]),
      ("consultancy", "Planning advice and appeals", "Sometimes the first step is advice rather than drawings. We assess the likely outcome of an application, suggest changes that would improve its chances, check permitted development rights and prepare planning statements. If a scheme has been refused, we advise on whether to revise it or appeal.",
       ["Pre-application advice", "Permitted development checks", "Planning and householder statements", "Appeals to the Planning Inspectorate"]),
      ("building-control", "Building control drawings", "After planning approval, the work needs building regulations approval. We prepare the detailed drawings and specification your builder needs to price and build correctly, coordinating structural design with engineers we work with regularly.",
       ["Building regulation drawings", "Specification of materials", "Structural coordination", "Drainage layouts", "Responses to building control queries"])]
SVQ = {"extensions": "q=extension", "lofts": "q=loft", "new-build": "type=New+homes", "conversions": "q=conversion",
       "outbuildings": "type=Outbuildings+and+garages", "consultancy": "", "building-control": ""}
sv_html = "".join(f'''<section class="section{" band" if i % 2 else ""}" id="{a}"><div class="wrap split" style="align-items:center">
<div class="prose"><span class="label">{i+1:02d}</span><h2>{t}</h2><p>{d}</p><div><h3 style="font-size:1rem;margin:8px 0">Includes</h3><ul class="list-cols">{"".join(f"<li>{x}</li>" for x in L)}</ul></div><p><a class="more" href="projects.html?{SVQ[a]}#project-list">See examples</a></p></div>
<div class="ph" style="aspect-ratio:4/3"><span>Photo: {t.lower()}</span></div>
</div></section>''' for i, (a, t, d, L) in enumerate(SV))
pages["services.html"] = shell("services.html", "Services | Town & Country Planning Ltd",
 "Extensions, loft conversions, new homes, conversions, garden rooms, planning advice, appeals and building control drawings in North London and Hertfordshire.",
 page_head("Services", "Everything from first sketch to building control", "Whether it is a porch or a new house, we provide the design and planning work your project needs, and stay with it through building control.")
 + sv_html + CLOSING)

# ---------------- Areas hub ----------------
def area_card(a):
    return f'<a class="area-card" href="area-{a[0]}.html"><span class="label">{a[5]}</span><h3>{a[1]}</h3><span class="towns">{", ".join(a[6][:5])} and nearby</span><span class="go">Projects and towns in {a[1]}</span></a>'
further = ", ".join(n for n, l, _ in OTHER_TILES if l)
pages["areas.html"] = shell("areas.html", "Areas we cover | Town & Country Planning Ltd",
 "Planning drawings and applications across Barnet, Hertsmere, Enfield, Welwyn Hatfield, Haringey, Watford, Harrow, East Herts, Broxbourne and beyond.",
 page_head("Areas we cover", "Local to Cockfosters, trusted across London and Hertfordshire", "We have prepared applications for councils across North London and Hertfordshire. Knowing how each council approaches extensions, lofts and new homes helps us design schemes that suit local policy.")
 + '<section class="section"><div class="wrap areas-layout"><div class="stack" style="gap:16px"><h2>Where our projects are</h2><p class="lede">The darker the square, the more of our projects are in that area. Select an area to see the towns we cover and projects nearby.</p></div>' + tilemap() + '</div></section>'
 + '<section class="section band"><div class="wrap"><div class="section-head"><div class="stack"><span class="label">Our main areas</span><h2>Choose your area</h2></div></div><div class="area-cards">' + "".join(area_card(a) for a in AREAS) + '</div></div></section>'
 + f'<section class="section" id="further"><div class="wrap split"><div class="prose"><span class="label">Further afield</span><h2>Not on the list?</h2><p>We have also worked in {further}, and we are happy to look at projects elsewhere in London and the Home Counties. Call us to talk about your property.</p></div><div class="stack" style="justify-content:center"><div class="actions"><a class="btn btn-navy" href="tel:{PHONE_TEL}">Call {PHONE}</a><a class="btn btn-line" href="contact.html">Send an enquiry</a></div></div></div></section>'
 + CLOSING)

# ---------------- Area pages ----------------
for i, a in enumerate(AREAS):
    slug, name, short, lvl, grid, group, towns, council, portal = a
    others = [b for b in AREAS if b[0] != slug][:4]
    portal_html = f'<p>You can look up applications, including the plans we have submitted, on the <a href="{portal}" target="_blank" rel="noopener">{council} planning website</a>.</p>' if portal else f'<p>Applications here are decided by {council}. Each project below links to its public planning record.</p>'
    body = (page_head(f"Areas · {group}", f"Planning drawings and applications in {name}",
                      f"Extensions, loft conversions, new homes and conversions across {name}, from {towns[0]} to {towns[-1]}.")
     + f'''<section class="section"><div class="wrap split">
<div class="prose"><h2>Working with {council}</h2>
<p>{"Barnet is where most of our work is, and the area we know best." if lvl == 4 and slug == "barnet" else ("A large share of our projects are in " + name + "." if lvl >= 3 else "We regularly take on projects in " + name + ".")} We prepare applications that respond to the council's policies and design guidance, and we look carefully at conservation areas, the street scene and neighbours before a scheme is submitted.</p>
{portal_html}
<h3 style="margin-top:8px">Towns and neighbourhoods</h3>
<div class="town-chips">{"".join(f"<span>{t}</span>" for t in towns)}</div>
</div>
<div class="map-wrap map-small"><div id="map" role="region" aria-label="Map of approved projects in {name}" data-borough="{name}"></div></div>
</div></section>
<section class="section band"><div class="wrap">
<div class="section-head"><div class="stack"><span class="label">Projects in {name}</span><h2>Approved projects in {name}</h2></div><a class="more" href="projects.html">All projects</a></div>
<div class="grid" id="project-list" data-borough="{name}"></div><div class="load-more"><button type="button" class="btn btn-line" id="project-more" hidden>Show more projects</button></div>
</div></section>
<section class="section-sm"><div class="wrap"><div class="section-head" style="margin-bottom:20px"><h2 style="font-size:1.4rem">Nearby areas</h2><a class="more" href="areas.html">All areas</a></div><div class="area-cards">{"".join(area_card(b) for b in others)}</div></div></section>
''' + CLOSING)
    pages[f"area-{slug}.html"] = shell(f"area-{slug}.html", f"Planning drawings in {name} | Town & Country Planning Ltd",
        f"Extensions, loft conversions and new homes in {name}: {', '.join(towns[:4])} and nearby. Planning drawings and applications by Town & Country Planning Ltd. Call {PHONE}.",
        body, extra_head=LEAFLET, scripts=("data/projects.js", "data/featured.js", "js/projects.js") + MAPJS)

# ---------------- Process ----------------
pages["process.html"] = shell("process.html", "How we work | Town & Country Planning Ltd",
 "Our five step process from consultation to planning approval and building control, with answers to common planning questions.",
 '<section class="section band-navy"><div class="wrap stack" style="gap:48px"><div class="stack" style="gap:16px;max-width:760px"><span class="label">How we work</span><h1>From first conversation to approved plans</h1><p class="lede" style="color:var(--on-navy-muted)">Five clear steps, with one team handling everything and keeping you informed throughout.</p></div>'
 + timeline() + '</div></section>'
 + f'<section class="section" id="faq"><div class="wrap" style="max-width:900px"><div class="section-head"><div class="stack"><span class="label">Questions</span><h2>Common questions</h2></div><a class="more" href="faq.html">All questions</a></div>{faq_list(["Where do I start?", "Do I always need planning permission for an extension?", "How long does planning permission take?", "Do I need building regulations approval?"])}</div></section>' + CLOSING)

# ---------------- FAQ page ----------------
def _plain(a):
    import re
    return H.unescape(re.sub(r"<[^>]+>", "", a))
faq_ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _plain(a)}} for _g, items in FAQ for q, a in items]}) + '</script>\n'
faq_toc = "".join(f'<a href="#faq-{i}">{g}</a>' for i, (g, _x) in enumerate(FAQ))
faq_body = "".join(f'<section class="faq-group" id="faq-{i}" aria-labelledby="faq-{i}-h"><h2 id="faq-{i}-h">{g}</h2><div class="faq">' + "".join(faq_item(q, a) for q, a in items) + '</div></section>' for i, (g, items) in enumerate(FAQ))
pages["faq.html"] = shell("faq.html", "Frequently asked questions | Town & Country Planning Ltd",
 "Answers to common questions about planning permission, permitted development, loft conversions, extensions, building regulations, party walls and working with us.",
 page_head("FAQ", "Frequently asked questions", "Straight answers to the questions we are asked most. If yours is not here, call us: we are happy to talk it through.")
 + f'<section class="section"><div class="wrap faq-layout"><nav class="faq-toc" aria-label="Question topics"><span class="label">Topics</span>{faq_toc}</nav><div>{faq_body}</div></div></section>' + CLOSING,
 extra_head=faq_ld)

# ---------------- Fees ----------------
PROJ_OPTS = ["Rear or side extension", "Loft conversion", "Extension and loft", "Garage or garden room", "New build", "Not sure yet"]
def opts(q, vals, sel):
    return '<div class="opts">' + "".join(f'<button type="button" class="chip" data-q="{q}" data-v="{v}" aria-pressed="{"true" if v == sel else "false"}">{v}</button>' for v in vals) + '</div>'
pages["fees.html"] = shell("fees.html", "Fees | Town & Country Planning Ltd",
 "A guide to our design and planning fees for extensions, lofts, conversions and new homes.",
 page_head("Fees", "Estimate your design fee", "Three quick questions give you a guide to our fees for drawings and planning. We confirm a fixed quote once we have talked through your project.")
 + f'''<section class="section"><div class="wrap calc" id="fee-calc">
<div class="calc-q">
<fieldset><legend>1. What type of property?</legend>{opts("property", ["House", "Flat", "Commercial"], "House")}</fieldset>
<fieldset><legend>2. What are you planning?</legend>{opts("project", PROJ_OPTS, "Loft conversion")}</fieldset>
<fieldset><legend>3. How much do you need from us?</legend>{opts("pack", ["Planning drawings", "Planning and building control"], "Planning drawings")}</fieldset>
</div>
<aside class="estimate" aria-live="polite">
<span class="elabel">Your estimate</span>
<span class="price" id="fee-price">We'll quote by phone</span>
<span id="fee-summary"></span>
<strong>Included</strong>
<ul><li>Consultation at the property</li><li>Measured survey</li><li>Draft and final plans</li><li>Planning application managed with the council</li><li id="fee-bc" hidden>Building control drawings</li></ul>
<a class="btn btn-white" href="contact.html">Talk to us about your project</a>
<small>A guide only. The council's own application fee is paid separately.</small>
</aside>
</div></section>''' + CLOSING, scripts=("js/fees.js",))

# ---------------- Reviews ----------------
pages["reviews.html"] = shell("reviews.html", "Client reviews | Town & Country Planning Ltd",
 "What our clients say about working with Town & Country Planning Ltd on their extensions, loft conversions and new homes.",
 page_head("Reviews", "What our clients say", "Most of our work comes from recommendation, often from clients who come back for their next project.")
 + '<section class="section"><div class="wrap">' + reviews_carousel() + '</div></section>'
 + '<section class="section band"><div class="wrap"><div class="section-head"><div class="stack"><span class="label">All reviews</span><h2>Every review in full</h2></div></div>' + quotes(range(len(Q))) + '</div></section>' + CLOSING,
 scripts=("js/carousel.js",))

# ---------------- About ----------------
pages["about.html"] = shell("about.html", "About us | Town & Country Planning Ltd",
 "Independent planning and design practice in Cockfosters, Barnet, founded by Martin McGahon in 2005.",
 page_head("About us", "A small practice with a long record of approvals", "Town &amp; Country Planning Ltd was founded by Martin McGahon in 2005. From our base in Cockfosters we design and manage planning applications for homeowners, builders and developers across North London and Hertfordshire.")
 + '''<section class="section"><div class="wrap split" style="align-items:center">
<div class="prose">
<h2>How we have grown</h2>
<p>The practice has grown almost entirely through recommendation. Clients come back for their next project, and builders we work alongside introduce us to their customers.</p>
<p>We combine design with a detailed knowledge of local planning policy. That means proposals that suit the house and the street, and applications that are complete and clear when they reach the planning officer.</p>
<p>We stay involved after approval, preparing building control drawings and recommending builders and structural engineers we trust.</p>
</div>
<div class="ph" style="aspect-ratio:4/3"><span>Photo: the team or the office</span></div>
</div></section>
<section class="section press" id="press" aria-labelledby="press-h"><div class="wrap press-wrap">
<figure class="press-cover"><img src="img/press/essential-kitchen-jan-2017.jpg" alt="Cover of Essential Kitchen Bathroom Bedroom magazine, January 2017" width="490" height="650" loading="lazy"></figure>
<div class="stack" style="gap:16px"><span class="label">In the press</span><h2 id="press-h">As featured in Essential Kitchen Bathroom Bedroom</h2>
<p class="lede">Our work appeared in the January 2017 issue of <em>Essential Kitchen Bathroom Bedroom</em>, the UK magazine for kitchen, bathroom and bedroom design.</p></div>
</div></section>
<section class="section band"><div class="wrap">
<div class="section-head"><div class="stack"><span class="label">The team</span><h2>Who you will work with</h2></div></div>
<div class="team">
<div><div class="ph"><span>Photo</span></div><strong>Martin McGahon</strong><small>Founder</small></div>
<div><div class="ph"><span>Photo</span></div><strong>[Name]</strong><small>[Role]</small></div>
<div><div class="ph"><span>Photo</span></div><strong>[Name]</strong><small>[Role]</small></div>
<div><div class="ph"><span>Photo</span></div><strong>[Name]</strong><small>[Role]</small></div>
</div>
</div></section>
<section class="section"><div class="wrap">
<div class="section-head"><div class="stack"><span class="label">How we work</span><h2>What you can expect</h2></div></div>
<div class="values">
<div><h3>Personal service</h3><p>You deal with the same people from the first visit to the final drawing.</p></div>
<div><h3>Honest advice</h3><p>We tell you early what is likely to be approved, and what is not.</p></div>
<div><h3>Local knowledge</h3><p>Years of applications with the same councils, and the policies behind their decisions.</p></div>
<div><h3>Start to finish</h3><p>Survey, design, planning and building control, handled by one team.</p></div>
</div>
</div></section>''' + CLOSING)

# ---------------- Contact ----------------
pages["contact.html"] = shell("contact.html", "Contact us | Town & Country Planning Ltd",
 f"Call {PHONE} or email {EMAIL} about your extension, loft conversion or new home in North London or Hertfordshire.",
 f'''<section class="section band"><div class="wrap split" style="align-items:flex-start">
<div class="stack" style="gap:28px">
<div class="stack"><span class="label">Contact</span><h1>Let's talk about your project</h1><p class="lede">Whether your plans are clear or you are still exploring, call or send us a message and we will get back to you.</p></div>
<div class="contact-lines">
<div><span class="label">Telephone</span><br><a class="big" href="tel:{PHONE_TEL}">{PHONE}</a></div>
<div><span class="label">Email</span><br><a class="big" href="mailto:{EMAIL}">{EMAIL}</a></div>
<div><span class="label">Based in</span><br>Cockfosters, Barnet EN4</div>
<div><span class="label">Hours</span><br>Monday to Friday 9am to 6pm<br>Saturday 9am to 1pm</div>
<div><span class="label">Areas</span><br>North London and Hertfordshire. <a href="areas.html">See areas we cover</a>.</div>
</div>
</div>
<form class="enquiry" id="enquiry" novalidate>
<h2 style="font-size:1.4rem">Send us a message</h2>
<label for="f-name">Your name</label><input id="f-name" name="name" type="text" autocomplete="name" required>
<label for="f-contact">Phone or email</label><input id="f-contact" name="contact" type="text" autocomplete="email" required>
<label for="f-area">Town or postcode of the property</label><input id="f-area" name="area" type="text">
<label for="f-type">Type of project</label>
<select id="f-type" name="type"><option value="">Please choose</option><option>Single storey extension</option><option>Two storey extension</option><option>Loft conversion</option><option>Garage conversion</option><option>New home</option><option>Garden room or outbuilding</option><option>Planning advice</option><option>Building control drawings</option><option>Other or not sure</option></select>
<label for="f-msg">Tell us about your project</label><textarea id="f-msg" name="message" rows="4"></textarea>
<button class="btn btn-accent" type="submit">Send enquiry</button>
<p class="form-msg" id="f-status" aria-live="polite">We will never share your details.</p>
</form>
</div></section>''', scripts=("js/contact.js",))

for _i in range(len(FEATURED)):
    pages[feat_url(FEATURED[_i][1])] = featured_page(_i)

pages["404.html"] = shell("404.html", "Page not found | Town & Country Planning Ltd", "Page not found.",
 '<section class="section"><div class="wrap stack"><span class="label">404</span><h1>Page not found</h1><p class="lede">That page has moved or no longer exists.</p><div class="actions"><a class="btn btn-navy" href="index.html">Go to the homepage</a><a class="btn btn-line" href="projects.html">Browse projects</a></div></div></section>')

for name, doc in pages.items():
    open(os.path.join(OUT, name), "w").write(doc)

redirect = lambda target, title: f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>{title}</title><meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{SITE}{target}"><meta name="robots" content="noindex"></head><body><p>This page has moved to <a href="{target}">{target}</a>.</p></body></html>
'''
open(os.path.join(OUT, "gallery.html"), "w").write(redirect("projects.html", "Our projects"))
open(os.path.join(OUT, "map.html"), "w").write(redirect("projects.html", "Projects and map").replace("</head>", "<script>location.replace('projects.html' + (location.hash || '#map'));</script></head>"))
urls = [""] + [n for n in pages if n not in ("index.html", "404.html")]
open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
print("built", len(pages), "pages")
