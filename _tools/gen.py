#!/usr/bin/env python3
"""Generate Jekyll posts for the Quebec Governance Monitor site from the daily digest .txt files.

Usage: python3 _tools/gen.py [YYYY-MM-DD ...]   (no args = every day listed in TAGS)
Source format per day file (SRC/YYYY-MM-DD.txt):
  *Quebec Governance Daily – ...*        (title line)
  *Section heading FR / Section heading EN*
  *Headline as published*
  🇫🇷 French summary
  🇬🇧 English summary
  https://url
  💡🇫🇷 Pourquoi c’est important (optional; else taken from _data/why.json)
  💡🇬🇧 Why it matters (optional; else taken from _data/why.json)
  — Quebec Governance Monitor           (signature; skipped: the site footer signs each page in the reader's
                                         language, site.title_fr / site.title in _config.yml)
Why it matters rule (README step 3b; enforced by plain.py --strict): the line must add one thing the summary does not
say (the public stake, what to watch next, or the gap in the record) and never repeat a number from the summary.
Every fact is checked against the cached article.
Per story the post also shows, when present: the "Why it matters" line (_data/why.json, keyed by story URL)
and any "money in human terms" item whose story_url is that story (_data/money.json, run _tools/plain.py money).
Each language is wrapped in class="l-fr" / class="l-en" so the site's FR|EN toggle shows one at a time.
Headlines are language-neutral in the post body (shown as published in both modes).

The front matter also gets a structured `stories:` list that the homepage renders (featured stories, news by
category). Per story it combines the .txt with _data/story_meta.json (keyed by story URL: category, importance 1-5,
optional title_en / title_fr translations of the headline) and _data/why.json. The 3 stories with the highest
importance (ties keep digest order) get featured: 1..3. Missing metadata never fails: the category falls back to
HEADING_CATEGORY (section heading), then 'other'; importance defaults to 2.
"""
import html, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plain
SRC = os.environ.get("DIGEST_SRC", "/workspace/governance-digest")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_posts")
FR_MONTHS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]
EN_MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# Per-day topic tags (only when clearly applicable): it-digital, crown-corporations, procurement
TAGS = {"2026-10-21": ["crown-corporations"],
        "2026-10-22": ["it-digital", "crown-corporations"],
        "2026-10-23": ["it-digital", "crown-corporations", "procurement"],
        "2026-10-24": ["it-digital", "crown-corporations"],
        "2026-10-25": ["crown-corporations", "procurement"],
        "2026-10-26": [],
        "2026-10-27": ["crown-corporations", "procurement"],
        "2026-10-28": ["crown-corporations"],
        "2026-10-29": ["crown-corporations"],
        "2026-10-30": ["crown-corporations", "procurement"],
        "2026-10-31": ["it-digital", "crown-corporations"],
        "2026-11-01": ["crown-corporations"],
        "2026-11-02": ["it-digital", "crown-corporations"],
        "2026-11-03": ["crown-corporations", "it-digital"],
        "2026-11-04": ["crown-corporations", "procurement"],
        "2026-11-05": ["crown-corporations", "it-digital"],
        "2026-11-06": ["it-digital", "crown-corporations", "procurement"],
        "2026-11-07": ["crown-corporations", "procurement"],
        "2026-11-08": [],
        "2026-11-09": ["crown-corporations"],
        "2026-11-10": ["crown-corporations", "procurement"],
        "2026-11-11": ["it-digital", "crown-corporations", "procurement"],
        "2026-11-12": ["crown-corporations", "procurement"],
 "2026-11-13": ["crown-corporations", "procurement"],
 "2026-11-14": ["crown-corporations"]}
