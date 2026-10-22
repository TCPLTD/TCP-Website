"""Builds every HTML page of the site. Run from the repo root:  python3 tools/build_pages.py .
Shared layout (sidebar menu, footer) and all page text live here."""
import os, sys, json, html as H

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
SITE = "https://townandcountryplanningltd.co.uk/"
PHONE, PHONE_TEL, EMAIL = "07843 561129", "07843561129", "martin@tcpltd.net"
GOOGLE_REVIEWS = "https://www.google.com/search?q=Town+%26+Country+Planning+Ltd+Cockfosters"  # replace with the Google review link when available

NAV = [("index.html", "Home"), ("projects.html", "Projects"), ("map.html", "Project map"), ("services.html", "Services"),
       ("areas.html", "Areas we cover"), ("process.html", "How we work"), ("fees.html", "Fees"), ("reviews.html", "Reviews"),
       ("about.html", "About us"), ("contact.html", "Contact")]

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
        cls = f"lvl-{lvl}" if lvl else "lvl-1"
        style = f"grid-row:{r+1};grid-column:{c+1}" + ("" if lvl else ";opacity:0.55")
        cells[(r, c)] = f'<a class="{cls}" href="areas.html#further" style="{style}" title="{name}">{name}</a>'
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
<div><h3>Explore</h3><ul><li><a href="projects.html">Projects</a></li><li><a href="map.html">Project map</a></li><li><a href="services.html">Services</a></li><li><a href="fees.html">Fees</a></li><li><a href="reviews.html">Reviews</a></li></ul></div>
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
def quote_html(i):
    t, n, place = Q[i]
    t = t.replace("&hellip;", "\x00"); t = esc(t).replace("\x00", "&hellip;")
    return f'<figure class="quote"><span class="stars" aria-label="Five stars">★★★★★</span><blockquote>&ldquo;{t}&rdquo;</blockquote><figcaption>{esc(n)}, {esc(place)}</figcaption></figure>'
def quotes(idx): return '<div class="quotes">' + "".join(quote_html(i) for i in idx) + '</div>'
def reviews_top():
    return f'''<div class="reviews-top"><div><span class="label">Reviews</span><h3>Worked with us? We would value your review.</h3><p class="muted">Most of our work comes from recommendation. A short Google review helps the next homeowner find us.</p></div>
<div class="actions"><a class="btn btn-navy" href="{GOOGLE_REVIEWS}" target="_blank" rel="noopener">Review us on Google</a><a class="btn btn-line" href="{GOOGLE_REVIEWS}" target="_blank" rel="noopener">Read our Google reviews</a></div></div>'''

