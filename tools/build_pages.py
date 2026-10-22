import os, sys, json
OUT = sys.argv[1]
SITE = "https://townandcountryplanningltd.co.uk/"
NAV = [("projects.html","Projects"),("map.html","Map"),("services.html","Services"),("process.html","How we work"),("fees.html","Fees"),("about.html","About"),("contact.html","Contact")]
AREAS = "Barnet, Enfield, Hertsmere, Harrow, Welwyn Hatfield, East Herts and the surrounding areas"

def page(fname, title, desc, body, extra_head="", scripts=()):
    nav = "\n".join(f'<a href="{h}"{" aria-current=\"page\"" if h==fname else ""}>{t}</a>' for h,t in NAV)
    canon = SITE if fname=="index.html" else SITE+fname
    ld = ""
    if fname == "index.html":
        ld = '<script type="application/ld+json">' + json.dumps({
            "@context":"https://schema.org","@type":"ProfessionalService","name":"Town & Country Planning Ltd",
            "url":SITE,"telephone":"+447843561129","email":"martin@tcpltd.net","foundingDate":"2009",
            "address":{"@type":"PostalAddress","addressLocality":"Cockfosters, Barnet","postalCode":"EN4","addressCountry":"GB"},
            "areaServed":["Barnet","Enfield","Hertsmere","Harrow","Welwyn Hatfield","East Hertfordshire"],
            "description":"Planning drawings and planning applications for extensions, loft conversions and new builds in North London and Hertfordshire."}) + '</script>'
    sc = "\n".join(f'<script src="{s}"></script>' for s in scripts)
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&amp;family=Inter:wght@400;500;600&amp;display=swap">
<link rel="stylesheet" href="css/site.css">
{extra_head}{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
<div class="wrap">
<a class="brand" href="index.html" aria-label="Town &amp; Country Planning Ltd, home">
<span class="brand-mark" aria-hidden="true">T&amp;C</span>
<span class="brand-name">Town &amp; Country<span>Planning Ltd</span></span>
</a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
<nav class="nav" id="site-nav" aria-label="Main">
{nav}
<a class="btn btn-brick" href="tel:07843561129">Call 07843 561129</a>
</nav>
</div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
<div class="wrap">
<div class="stack" style="gap:6px">
<strong style="color:var(--ink)">Town &amp; Country Planning Ltd</strong>
<span>Cockfosters, Barnet EN4</span>
<span><a href="tel:07843561129">07843 561129</a> · <a href="mailto:martin@tcpltd.net">martin@tcpltd.net</a></span>
</div>
<nav aria-label="Footer">
{nav}
</nav>
<div>© <span id="year">2026</span> Town &amp; Country Planning Ltd<br>[Company number]</div>
</div>
</footer>
<script src="js/site.js"></script>
{sc}
</body>
</html>
'''

CTA = '''<section class="section"><div class="wrap">
<div class="cta-box"><div><h2>Talk to us about your plans</h2><p>Call or email and we will arrange a time to discuss your project.</p></div>
<div class="actions" style="flex:0 1 auto"><a class="btn btn-brick" href="tel:07843561129">Call 07843 561129</a><a class="btn btn-line" href="contact.html">Send an enquiry</a></div></div>
</div></section>'''

STEPS = [("Initial consultation","We meet at your home, talk through your ideas and check what is possible, including permitted development."),
("Measured survey","We carry out a full measured survey of the property."),
("Design and drawings","Existing and proposed plans drawn in CAD, with draft options to help you settle the design."),
("Planning submission","We submit the application and manage it with the council, keeping you informed throughout."),
("Building control","Once approved, we prepare detailed building regulation drawings so your builder can work with confidence.")]
steps_html = '<ol class="steps">' + "".join(f'<li><span class="n">{i}</span><strong>{t}</strong><p>{d}</p></li>' for i,(t,d) in enumerate(STEPS,1)) + '</ol>'

SERVICES = [("Extensions","Single and double storey, side return, wraparound and over-garage extensions."),
("Loft conversions","Dormer, hip to gable, mansard and rooflight lofts."),
("New build homes","Replacement dwellings, new homes on residential plots and small developments."),
("Garage and flat conversions","Garage, basement and house to flat conversions, and change of use."),
("Garden offices and outbuildings","Garden offices, studios, annexes and pool buildings."),
("Planning consultancy","Pre-application advice, permitted development checks, planning statements and appeals."),
("Building control drawings","Technical drawings and specifications, coordinated with structural engineers.")]
svc_html = '<div class="grid-tight">' + "".join(f'<a class="svc" href="services.html#{"extensions" if t.startswith("Loft") else t.split()[0].lower()}"><h3>{t}</h3><p>{d}</p></a>' for t,d in SERVICES) + '</div>'

Q = [("Following on from a recommendation from a friend and various talks with other architects we decided to instruct Martin to be the architect for our project, which was a single storey L-shape extension and loft conversion. Both myself and my wife had not done this before so it was reassuring Martin was there to listen and make our ideas and dreams into reality, and he closely worked with our builder at all times. I have already recommended Martin and will continue to do so.","Mr &amp; Mrs B. Jacobs","Borehamwood, Herts"),
("I first used the services of TCPL some years ago for a substantial extension to my home. From their knowledge and experience they were able to expertly advise and guide me through daunting stages to get the project started. They produced plans of the proposed extension, provided a set of specifications in accordance with regulations and made the required applications to the local authorities. Suffice to say I am currently using them again for a commercial conversion project and again the level of knowledge, advice and support is first class. I would not hesitate in recommending them to anyone embarking on a building project.","Mr &amp; Mrs Eaves","Hatfield, Herts"),
("&hellip; Mr McGahon proved to be extremely professional and quickly turned our ideas into reality. He was efficient, yet patient, answering our questions, and offering explanations and suggestions where necessary. As novices, he put us at ease, so when we finally embarked on the build, we were fully prepared and the building works were successfully completed without any problems. We have what we envisaged and more. I would be happy to recommend Town &amp; Country Planning Ltd.","Ms Hill","Potters Bar, Herts"),
("We were recommended to use Martin through a friend which for us was the best route as we knew he was great at his job and trustworthy. Having never carried out work on a property before, he was so helpful and explained everything that needed doing. He didn't only work on drawing up plans. He has a great relationship with the Council so had an insight into what we were and weren't allowed to carry out. Once we received our permission he helped us with everything else that needed carrying out too, which you don't get from all architects. He has helped us create our dream home.","Mr &amp; Mrs Beresford","Borehamwood, Herts"),
("I would just like to say a big thank you for the first class service you provided me with in regards to our loft conversion. From start to finish your knowledge and advice was a huge plus for us in maximising our options and I look forward to working with you in the spring when we commence the garage conversion.","Mr &amp; Mrs S. Loughlin","Barnet, Herts"),
("Martin at Town &amp; Country Planning Ltd have proven themselves again and again by producing innovative and creative designs and achieving planning consent for our projects. A personal service with a big practice feel.","Mr Harris, UK Room / Investco Properties","Mill Hill, London"),
("Martin from Town &amp; Country Planning Ltd had been recommended to us by some local friends. We found Martin incredibly helpful and he spent some time trying to understand our exact requirements. He explained in detail how our plans would be impacted by the council regulations to ensure we were making informed decisions. Martin has extensive experience with the council which enabled us to track progress and make changes that enabled us to secure permission in a timely manner.","Mr and Mrs Mohammed","Mill Hill, London"),
("Between me and my next door neighbour we have used this company no more than four times in as many years. This says it all really. Fantastic service, would recommend this company over and over again. Thanks for everything Town &amp; Country Planning Ltd.","Mr Austin","Borehamwood, Herts"),
("Our builder has a long standing work relationship with Martin and introduced us to him. We found Martin to be extremely competent as he drew up our plans quickly and accurately, and offered ideas and suggestions we had not thought of ourselves. Martin has experience and contacts with the local council so was able to guide us in what is acceptable and likely to get planning permission approval. We were so impressed with Martin's work on our first extension that we are now using him to draw up plans for our second!","Mr &amp; Mrs O'Grady","Borehamwood, Herts"),
("My wife and I have been delighted with the rear and loft extensions TCP have designed for our house. Both have been sympathetically detailed to suit the property and give a 'wow' factor. The information produced by TCP was accepted and approved on the first occasion by the Local Authority Planning and Building Control departments. This demonstrates TCP have a thorough knowledge and understanding of local building constraints. We had confidence in TCP from start to finish.","Mr, BEng (Hons) CEng MICE","Finchley, London")]
def quotes(idx): return '<div class="quotes">' + "".join(f'<figure class="quote"><blockquote>&ldquo;{Q[i][0]}&rdquo;</blockquote><figcaption>{Q[i][1]}, {Q[i][2]}</figcaption></figure>' for i in idx) + '</div>'

CHIPS = ["All","Extension","Loft","New build","Garage or garden room","Commercial"]
def filters(with_area=True):
    chips = "".join(f'<button type="button" class="chip" data-type-filter="{c}" aria-pressed="{"true" if c=="All" else "false"}">{"All types" if c=="All" else c}</button>' for c in CHIPS)
    area = '<label class="visually-hidden" for="project-area">Area</label><select id="project-area"><option value="">All areas</option></select>' if with_area else ''
    return f'<div class="filters"><label class="visually-hidden" for="project-search">Search projects</label><input id="project-search" type="search" placeholder="Search by street, town or type, e.g. loft or Barnet">{area}{chips}</div>'

pages = {}

pages["index.html"] = page("index.html",
 "Town & Country Planning Ltd | Planning drawings, Barnet and Hertfordshire",
 "Planning drawings and planning applications for extensions, loft conversions and new builds across Barnet, Enfield, Hertsmere and Hertfordshire since 2009. Call 07843 561129.",
 f'''<section class="band hero"><div class="wrap">
<div class="hero-copy">
<p class="eyebrow">Planning drawings and approvals · North London and Hertfordshire</p>
<h1>Extensions, lofts and new homes, designed and taken through planning for you.</h1>
<p class="lede">Since 2009 we have surveyed, drawn and secured planning approval for homes across Barnet, Enfield, Hertsmere and beyond. We manage the whole process with the council, from first visit to building control.</p>
<div class="actions"><a class="btn btn-green" href="map.html">See projects near you</a><a class="btn btn-line" href="contact.html">Arrange a meeting</a></div>
<p class="areas"><strong>Areas we cover:</strong> {AREAS}.</p>
</div>
<div class="hero-media"><div class="placeholder">[Hero photo: your best finished build]</div></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><div class="stack"><h2>Recent approved projects</h2><p class="lede">Search by what you're planning or where you live.</p></div><a href="projects.html">View all projects</a></div>
{filters(False)}
<div class="grid" id="project-list" data-limit="6"></div>
</div></section>

<section class="section band"><div class="wrap">
<div class="split" style="align-items:center">
<div class="stack"><h2>See what we've done on your road</h2><p class="lede">Every pin is a job that won planning approval. Tap one to see photos, what we did and a link to the approved plans on the council's website.</p><div><a class="btn btn-green" href="map.html">Open the full map</a></div></div>
<div class="map-wrap map-small"><div id="map" role="region" aria-label="Map of approved projects"></div></div>
</div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>What we do</h2><a href="services.html">All services</a></div>
{svc_html}
</div></section>

<section class="section band-green"><div class="wrap stack" style="gap:28px">
<div class="stack" style="gap:8px"><h2>Five steps from idea to approval</h2><p>Householder applications are normally decided within 8 weeks of the council validating them.</p></div>
{steps_html}
</div></section>

<section class="section"><div class="wrap">
<div class="cta-box"><div><h2>What will my design cost?</h2><p>Answer three quick questions to see what is included for your type of project.</p></div><a class="btn btn-brick" href="fees.html">Estimate my fee</a></div>
</div></section>

<section class="section band"><div class="wrap">
<div class="section-head"><h2>What clients say</h2><a href="about.html#testimonials">Read all testimonials</a></div>
{quotes([0,1,5])}
</div></section>
{CTA}''',
 extra_head='<link rel="stylesheet" href="css/vendor/leaflet.css">\n',
 scripts=("data/projects.js","js/projects.js","js/vendor/leaflet.js","js/map.js"))

pages["projects.html"] = page("projects.html","Our projects | Town & Country Planning Ltd",
 "Approved extensions, loft conversions, new builds and conversions across Barnet, Enfield, Hertsmere and Hertfordshire. Search by area or type.",
 f'''<section class="section"><div class="wrap">
<div class="stack" style="margin-bottom:28px"><h1>Our projects</h1><p class="lede">A selection of approved jobs. Search by street, town or type of work, or pick an area.</p></div>
{filters(True)}
<p class="result-count" id="project-count" aria-live="polite"></p>
<div class="grid" id="project-list"></div>
</div></section>
{CTA}''', scripts=("data/projects.js","js/projects.js"))

pages["map.html"] = page("map.html","Project map | Town & Country Planning Ltd",
 "Map of our approved planning projects across North London and Hertfordshire. See jobs on your road with photos and links to the approved plans.",
 '''<section class="section"><div class="wrap stack" style="gap:20px">
<div class="stack"><h1>Project map</h1><p class="lede">Every pin is a job that received planning approval. We show the street, never the house number. Each link goes to the public planning record on the council's website.</p></div>
<div class="map-wrap"><div id="map" role="region" aria-label="Map of approved projects"></div></div>
<p class="map-note">Prefer a list? <a href="projects.html">Browse and search all projects</a>.</p>
</div></section>''',
 extra_head='<link rel="stylesheet" href="css/vendor/leaflet.css">\n', scripts=("data/projects.js","js/vendor/leaflet.js","js/map.js"))

SV = [("extensions","Extensions and loft conversions","The most popular way to add space and value. Whether you want a larger kitchen, an extra bedroom or a home office, we design an extension that makes the best of your property and plot. Many extensions and lofts can be built under permitted development, so no planning application is needed. We check this at the start, which often saves time and cost. Where permission is needed, we manage the whole application.",
  ["Single and double storey rear extensions","Side return and wraparound extensions","Over-garage extensions","Front porches","Dormer and L-shaped dormer lofts","Hip to gable and mansard lofts","Rooflight lofts"]),
 ("new","New build homes","Full design and planning for replacement dwellings and new homes, from first ideas to planning consent. We work on replacement houses on existing plots, new homes in large gardens and small developments, and prepare appeals to the Planning Inspectorate where an application has been refused.",
  ["Replacement dwellings","New homes on residential plots","Pre-application advice","Design and access statements","Planning appeals","Discharge of conditions"]),
 ("garage","Garage and flat conversions","Converting an existing space is often the most cost-effective way to add a room. Many garage conversions fall under permitted development. We also prepare applications for house to flat conversions and changes of use across Barnet, Enfield and neighbouring boroughs.",
  ["Integral and detached garage conversions","Basement conversions","House to flat conversions","Commercial to residential","Change of use applications"]),
 ("garden","Garden offices and outbuildings","Many garden offices and outbuildings can be built without planning permission, depending on size and position. We check your property and advise. In conservation areas or on listed buildings, we prepare and manage the full application.",
  ["Garden offices and studios","Annexes","Pool buildings","Stores and workshops"]),
 ("planning","Planning consultancy","Sometimes you need advice before you commit to drawings. We advise on the likely outcome of an application, on design changes that would improve its chances, and on your permitted development rights, and we prepare the supporting documents.",
  ["Pre-application advice","Permitted development checks","Planning and householder statements","Appeal support","Commercial development advice"]),
 ("building","Building control drawings","After planning approval, building regulations approval is the next step. We prepare detailed drawings and specifications for building control so your builder can price and build the work correctly, coordinating with structural engineers where needed.",
  ["Building regulation drawings","Specification of materials","Structural coordination","Drainage design","Submission and responses to building control"])]
sv_html = "".join(f'''<section class="section{" band" if i%2 else ""}" id="{a}"><div class="wrap split">
<div class="prose"><h2>{t}</h2><p>{d}</p><p><a href="projects.html">See examples of our work</a></p></div>
<div><h3 style="margin-bottom:12px">Includes</h3><ul class="list-cols">{"".join(f"<li>{x}</li>" for x in L)}</ul></div>
</div></section>''' for i,(a,t,d,L) in enumerate(SV))
pages["services.html"] = page("services.html","Services | Town & Country Planning Ltd",
 "Extensions, loft conversions, new builds, conversions, garden offices, planning consultancy and building control drawings in North London and Hertfordshire.",
 f'''<section class="section band"><div class="wrap stack"><h1>Our services</h1><p class="lede">From a single storey kitchen extension to a new home or a planning appeal, we provide the design and planning service your project needs.</p></div></section>
{sv_html}
{CTA}''')

FAQ = [("Planning permission",[
 ("Do I always need planning permission for an extension?","Not always. Many extensions can be built under permitted development rights. As a guide, a single storey rear extension can go out 3 metres on a terraced or semi-detached house and 4 metres on a detached house, or up to 6 and 8 metres through the council's prior approval process. These rights are restricted in conservation areas, on listed buildings and where earlier extensions have used them up. We check your position at the start."),
 ("How long does planning permission take?","Councils aim to decide householder applications within 8 weeks of validating them, and major applications within 13 weeks. Some councils take longer in busy periods. We follow up with the planning officer on your behalf and keep you updated."),
 ("What happens if planning permission is refused?","You can appeal to the Planning Inspectorate (for householder applications, within 12 weeks of the decision), revise the design to deal with the reasons for refusal and apply again, or ask the council for pre-application advice. We will recommend the best route based on the reasons given."),
 ("What is a pre-application enquiry?","A request to the council for its view on a proposal before a full application is made. It is usually paid. It can be worth it for larger or sensitive schemes, and we can tell you whether it is worthwhile for yours and prepare it for you.")]),
("Extensions and lofts",[
 ("Can I extend a semi-detached house?","Yes. Single storey rear extensions are often possible under permitted development. Side and two storey extensions usually need planning permission. We will go through the options for your property when we meet."),
 ("Do I need planning permission for a loft conversion?","Many loft conversions are permitted development, provided the extra roof space is no more than 40 cubic metres on a terraced house or 50 cubic metres on a detached or semi-detached house. Dormers facing the road need permission, and so do most roof changes in conservation areas.")]),
("Working with us",[
 ("How much does it cost?","Fees depend on the type and size of the project. We give you a fixed quote once we understand what you want to do, covering everything from the survey to the planning decision. Council application fees are paid separately. You can get a guide on our <a href=\"fees.html\">fees page</a>."),
 ("Do you prepare building control drawings?","Yes. After planning approval we prepare the detailed drawings needed for building regulations, including construction details, specifications and drainage, and coordinate structural calculations where needed. These are quoted separately."),
 ("Can you recommend a builder?","Yes. We have worked with reliable builders across North London and Hertfordshire for many years and are happy to suggest some when you reach the build stage."),
 ("Which areas do you cover?",f"{AREAS}. We regularly work in Cockfosters, New Barnet, East Barnet, Hadley Wood, Southgate, Winchmore Hill, Finchley, Mill Hill, Potters Bar, Borehamwood and Hatfield. If you are unsure, just call.")])]
faq_html = "".join(f'<h3>{g}</h3>' + "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in items) for g,items in FAQ)
pages["process.html"] = page("process.html","How we work | Town & Country Planning Ltd",
 "Our five step process from initial consultation to planning approval and building control, plus answers to common planning questions.",
 f'''<section class="section band-green"><div class="wrap stack" style="gap:28px">
<div class="stack" style="gap:12px"><h1>How we work</h1><p class="lede" style="color:var(--on-green-muted)">Five steps take your project from first idea to planning approval and building control. We manage the council for you at every stage.</p></div>
{steps_html}
</div></section>
<section class="section" id="faq"><div class="wrap faq" style="max-width:860px;margin:0 auto">
<h2>Common questions</h2>
{faq_html}
</div></section>
{CTA}''')

PROJ_OPTS = ["Rear or side extension","Loft conversion","Extension and loft","Garage or garden room","New build","Not sure yet"]
def opts(q, vals, sel):
    return '<div class="opts">' + "".join(f'<button type="button" class="chip" data-q="{q}" data-v="{v}" aria-pressed="{"true" if v==sel else "false"}">{v}</button>' for v in vals) + '</div>'
pages["fees.html"] = page("fees.html","Fees | Town & Country Planning Ltd",
 "Get a guide to our design and planning fees for extensions, lofts, conversions and new builds.",
 f'''<section class="section band"><div class="wrap stack"><h1>Estimate your design fee</h1><p class="lede">Three quick questions give you a guide to our fees for drawings and planning. We confirm your exact quote once we have talked through your project.</p></div></section>
<section class="section"><div class="wrap calc" id="fee-calc">
<div class="calc-q">
<fieldset><legend>1. What type of property?</legend>{opts("property",["House","Flat","Commercial"],"House")}</fieldset>
<fieldset><legend>2. What are you planning?</legend>{opts("project",PROJ_OPTS,"Loft conversion")}</fieldset>
<fieldset><legend>3. How much do you need from us?</legend>{opts("pack",["Planning drawings","Planning and building control"],"Planning drawings")}</fieldset>
</div>
<aside class="estimate" aria-live="polite">
<span class="label">Your estimate</span>
<span class="price" id="fee-price">We'll quote by phone</span>
<span id="fee-summary"></span>
<strong>Included</strong>
<ul><li>Initial consultation</li><li>Measured survey</li><li>Draft and final plans</li><li>Planning application managed with the council</li><li id="fee-bc" hidden>Building control drawings</li></ul>
<a class="btn" href="contact.html">Talk to us about your project</a>
<small>A guide only. The council's own application fee is paid separately.</small>
</aside>
</div></section>''', scripts=("js/fees.js",))

pages["about.html"] = page("about.html","About us | Town & Country Planning Ltd",
 "Independent architectural planning consultancy in Cockfosters, Barnet, founded by Martin McGahon in 2009. Read what our clients say.",
 f'''<section class="section band"><div class="wrap split">
<div class="prose">
<h1>About us</h1>
<p class="lede">Town &amp; Country Planning Ltd is an independent architectural planning consultancy based in Cockfosters, Barnet, helping homeowners and developers across North London and Hertfordshire since 2009.</p>
<p>The practice was founded by Martin McGahon and has grown almost entirely through recommendation. We work mainly with homeowners who want to extend, convert or rebuild, and with developers and commercial clients on larger schemes. Whatever the size of the job, you get the same personal service.</p>
<p>Our strength is good design combined with a thorough knowledge of local planning policy and long working relationships with the councils we deal with. All drawings are produced in CAD, so builders, planners and building control officers can read them clearly.</p>
<p>We manage the whole process with the council and keep you informed at every stage. When it is time to build, we can recommend reliable builders and structural engineers we have worked with for years.</p>
</div>
<div class="stack">
<h2>Our team</h2>
<div class="team">
<div><div class="placeholder">[Photo]</div><strong>Martin McGahon</strong><small>Founder</small></div>
<div><div class="placeholder">[Photo]</div><strong>[Name]</strong><small>[Role]</small></div>
<div><div class="placeholder">[Photo]</div><strong>[Name]</strong><small>[Role]</small></div>
</div>
</div>
</div></section>
<section class="section"><div class="wrap">
<div class="grid-tight">
<div class="svc"><h3>Personal service</h3><p>Every project is different. We take time to understand what you need before we draw a line.</p></div>
<div class="svc"><h3>Local knowledge</h3><p>In-depth knowledge of planning policy in Barnet, Enfield, Hertsmere and neighbouring councils.</p></div>
<div class="svc"><h3>The whole process</h3><p>From survey to planning approval and building control, with progress updates throughout.</p></div>
<div class="svc"><h3>A strong approval record</h3><p>Our approvals reflect both our design work and our understanding of what councils will accept.</p></div>
</div>
</div></section>
<section class="section band" id="testimonials"><div class="wrap stack" style="gap:28px">
<h2>What clients say</h2>
{quotes(range(len(Q)))}
</div></section>
{CTA}''')

pages["contact.html"] = page("contact.html","Contact us | Town & Country Planning Ltd",
 "Call 07843 561129 or email martin@tcpltd.net to talk about your extension, loft conversion or new build in North London or Hertfordshire.",
 f'''<section class="section band"><div class="wrap split" style="align-items:flex-start">
<div class="stack" style="gap:24px">
<div class="stack"><h1>Contact us</h1><p class="lede">Whether you have a clear plan or are just exploring your options, call or send us a message and we will get back to you.</p></div>
<div class="contact-lines">
<div><span class="eyebrow">Telephone</span><br><a class="big" href="tel:07843561129">07843 561129</a></div>
<div><span class="eyebrow">Email</span><br><a class="big" href="mailto:martin@tcpltd.net">martin@tcpltd.net</a></div>
<div><span class="eyebrow">Based in</span><br>Cockfosters, Barnet EN4</div>
<div><span class="eyebrow">Hours</span><br>Monday to Friday 9am to 6pm<br>Saturday 9am to 1pm</div>
<div><span class="eyebrow">Areas we cover</span><br>{AREAS}.</div>
</div>
</div>
<form class="enquiry" id="enquiry" novalidate>
<h2 style="font-size:1.4rem">Send us a message</h2>
<label for="f-name">Your name</label><input id="f-name" name="name" type="text" autocomplete="name" required>
<label for="f-contact">Phone or email</label><input id="f-contact" name="contact" type="text" autocomplete="email" required>
<label for="f-area">Town or postcode of the property</label><input id="f-area" name="area" type="text">
<label for="f-type">Type of project</label>
<select id="f-type" name="type"><option value="">Please choose</option><option>Single storey extension</option><option>Two storey extension</option><option>Loft conversion</option><option>Garage conversion</option><option>New build</option><option>Garden office or outbuilding</option><option>Planning advice</option><option>Building control drawings</option><option>Other or not sure</option></select>
<label for="f-msg">Tell us about your project</label><textarea id="f-msg" name="message" rows="4"></textarea>
<button class="btn btn-brick" type="submit">Send enquiry</button>
<p class="form-msg" id="f-status" aria-live="polite">We will never share your details.</p>
</form>
</div></section>''', scripts=("js/contact.js",))

for name, html in pages.items():
    open(os.path.join(OUT, name), "w").write(html)

redirect = lambda target, title: f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>{title}</title><meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{SITE}{target}"><meta name="robots" content="noindex"></head><body><p>This page has moved to <a href="{target}">{target}</a>.</p></body></html>
'''
open(os.path.join(OUT,"gallery.html"),"w").write(redirect("projects.html","Our projects"))
open(os.path.join(OUT,"faq.html"),"w").write(redirect("process.html#faq","How we work"))
open(os.path.join(OUT,"404.html"),"w").write(page("404.html","Page not found | Town & Country Planning Ltd","Page not found.",
 '<section class="section"><div class="wrap stack"><h1>Page not found</h1><p class="lede">That page has moved or no longer exists.</p><div class="actions"><a class="btn btn-green" href="index.html">Go to the homepage</a><a class="btn btn-line" href="projects.html">Browse projects</a></div></div></section>'))
urls = ["", "projects.html","map.html","services.html","process.html","fees.html","about.html","contact.html"]
open(os.path.join(OUT,"sitemap.xml"),"w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(OUT,"robots.txt"),"w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
print("built", len(pages))