# Per-day one-line summary, (FR, EN), written only from that day's stories
SUMMARY = {
 "2026-10-21": ("Lion Électrique : perquisition de la GRC et dossiers de l’AMF; nouveau Conseil des ministres; tarifs d’Hydro-Québec pour les centres de données.",
                "Lion Électrique: RCMP search and AMF cases; new cabinet; Hydro-Québec data-centre rates."),
 "2026-10-22": ("Nominations dans la haute fonction publique; faille PHP : la SAQ, la STM et la SAAQ ferment leurs sites; suivis sur Lion Électrique et les recomptages.",
                "Senior civil-service appointments; PHP flaw: SAQ, STM and SAAQ lock their sites; follow-ups on Lion Électrique and the recounts."),
 "2026-10-23": ("Contrats TI de gré à gré et firmes étrangères; Hydro-Québec et SAQ; Marie-Claude Sarrazin (ex-commission Gallant) à la Justice.",
                "Untendered IT contracts and foreign firms; Hydro-Québec and the SAQ; Marie-Claude Sarrazin (ex-Gallant commission) at Justice."),
 "2026-10-24": ("Aide d’urgence en itinérance; la SAQ et Consignaction; l’Espace client d’Hydro-Québec hors ligne; FNZ et La Caisse; mandats des nouveaux ministres, dont l’audit des projets informatiques; projets d’infrastructures reportés.",
                "Emergency homelessness aid; the SAQ and Consignaction; Hydro-Québec’s customer accounts offline; FNZ and La Caisse; new ministers’ mandates, including an audit of IT projects; infrastructure projects delayed."),
 "2026-10-25": ("Contrôleurs routiers de la SAAQ de retour sur les routes; vente de vins américains à la SAQ; voie d’essais du TGV d’Alto; chirurgies reportées faute d’instruments stériles; PSPP absent de la rencontre avec les chefs autochtones; L’Ascension attend toujours Québec; sommes versées par Hydro-Québec à McKinsey et à d’autres firmes-conseils.",
                "SAAQ road controllers back on patrol; SAQ sale of American wines; Alto’s high-speed rail test track; surgeries postponed for lack of sterile instruments; PSPP absent from the meeting with Indigenous leaders; L’Ascension still waiting for Quebec; Hydro-Québec’s payments to McKinsey and other consulting firms."),
 "2026-10-26": ("L’UPAC enquête sur Rigaud (lanceur d’alerte); la RBQ retire la licence de Swimko; violence envers le personnel scolaire; attente pour les mammographies en Abitibi-Témiscamingue; BEI et déontologie pour un policier du SPVM; Montréal demande un contrôle des loyers; rencontre Premières Nations–premiers ministres; vaccination contre la grippe.",
                "UPAC investigates Rigaud (whistleblower); RBQ revokes Swimko’s licence; violence against school support staff; mammogram waits in Abitibi-Témiscamingue; BEI and ethics probes of an SPVM officer; Montreal asks for rent control; First Nations–First Ministers meeting; flu vaccination."),
 "2026-10-27": ("Tarifs des centres de données : la Cour supérieure annule les décrets de Québec; contrat d’urgence de gré à gré au Stade olympique; La Caisse achète une part des tours de Bell; PSPP privé de parole au sommet Canada-UE; soulèvement à Bordeaux; enquête du coroner sur les poids lourds; suivis : Lion Électrique, Vachon, discours d’ouverture et itinérance.",
                "Data-centre rates: Superior Court strikes down Quebec’s orders; emergency untendered contract at the Olympic Stadium; La Caisse buys into Bell’s towers; PSPP denied a speech at the Canada–EU summit; uprising at Bordeaux jail; coroner’s heavy-truck inquiry; follow-ups: Lion Électrique, Vachon, opening speech and homelessness."),
 "2026-10-28": ("Retraites anticipées et indemnités de départ pour réduire la fonction publique (selon des sources); Carney réplique à PSPP sur le sommet Canada-UE; projet de loi sur le changement d’heure; étude Cardus sur les fonds publics aux groupes militants; fautes dans des lettres de l’aide sociale; une résidence pour aînés fermera à Val-d’Or; rapport du coroner après la mort d’une fillette; branchements d’Hydro-Québec et grève; plaintes au RTC; suivi : livre blanc sur l’itinérance.",
                "Early retirement and severance to shrink the public service (according to sources); Carney hits back at PSPP over the Canada–EU summit; clock-change bill; Cardus study on public money for advocacy groups; errors in welfare letters; a Val-d’Or seniors’ residence to close; coroner’s report after a girl’s death; Hydro-Québec connections and the strike; RTC complaints; follow-up: homelessness white paper."),
 "2026-10-29": ("Deux proches de Fréchette nommés dans la haute fonction publique; la mégadéduction fédérale coûtera environ 1 milliard par année à Québec; 20 % des chirurgies au privé; deux enquêtes sur des décès d’enfants à la DPJ anglophone; Québec veut faire annuler la vente de 94 logements sociaux à Repentigny; démantèlement du poste 39 du SPVM; BAPE réclamé pour le terminal de QSL; Montréal en « mode rattrapage »; suivis : sommet Canada-UE, L’Ascension.",
                "Two Fréchette aides named to senior public-service posts; the federal mega-deduction will cost Quebec about $1 billion a year; 20% of surgeries in private clinics; two probes into child deaths at the English-language DPJ; Quebec seeks to cancel the sale of 94 social housing units in Repentigny; dismantling of SPVM station 39; BAPE sought for the QSL terminal; Montreal in “catch-up mode”; follow-ups: Canada–EU summit, L’Ascension."),
 "2026-10-30": ("L’AMP blâme la Société des traversiers pour quatre contrats de gré à gré; le TAT donne raison au syndicat en grève d’Hydro-Québec; tramway de Québec : travaux préparatoires dans les budgets, selon la Ville; Jacinthe-Eve Arel à l’Efficacité gouvernementale; la lieutenante-gouverneure défend son rôle; infrastructures d’eau et logement; un policier du poste 39 aurait effacé une preuve; Keel annule sa séance portes ouvertes à Sherbrooke; suivi : Dubé et Santé Québec.",
                "The AMP faults the ferry corporation (STQ) over four untendered contracts; the TAT sides with Hydro-Québec’s striking trades union; Quebec City tramway prep work on budget, the City says; Jacinthe-Eve Arel joins Government Efficiency; the lieutenant governor defends her role; water infrastructure and housing; a Station 39 officer allegedly erased evidence; Keel cancels its Sherbrooke open house; follow-up: Dubé and Santé Québec."),
 "2026-10-31": ("Churchill Falls : Terre-Neuve-et-Labrador refuse de renégocier l’entente; 44 postes abolis chez Santé Québec Chaudière-Appalaches; départs de médecins à Victoriaville et Dossier santé numérique; le chef du SPVM défend le changement de culture; Loto-Québec garde les appareils de loterie vidéo dans les bars de Rimouski; nouvelle alliance Canada-UE; Carney veut rencontrer PSPP; QS demande l’annulation de la nomination de Jacinthe-Eve Arel; Stéphan La Roche sous-ministre de la Culture.",
                "Churchill Falls: Newfoundland and Labrador refuses to renegotiate the deal; 44 positions cut at Santé Québec Chaudière-Appalaches; doctors leave Victoriaville amid the Digital Health Record rollout; SPVM chief defends culture change; Loto-Québec keeps video lottery terminals in Rimouski bars; new Canada–EU alliance; Carney wants to meet PSPP; QS demands Jacinthe-Eve Arel’s appointment be cancelled; Stéphan La Roche named deputy minister of Culture."),
 "2026-11-01": ("Hydro-Québec reconnaît des délais de raccordement plus longs en Abitibi-Témiscamingue; cinq morts en cinq ans chez le recycleur AIM; une fausse citation attribuée à Jacinthe-Eve Arel; élections partielles fédérales le 7 décembre, dont trois au Québec; trois maires veulent une base navale dans le Bas-Saint-Laurent; premier Sommet des Laurentides sur le climat.",
                "Hydro-Québec acknowledges longer connection delays in Abitibi-Témiscamingue; five deaths in five years at recycler AIM; a fake quote attributed to Jacinthe-Eve Arel; federal by-elections on Dec. 7, three in Quebec; three mayors want a naval base in the Lower St. Lawrence; first Laurentians Summit on climate."),
 "2026-11-02": ("Le PQ démantèle le ministère de la Cybersécurité et du Numérique et transfère ses employés au Conseil du trésor; état d’urgence à L’Isle-aux-Coudres après le bris du traversier de la STQ; Québec maintient trois jours de présence au bureau pour les fonctionnaires; temps de réponse en hausse chez les pompiers de Montréal; fermeture du Centre médical familial de Wakefield; feu vert au projet aurifère Windfall; suivis : PSPP accepte de rencontrer Mark Carney, à Québec, et prévoit son discours d’ouverture sans la lieutenante-gouverneure.",
                "The PQ dismantles the Ministry of Cybersecurity and Digital Affairs and moves its staff to the Treasury Board; state of emergency on Isle-aux-Coudres after the STQ ferry breaks down; Quebec keeps three office days a week for public servants; Montreal fire response times rise; Wakefield Family Medical Centre closes; green light for the Windfall gold project; follow-ups: PSPP agrees to meet Mark Carney, in Quebec City, and plans his opening speech without the lieutenant governor."),
 "2026-11-03": ("Hydro-Québec repousse à 2041 sa hausse de production et prévoit importer de l’électricité presque tout au long de son plan; primes de départ dans la haute fonction publique; Sébastien D’Astous promet des abolitions de postes; incertitude après la fermeture du PEQ; Montréal : sept policiers congédiés et règlement anti-insultes maintenu; fin des primes en RPA; suivis : dates proposées pour une rencontre Carney–St-Pierre Plamondon, Therrien ouvert à discuter du télétravail, QS dénonce le démantèlement du ministère de la Cybersécurité et du Numérique.",
                "Hydro-Québec pushes its production increase back to 2041 and plans to import electricity for almost all of its plan; severance payments in the senior public service; Sébastien D’Astous promises job cuts; uncertainty after the PEQ closes; Montreal: seven police officers fired and the anti-insult bylaw stays in force; end of the RPA wage premium; follow-ups: dates proposed for a Carney–St-Pierre Plamondon meeting, Therrien open to talks on telework, QS denounces the dismantling of the Ministry of Cybersecurity and Digital Affairs."),
 "2026-11-04": ("PSPP évoque un déficit « important » et nomme un conseiller chargé de traquer le gaspillage avec le Conseil du trésor; Investissement Québec poursuit Northex; La Caisse « très surprise » par Alstom; le SPVM acquiert des caméras de lecture de plaques; la consigne sur le verre pourrait être reportée.",
                "PSPP points to a “significant” deficit and names an adviser to hunt for waste with the Treasury Board; Investissement Québec sues Northex; La Caisse “very surprised” by Alstom; the SPVM buys licence-plate-reading cameras; the deposit on glass could be postponed."),
 "2026-11-05": ("Nemaska Lithium, projet à 1,2 milliard de fonds publics, risque de manquer de financement à Bécancour; Québec exige 690 M$ d’Ottawa pour les demandeurs d’asile; rentrée parlementaire reportée au 1er décembre; Hydro-Québec propose un partenariat avec Kahnawà:ke sur la ligne vers New York; faux CSQ : une ex-fonctionnaire accusée; l’opposition dit non à la loi 101 au cégep.",
                "Nemaska Lithium, a project with $1.2 billion in public funds, risks running short of financing in Bécancour; Quebec demands $690 million from Ottawa for asylum seekers; the Assembly’s return is postponed to Dec. 1; Hydro-Québec proposes a Kahnawà:ke partnership on the New York line; false CSQs: a former official charged; the opposition says no to Bill 101 at CEGEP."),
 "2026-11-06": ("Marceau juge que le budget fédéral « ne répond pas aux attentes »; Équiterre réclame un moratoire sur les centres de données; première rencontre Carney–PSPP au Cambodge; poursuite sur les fenêtres de l’observatoire du Stade olympique; la consigne s’étendra aux pintes de lait le 1er mars.",
                "Marceau says the federal budget “does not meet expectations”; Équiterre calls for a moratorium on data centres; first Carney–PSPP meeting in Cambodia; a lawsuit over the Olympic Stadium observatory windows; the deposit will cover milk cartons on March 1."),
 "2026-11-07": ("Hydro-Québec vise le terrain de Northvolt; Québec refuse de nouveaux fonds à Nemaska; la formation en éthique reste facultative.",
                "Hydro-Québec targets Northvolt’s land; Quebec refuses more Nemaska funding; ethics training remains optional."),
 "2026-11-08": ("Vaccins antigrippaux gratuits réservés aux groupes admissibles; le CUSM demande d’éviter deux urgences; la ministre Gentilcore réagit aux accusations visant une ex-employée de l’Immigration; plaintes visant Fady Dagher; une étude propose une « démonarchisation » graduelle; assurance des maisons patrimoniales.",
                "Free flu shots limited to eligible groups; the MUHC asks people to avoid two emergency departments; Minister Gentilcore reacts to charges against a former Immigration employee; complaints target Fady Dagher; a study proposes gradual ‘demonarchization’; heritage-home insurance."),
 "2026-11-09": ("Québec met fin aux prêts pardonnables; les libéraux contestent en cour le résultat dans Vachon; Consignaction compte sur les contenants non retournés; retrait préventif d’un traversier à L’Isle-aux-Coudres; tunnel La Fontaine; liberté académique; incendies criminels à Ormstown; manifestation devant le PDQ 39; transport médical par hélicoptère; recommandations d’une coroner à Verdun.",
                "Quebec ends forgivable loans; the Liberals contest the Vachon result in court; Consignaction relies on unreturned containers; a ferry withdrawn as a precaution at L’Isle-aux-Coudres; La Fontaine tunnel; academic freedom; arson fires in Ormstown; protest outside Station 39; medical helicopter transport; a coroner’s recommendations in Verdun."),
 "2026-11-10": ("Près d’une centaine de mises à pied chez Nemaska Lithium; Hydro-Québec remplacera des thermostats Hilo; soumissions trop élevées pour l’urgence de l’hôpital de Jonquière; François Legault défend les prêts pardonnables; appels à encadrer les centres de données; une conseillère spéciale pour la Capitale-Nationale; traversiers de L’Isle-aux-Coudres; grève étudiante; coûts en hausse à Lévis; rapport de coroner sur une gare du REM.",
                "Nearly a hundred layoffs at Nemaska Lithium; Hydro-Québec to replace Hilo thermostats; bids too high for the Jonquière hospital emergency department; François Legault defends forgivable loans; calls to regulate data centres; a special adviser for the Capitale-Nationale; L’Isle-aux-Coudres ferries; student strike; rising costs in Lévis; coroner’s report on a REM station."),
 "2026-11-11": ("Plus de 40 M$ en contrats publics à Amazon Web Services; des écoles recourent à des chasseurs de têtes et à des agences; l’électrification des autobus n’est plus une priorité; ralentissement confirmé chez Nemaska Lithium; audiences du BAPE sur TES Canada; Domtar et les centrales de la Shipshaw; le ministre Girard et les ratés de la STQ; CF Montréal; itinérance et conditions fédérales; un juge de la Cour supérieure demande sa réintégration.",
                "More than $40M in public contracts to Amazon Web Services; schools turn to headhunters and agencies; bus electrification no longer a priority; Nemaska Lithium slowdown confirmed; BAPE hearings on TES Canada; Domtar and the Shipshaw power plants; Minister Girard on STQ breakdowns; CF Montréal; homelessness and federal conditions; a Superior Court judge seeks reinstatement."),
 "2026-11-12": ("Accusations de vol de données à la SAAQ; quatre parcs éoliens en retard pour Hydro-Québec; confusion sur l’abolition de Santé Québec; fin d’un projet pilote de chirurgies au privé; un traversier à louer pour L’Isle-aux-Coudres?; vers un décret pour Horne 5; départ du fondateur de Flo; le coût du garage de la Canardière; contrats au cabinet du maire de Saguenay; projet de loi sur les cégeps anglophones.",
                "Charges over SAAQ data theft; four wind farms late for Hydro-Québec; confusion over abolishing Santé Québec; private-surgery pilot cancelled; a ferry to rent for L’Isle-aux-Coudres?; toward a decree for Horne 5; Flo’s founder leaves; the cost of the Canardière garage; contracts in the Saguenay mayor’s office; bill on English-language CEGEPs."),
 "2026-11-13": ("Hausse de salaire pour cinq hauts fonctionnaires; parcs éoliens freinés par les délais d’autorisation; Sainte-Flavie attend depuis 447 jours; logements abordables en attente d’Hydro-Québec à Amos; coupes en soins palliatifs à Lévis; la facture des usines d’eaux usées de Lévis; Saguenay acquiert une rue sans l’avis de ses ingénieurs; un autre immeuble pour le tramway; stages rémunérés; prison pour une fraude aux remboursements de taxes.",
                "Salary premium for five senior public servants; wind farms held back by approval delays; Sainte-Flavie has waited 447 days; affordable housing waiting on Hydro-Québec in Amos; palliative care cuts in Lévis; the bill for Lévis’s wastewater plants; Saguenay acquires a street without its engineers’ backing; another building for the tramway; paid internships; prison for tax-refund fraud."),
 "2026-11-14": ("Le tribunal approuve la vente de l’ancien terrain de Northvolt à Hydro-Québec; sécheresse record et achats d’électricité chez Hydro-Québec; Québec veut retravailler l’entente sur Churchill Falls; fraude alléguée chez un mandataire de la SAAQ; thermostat Hilo récent qui surchauffe; recul partiel aux soins palliatifs de Lévis; Milliard critique le début de mandat du PQ; la reconnaissance de Québec solidaire en négociation; taxes et aide au loyer à Montréal; la Constitution en français devant les tribunaux.",
                "Court approves the sale of Northvolt’s former land to Hydro-Québec; record drought and electricity purchases at Hydro-Québec; Quebec wants to rework the Churchill Falls agreement; alleged fraud at an SAAQ agent; a recent Hilo thermostat overheats; partial reversal on palliative care in Lévis; Milliard criticizes the PQ’s start; Québec solidaire’s recognition under negotiation; taxes and rent aid in Montreal; the French Constitution before the courts."),
}
# Section headings that are not in "FR / EN" form: explicit (FR, EN) pairs, trivial translations only.
HEADINGS = {
 "Fraud & investigations": ("Fraude & enquêtes", "Fraud & investigations"),
 "Government & institutions": ("Gouvernement & institutions", "Government & institutions"),
 "Energy & industry": ("Énergie & industrie", "Energy & industry"),
 "Lobbying & ethics": ("Lobbyisme & éthique", "Lobbying & ethics"),
 "Justice & investigations": ("Justice & enquêtes", "Justice & investigations"),
 "Contracting & labour": ("Contrats & travail", "Contracting & labour"),
 "Health & social services": ("Santé & services sociaux", "Health & social services"),
 "Public finances": ("Finances publiques", "Public finances"),
 "Mise à jour / Update (après-midi)": ("Mise à jour (après-midi)", "Update (afternoon)"),
 "Mise à jour / Update (fin de matinée / late morning)": ("Mise à jour (fin de matinée)", "Update (late morning)"),
 "Mise à jour / Update (fin d’après-midi / late afternoon)": ("Mise à jour (fin d’après-midi)", "Update (late afternoon)"),
}
# Section heading (EN part) -> homepage category id, used when a story has no category in _data/story_meta.json.
HEADING_CATEGORY = {
 "Government & institutions": "government", "Fraud & investigations": "justice", "Energy & industry": "energy",
 "Energy & digital": "energy", "Lobbying & ethics": "justice", "Crown corporations & IT": "crown-it",
 "Contracting & Crown corporations": "crown-it", "Health": "health",
}
# Domain -> outlet name shown next to each story on the homepage (fallback: the domain).
OUTLETS = {
 "ici.radio-canada.ca": "Radio-Canada", "www.lapresse.ca": "La Presse", "www.tvanouvelles.ca": "TVA Nouvelles",
 "www.journaldemontreal.com": "Le Journal de Montréal", "www.journaldequebec.com": "Le Journal de Québec",
 "www.cbc.ca": "CBC News", "montrealgazette.com": "Montreal Gazette", "www.newswire.ca": "Newswire (communiqué)",
 "www.noovo.info": "Noovo Info", "lautorite.qc.ca": "Autorité des marchés financiers", "www.latribune.ca": "La Tribune",
 "www.ledevoir.com": "Le Devoir", "www.vgq.qc.ca": "Vérificateur général du Québec", "www.quebec.ca": "Gouvernement du Québec",
 "www.assnat.qc.ca": "Assemblée nationale", "lobbyisme.quebec": "Commissaire au lobbyisme",
 "www.hydroquebec.com": "Hydro-Québec (document)",
 "montreal.citynews.ca": "CityNews Montréal", "www.cardus.ca": "Institut Cardus (communiqué)",
 "www150.statcan.gc.ca": "Statistique Canada",
}
def outlet(url):
    from urllib.parse import urlparse
    h = urlparse(url or "").netloc.lower()
    return OUTLETS.get(h) or h.removeprefix("www.")