def filters(full=True):
    selects = ('<label class="fl"><span>Area</span><select id="project-area"><option value="">All areas</option></select></label>'
               '<label class="fl"><span>Year approved</span><select id="project-year"><option value="">Any year</option></select></label>'
               '<label class="fl"><span>Type of approval</span><select id="project-route"><option value="">Any approval</option></select></label>') if full else ''
    return (f'<div class="filter-panel"><div class="filter-row"><label class="fl fl-search"><span>Search</span>'
            f'<input id="project-search" type="search" placeholder="Street, town or type of work, e.g. loft or Potters Bar"></label>{selects}'
            f'<button type="button" class="btn btn-line btn-clear" id="project-clear" hidden>Clear filters</button></div>'
            f'<div class="filter-chips" id="project-types" role="group" aria-label="Type of work"></div></div>'
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

def hero(h1, sub, actions, label="Planning and design consultants · since 2005", art=True):
    right = f'<div class="hero-art">{HERO_ART}</div>' if art else ''
    return f'''<section class="hero"><div class="wrap"><div class="hero-copy"><span class="label">{label}</span><h1>{h1}</h1><p>{sub}</p>{actions}</div>{right}</div></section>'''

def page_head(label, h1, lede, cls="band"):
    return f'<section class="{cls} page-head"><div class="wrap stack"><span class="label">{label}</span><h1>{h1}</h1><p class="lede">{lede}</p></div></section>'

pages = {}
LEAFLET = '<link rel="stylesheet" href="css/vendor/leaflet.css">\n<link rel="stylesheet" href="css/vendor/MarkerCluster.css">\n'
MAPJS = ("js/vendor/leaflet.js", "js/vendor/leaflet.markercluster.js", "js/map.js")

# ---------------- Home ----------------
pages["index.html"] = shell("index.html",
 "Town & Country Planning Ltd | Planning drawings and permission, North London and Hertfordshire",
 "Independent planning and design practice in Cockfosters. Extensions, loft conversions and new homes taken from first idea to planning approval and building control since 2005. Call 07843 561129.",
 hero("We design it, draw it and take it through planning.",
      "Town &amp; Country Planning is an independent practice in Cockfosters. Since 2005 we have worked on hundreds of extensions, loft conversions and new homes across North London and Hertfordshire, from the first conversation to approved plans.",
      f'<div class="actions"><a class="btn btn-accent" href="projects.html">See our projects</a><a class="btn btn-ghost" href="tel:{PHONE_TEL}">Call {PHONE}</a></div>')
 + '''<section class="trust"><div class="wrap">
<div><strong>Since 2005</strong><span>Independent, based in Cockfosters</span></div>
<div><strong>500+ approved projects</strong><span>Across London and Hertfordshire</span></div>
<div><strong>One team, start to finish</strong><span>Survey, design, planning, building control</span></div>
<div><strong>Built on recommendation</strong><span>Clients return and refer their friends</span></div>
</div></section>
<section class="section"><div class="wrap intro">
<div class="stack" style="gap:20px">
<span class="label">About the practice</span>
<h2>Good design, and the planning knowledge to get it approved.</h2>
<p class="lede">A strong application starts with a design that suits the house, the street and the council's policies. We bring all three together, then manage the application so you are not left dealing with the council on your own.</p>
<p class="muted">We work mainly with homeowners, and also with builders, developers and commercial clients. Every project, from a porch to a new house, is handled personally by the same small team.</p>
<div class="facts"><div><strong>Local knowledge</strong><span>Years of applications with the same councils</span></div><div><strong>Clear drawings</strong><span>Produced in CAD for planners and builders</span></div><div><strong>Kept informed</strong><span>Updates at every stage of the application</span></div></div>
<div><a class="more" href="about.html">More about us</a></div>
</div>
<div class="mosaic"><div class="ph"><span>Photo: finished extension</span></div><div class="ph"><span>Photo: team on site</span></div><div class="ph"><span>Photo: drawings</span></div></div>
</div></section>
<section class="section band"><div class="wrap">
<div class="section-head"><div class="stack"><span class="label">What we do</span><h2>Services for every scale of project</h2></div><a class="more" href="services.html">All services</a></div>
''' + service_tiles() + '''
</div></section>
<section class="section"><div class="wrap">
<div class="section-head"><div class="stack"><span class="label">Recent approvals</span><h2>Projects we have taken through planning</h2><p class="muted">Every project shown received planning approval. Search by type or town.</p></div><a class="more" href="projects.html">View all projects</a></div>
''' + filters(False) + '''
<div class="grid" id="project-list" data-limit="6"></div>
</div></section>
<section class="section paper"><div class="wrap map-split">
<div class="stack" style="gap:20px"><span class="label">Project map</span><h2>See what we have done on your road</h2><p class="lede">Each pin is an approved project. Open one for photos, a short description and a link to the approved plans on the council's website.</p><div><a class="btn btn-navy" href="map.html">Open the full map</a></div></div>
<div class="map-wrap map-small"><div id="map" role="region" aria-label="Map of approved projects"></div></div>
</div></section>
<section class="section band-navy"><div class="wrap stack" style="gap:48px">
<div class="section-head" style="margin:0"><div class="stack"><span class="label">How we work</span><h2>Five steps from idea to approval</h2><p>Householder applications are normally decided within eight weeks of the council validating them.</p></div><a class="more" href="process.html">How we work</a></div>
''' + timeline() + '''
</div></section>
<section class="section"><div class="wrap areas-layout">
<div class="stack" style="gap:20px"><span class="label">Areas we cover</span><h2>Rooted in Barnet and Hertfordshire, working well beyond.</h2><p class="lede">Most of our work is within a few miles of Cockfosters, and we regularly take on projects across North London and Hertfordshire. Pick an area to see the towns we work in and projects nearby.</p><div><a class="btn btn-navy" href="areas.html">Explore areas</a></div></div>
''' + tilemap() + '''
</div></section>
<section class="section band" id="reviews"><div class="wrap">
<div class="section-head"><div class="stack"><span class="label">Client reviews</span><h2>What our clients say</h2></div><a class="more" href="reviews.html">All reviews</a></div>
''' + reviews_top() + quotes([0, 1, 3]) + '''
</div></section>
<section class="section-sm"><div class="wrap"><div class="cta-box"><div><span class="label">Fees</span><h2>What will my design cost?</h2><p>Answer three quick questions to see what is included for your type of project.</p></div><a class="btn btn-accent" href="fees.html">Estimate my fee</a></div></div></section>
''' + CLOSING,
 extra_head=LEAFLET, scripts=("data/projects.js", "js/projects.js") + MAPJS)

# ---------------- Projects ----------------
pages["projects.html"] = shell("projects.html", "Our projects | Town & Country Planning Ltd",
 "Approved extensions, loft conversions, new homes and conversions across North London and Hertfordshire. Search by town or type of work.",
 page_head("Projects", "Projects we have taken through planning", "Every project here received planning approval. Search by street, town or type of work, or choose an area.")
 + f'''<section class="section"><div class="wrap">
{filters(True)}
<div class="grid" id="project-list"></div>
<div class="load-more"><button type="button" class="btn btn-line" id="project-more" hidden>Show more projects</button></div>
</div></section>''' + CLOSING, scripts=("data/projects.js", "js/projects.js"))

# ---------------- Map ----------------
pages["map.html"] = shell("map.html", "Project map | Town & Country Planning Ltd",
 "Map of our approved planning projects across North London and Hertfordshire, with photos and links to the approved plans.",
 page_head("Project map", "Approved projects near you", "Every pin is a project that received planning approval. Numbers show where several projects sit close together: select one to zoom in. Pins mark the street, never the house.")
 + '''<section class="section-sm"><div class="wrap stack" style="gap:16px">
<div class="filter-panel map-filters"><div class="filter-row"><label class="fl fl-search"><span>Find a street or town</span><input id="map-search" type="search" placeholder="e.g. Potters Bar, EN4 or loft"></label>
<label class="fl"><span>Type of work</span><select id="map-type"><option value="">All types</option></select></label>
<label class="fl"><span>Area</span><select id="map-area"><option value="">All areas</option></select></label>
<button type="button" class="btn btn-line btn-clear" id="map-reset" hidden>Reset map</button></div>
<p class="map-count" id="map-count" aria-live="polite"></p></div>
<div class="map-wrap"><div id="map" role="region" aria-label="Map of approved projects"></div></div>
<p class="muted">Prefer a list? <a href="projects.html">Search all projects</a> or <a href="areas.html">browse by area</a>.</p>
</div></section>''' + CLOSING, extra_head=LEAFLET, scripts=("data/projects.js",) + MAPJS)

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
sv_html = "".join(f'''<section class="section{" band" if i % 2 else ""}" id="{a}"><div class="wrap split" style="align-items:center">
<div class="prose"><span class="label">{i+1:02d}</span><h2>{t}</h2><p>{d}</p><div><h3 style="font-size:1rem;margin:8px 0">Includes</h3><ul class="list-cols">{"".join(f"<li>{x}</li>" for x in L)}</ul></div><p><a class="more" href="projects.html">See examples</a></p></div>
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
        body, extra_head=LEAFLET, scripts=("data/projects.js", "js/projects.js") + MAPJS)

# ---------------- Process + FAQ ----------------
FAQ = [("Planning permission", [
  ("Do I always need planning permission for an extension?", "Not always. Many extensions can be built under permitted development rights. As a guide, a single storey rear extension can go out 3 metres on a terraced or semi-detached house and 4 metres on a detached house, or up to 6 and 8 metres through the council's prior approval process. These rights are restricted in conservation areas, on listed buildings and where earlier extensions have used them up. We check your position at the start."),
  ("How long does planning permission take?", "Councils aim to decide householder applications within eight weeks of validating them, and major applications within 13 weeks. Some councils take longer in busy periods. We follow up with the planning officer for you and keep you updated."),
  ("What happens if permission is refused?", "You can appeal to the Planning Inspectorate (for householder applications, within 12 weeks of the decision), revise the design to address the reasons for refusal and apply again, or ask the council for pre-application advice. We will recommend the best route based on the reasons given."),
  ("What is a pre-application enquiry?", "A request to the council for its view on a proposal before a full application is made. It is usually paid. It can be worthwhile for larger or sensitive schemes, and we can tell you whether it is worth it for yours.")]),
 ("Extensions and lofts", [
  ("Can I extend a semi-detached house?", "Yes. Single storey rear extensions are often possible under permitted development. Side and two storey extensions usually need planning permission. We will go through the options for your property when we meet."),
  ("Do I need planning permission for a loft conversion?", "Many loft conversions are permitted development, provided the extra roof space is no more than 40 cubic metres on a terraced house or 50 cubic metres on a detached or semi-detached house. Dormers facing the road need permission, as do most roof changes in conservation areas.")]),
 ("Working with us", [
  ("How much does it cost?", "Fees depend on the type and size of project. We give you a fixed quote once we understand what you want to do. Council application fees are paid separately. Our <a href=\"fees.html\">fees page</a> gives a guide."),
  ("Do you prepare building control drawings?", "Yes. After planning approval we prepare the detailed drawings needed for building regulations, including construction details, specification and drainage, and coordinate structural calculations where needed."),
  ("Can you recommend a builder?", "Yes. We have worked with reliable builders across North London and Hertfordshire for many years and are happy to suggest some when you reach the build stage."),
  ("Which areas do you cover?", "Mainly North London and Hertfordshire, and further afield by arrangement. See <a href=\"areas.html\">areas we cover</a>.")])]
faq_html = "".join(f'<h3>{g}</h3>' + "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in items) for g, items in FAQ)
pages["process.html"] = shell("process.html", "How we work | Town & Country Planning Ltd",
 "Our five step process from consultation to planning approval and building control, with answers to common planning questions.",
 '<section class="section band-navy"><div class="wrap stack" style="gap:48px"><div class="stack" style="gap:16px;max-width:760px"><span class="label">How we work</span><h1>From first conversation to approved plans</h1><p class="lede" style="color:var(--on-navy-muted)">Five clear steps, with one team handling everything and keeping you informed throughout.</p></div>'
 + timeline() + '</div></section>'
 + f'<section class="section" id="faq"><div class="wrap faq" style="max-width:900px"><span class="label">Questions</span><h2 style="margin-top:12px">Common questions</h2>{faq_html}</div></section>' + CLOSING)

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
 + '<section class="section"><div class="wrap">' + reviews_top() + quotes(range(len(Q))) + '</div></section>' + CLOSING)

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

pages["404.html"] = shell("404.html", "Page not found | Town & Country Planning Ltd", "Page not found.",
 '<section class="section"><div class="wrap stack"><span class="label">404</span><h1>Page not found</h1><p class="lede">That page has moved or no longer exists.</p><div class="actions"><a class="btn btn-navy" href="index.html">Go to the homepage</a><a class="btn btn-line" href="projects.html">Browse projects</a></div></div></section>')

for name, doc in pages.items():
    open(os.path.join(OUT, name), "w").write(doc)

redirect = lambda target, title: f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>{title}</title><meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{SITE}{target}"><meta name="robots" content="noindex"></head><body><p>This page has moved to <a href="{target}">{target}</a>.</p></body></html>
'''
open(os.path.join(OUT, "gallery.html"), "w").write(redirect("projects.html", "Our projects"))
open(os.path.join(OUT, "faq.html"), "w").write(redirect("process.html#faq", "How we work"))
urls = [""] + [n for n in pages if n not in ("index.html", "404.html")]
open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
print("built", len(pages), "pages")