STOP = set("""les des une est sont pour par dans avec sur que qui aux ses son leur leurs cette ces pas plus the and for are with that this from has have was were its their they will been into than about after also more who what
selon environ dont mais encore elle elles ils lui être fait avoir""".split())
def _words(t):
    import re
    return {w for w in re.findall(r"[\w’']+", (t or "").lower()) if len(w) > 3 and w not in STOP}
def _overlap(summary, why):
    w, s = {x[:5] for x in _words(why)}, {x[:5] for x in _words(summary)}
    return len(w & s) / len(w) if w else 1.0
def why_adds(st, wfr, wen):
    """Homepage only: show Why it matters when it adds to the summary (on average, under half of its words repeat it).
    The full digest post always shows it."""
    return (_overlap(st["fr"], wfr) + _overlap(st["en"], wen)) / 2 < 0.5

e = html.escape
def strip_star(s): return s.strip()[1:-1].strip()
def is_star(s): s = s.strip(); return len(s) > 2 and s.startswith("*") and s.endswith("*")
def bi(tag, fr, en, cls=""):
    c = f" {cls}" if cls else ""
    # Inline pairs get a hidden " / " separator so text-only readers (no CSS, reader views, crawlers) never see "FRen" run together.
    sep = '<span class="l-sep" aria-hidden="true"> / </span>' if tag == "span" else ""
    return (f'<{tag} class="l-fr{c}" lang="fr">{e(fr)}</{tag}>' + sep +
            f'<{tag} class="l-en{c}" lang="en">{e(en)}</{tag}>')

def story_id(url):
    """Stable anchor for a story (used to link straight to a story in its daily digest)."""
    import hashlib
    return "s-" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]

def money_box(it, pop):
    """'The money, in human terms' callout (same markup as _includes/money.html)."""
    src = f'<a href="{e(it["source_url"])}">{e(it["source_outlet"])}</a>'
    psrc = f'<a href="{e(pop["source_url"])}">ISQ</a>'
    return ('<div class="callout money"><p class="callout-label">' + bi("span", "L’argent, en termes concrets", "The money, in human terms") + '</p>'
            + bi("p", it["per_fr"], it["per_en"], "money-big")
            + bi("p", it["label_fr"], it["label_en"], "money-label")
            + bi("p", it["calc_fr"], it["calc_en"], "money-calc")
            + (bi("p", it["note_fr"], it["note_en"], "money-note") if it.get("note_en") else "")
            + f'<p class="l-fr money-src" lang="fr">Montant : {src}. Population : {psrc}, {e(pop["label_fr"])} (mise à jour {e(pop["source_updated"])}). Une façon de se représenter l’ordre de grandeur, pas une facture que chaque personne paie.</p>'
            + f'<p class="l-en money-src" lang="en">Amount: {src}. Population: {psrc}, {e(pop["label_en"])} (updated {e(pop["source_updated"])}). A way to picture the size, not a bill each person pays.</p>'
            + '</div>')

def split_heading(name, day, notes):
    if name in HEADINGS:
        if " / " not in name: notes.append(f"{day}: heading '{name}' was English-only; FR '{HEADINGS[name][0]}' added (trivial translation)")
        else: notes.append(f"{day}: heading '{name}' mapped to FR '{HEADINGS[name][0]}' / EN '{HEADINGS[name][1]}'")
        return HEADINGS[name]
    if name.count(" / ") == 1:
        fr, en = name.split(" / "); return fr.strip(), en.strip()
    notes.append(f"{day}: heading '{name}' exists in one language only; shown as-is in both modes")
    return name, name

def parse(day, issues):
    lines = [l.rstrip("\n") for l in open(f"{SRC}/{day}.txt", encoding="utf-8") if l.strip()]
    title_line = strip_star(lines[0]); i = 1; sections = []; cur = None
    while i < len(lines):
        l = lines[i].strip()
        if l.startswith("—"): i += 1; continue
        if is_star(l):
            nxt = lines[i+1].strip() if i+1 < len(lines) else ""
            if nxt.startswith(("🇫🇷", "🇬🇧", "http")):
                st = {"headline": strip_star(l), "fr": None, "en": None, "url": None}; i += 1
                while i < len(lines) and not is_star(lines[i]) and not lines[i].strip().startswith("—"):
                    t = lines[i].strip()
                    if t.startswith("💡🇫🇷"): st["why_fr"] = t.replace("💡🇫🇷", "", 1).strip()
                    elif t.startswith("💡🇬🇧"): st["why_en"] = t.replace("💡🇬🇧", "", 1).strip()
                    elif t.startswith("🇫🇷"): st["fr"] = t.replace("🇫🇷", "", 1).strip()
                    elif t.startswith("🇬🇧"): st["en"] = t.replace("🇬🇧", "", 1).strip()
                    elif t.startswith("http"): st["url"] = t
                    else: issues.append(f"{day}: unexpected line: {t}")
                    i += 1
                for k in ("fr", "en", "url"):
                    if not st[k]: issues.append(f"{day}: '{st['headline']}' missing {k}")
                if cur is None: cur = {"name": "", "stories": []}; sections.append(cur)
                cur["stories"].append(st); continue
            cur = {"name": strip_star(l), "stories": []}; sections.append(cur); i += 1; continue
        issues.append(f"{day}: stray line: {l}"); i += 1
    return title_line, sections

def build(day, issues, notes):
    if day not in TAGS or day not in SUMMARY:
        issues.append(f"{day}: add TAGS and SUMMARY entries first"); return None
    title_line, sections = parse(day, issues)
    y, m, d = map(int, day.split("-"))
    title_fr = f"Digest du {d}{'er' if d == 1 else ''} {FR_MONTHS[m-1]} {y}"
    title_en = f"Daily digest – {EN_MONTHS[m-1]} {d}, {y}"
    n = sum(len(s["stories"]) for s in sections)
    why = plain.load("why.json", {})
    money = plain.load("money.json", {"items": [], "population": {}})
    plain.compute(money) if money["items"] else None
    meta = plain.load("story_meta.json", {"stories": {}}).get("stories", {})
    cats = {c["id"] for c in plain.load("categories.json", {"items": []})["items"]}
    body, items = [], []
    for s in sections:
        if not s["stories"]: issues.append(f"{day}: empty section {s['name']}")
        fr, en = split_heading(s["name"], day, notes)
        body.append('<section class="digest-section">')
        body.append(f'<h2>{bi("span", fr, en)}</h2>' if fr != en else f'<h2>{e(fr)}</h2>')
        for st in s["stories"]:
            body.append(f'<article class="story" id="{story_id(st["url"] or st["headline"])}">')
            body.append(f'<h3><a href="{e(st["url"] or "")}">{e(st["headline"])}</a></h3>')
            body.append(bi("p", st["fr"] or "", st["en"] or "", "summary"))
            w = why.get(st["url"] or "", {})
            wfr, wen = st.get("why_fr") or w.get("fr"), st.get("why_en") or w.get("en")
            if wfr and wen:
                body.append('<div class="callout why"><p class="callout-label">' + bi("span", "Pourquoi c’est important", "Why it matters") + '</p>' + bi("p", wfr, wen) + '</div>')
            else: notes.append(f"{day}: no Why-it-matters line for {st['url']} (add it to _data/why.json)")
            m = meta.get(st["url"] or "", {})
            cat = m.get("category") or HEADING_CATEGORY.get(en.split(" (")[0]) or "other"
            if not m.get("category"): notes.append(f"{day}: no category in _data/story_meta.json for {st['url']} (using '{cat}')")
            if cat not in cats: issues.append(f"{day}: unknown category '{cat}' for {st['url']}"); cat = "other"
            it_ = {"id": story_id(st["url"] or st["headline"]), "url": st["url"] or "", "headline": st["headline"],
                   "title_en": m.get("title_en") or st["headline"], "title_fr": m.get("title_fr") or st["headline"],
                   "outlet": outlet(st["url"]), "category": cat, "importance": int(m.get("importance", 2)),
                   "summary_fr": st["fr"] or "", "summary_en": st["en"] or ""}
            if wfr and wen and why_adds(st, wfr, wen):
                it_["why_fr"], it_["why_en"] = wfr, wen
            items.append(it_)
            for it in [x for x in money["items"] if x.get("story_url") == st["url"]]:
                body.append(money_box(it, money["population"]))
            body.append('</article>')
        body.append('</section>')
    if any("{{" in t or "{%" in t for t in body): issues.append(f"{day}: Liquid-like text in content")
    for rank, it_ in enumerate(sorted(items, key=lambda x: -x["importance"])[:3], 1): it_["featured"] = rank
    for it_ in items: it_.setdefault("featured", 0)
    sfr, sen = SUMMARY[day]
    fm = ["---", "layout: post",
          f"title: {json.dumps(title_en, ensure_ascii=False)}",
          f"title_fr: {json.dumps(title_fr, ensure_ascii=False)}",
          f"date: {day}",
          f"summary: {json.dumps(sen, ensure_ascii=False)}",
          f"summary_fr: {json.dumps(sfr, ensure_ascii=False)}",
          f"story_count: {n}",
          "tags: [" + ", ".join(TAGS[day]) + "]",
          f"source_heading: {json.dumps(title_line, ensure_ascii=False)}",
          "stories:"] + [f"  - {json.dumps(it_, ensure_ascii=False)}" for it_ in items] + ["---", ""]
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/{day}-digest.md", "w", encoding="utf-8").write("\n".join(fm) + "\n".join(body) + "\n")
    return {s["name"]: len(s["stories"]) for s in sections} | {"_total": n}

if __name__ == "__main__":
    days = sys.argv[1:] or sorted(TAGS)
    issues, notes, counts = [], [], {}
    for day in days:
        r = build(day, issues, notes)
        if r: counts[day] = r
    print({d: c["_total"] for d, c in counts.items()})
    print("NOTES:"); [print("  " + x) for x in notes]
    print("ISSUES:", issues or "none")
