from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
import math

app = Flask(__name__)

# ── CONNEXION MONGODB ATLAS ───────────────────────
client = MongoClient("mongodb+srv://sachasereropro_db_user:TON_MOT_DE_PASSE@cluster0.ksm29hm.mongodb.net/?appName=Cluster0")
db  = client["manga_db"]
col = db["mangas"]

# ── HELPER ────────────────────────────────────────
def fix_id(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

def err(msg, code=400):
    return jsonify({"error": msg}), code

# ══════════════════════════════════════════════════
#  PAGE D'ACCUEIL  (HTML)
# ══════════════════════════════════════════════════
@app.route("/", methods=["GET"])
def home():
    return """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Manga API</title>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Noto+Sans+JP:wght@400;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet"/>
  <style>
    :root{
      --ink:#0d0d0d; --paper:#f5f0e8; --red:#e8192c; --gold:#f5a623;
      --accent:#1a1aff; --muted:#8a8070; --card:#fff; --border:#d4cfc4;
    }
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    html{scroll-behavior:smooth}
    body{
      background:var(--paper);color:var(--ink);
      font-family:'Noto Sans JP',sans-serif;
      background-image:
        repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(0,0,0,0.04) 39px,rgba(0,0,0,0.04) 40px),
        repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(0,0,0,0.04) 39px,rgba(0,0,0,0.04) 40px);
      min-height:100vh;
    }

    /* ── HEADER ── */
    header{
      border-bottom:3px solid var(--ink);
      background:var(--ink);color:var(--paper);
      padding:0 40px;
      display:flex;align-items:stretch;justify-content:space-between;
      flex-wrap:wrap;gap:0;
      animation:slideDown .5s ease both;
    }
    .header-left{
      display:flex;align-items:center;gap:16px;
      padding:20px 0;
      border-right:1px solid rgba(255,255,255,0.1);
      padding-right:40px;
    }
    .manga-logo{
      font-family:'Bebas Neue',sans-serif;
      font-size:3rem;letter-spacing:2px;
      line-height:1;
      color:var(--red);
      text-shadow:3px 3px 0 var(--gold);
    }
    .manga-logo span{color:var(--paper)}
    .tagline{font-size:.75rem;color:rgba(255,255,255,0.5);font-family:'JetBrains Mono',monospace;margin-top:4px}
    .status-pill{
      margin:20px 0 20px 40px;
      display:flex;align-items:center;gap:8px;
      background:rgba(0,255,100,0.1);border:1px solid rgba(0,255,100,0.3);
      border-radius:999px;padding:6px 14px;
      font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#00ff64;
    }
    .blink{width:7px;height:7px;background:#00ff64;border-radius:50%;animation:blink 1.5s infinite}

    /* ── HERO BAND ── */
    .hero-band{
      background:var(--red);color:var(--paper);
      padding:12px 40px;
      display:flex;align-items:center;gap:20px;
      overflow:hidden;
      border-bottom:3px solid var(--ink);
    }
    .hero-band span{
      font-family:'Bebas Neue',sans-serif;font-size:1.1rem;letter-spacing:3px;
      white-space:nowrap;opacity:.5;
    }
    .hero-band span.hi{opacity:1}

    /* ── MAIN ── */
    main{max-width:1100px;margin:0 auto;padding:48px 24px}

    /* ── SECTION ── */
    .section{margin-bottom:56px;animation:fadeUp .5s ease both}
    .section:nth-child(2){animation-delay:.08s}
    .section:nth-child(3){animation-delay:.16s}
    .section:nth-child(4){animation-delay:.24s}

    .section-label{
      display:inline-flex;align-items:center;gap:10px;
      font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:2px;
      border-left:4px solid var(--red);padding-left:12px;
      margin-bottom:20px;
    }
    .section-label .num{
      font-family:'JetBrains Mono',monospace;font-size:.7rem;
      background:var(--ink);color:var(--paper);
      padding:2px 7px;border-radius:4px;letter-spacing:0;
    }

    /* ── CARDS GRID ── */
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}

    .card{
      background:var(--card);
      border:2px solid var(--ink);
      border-radius:0;
      box-shadow:4px 4px 0 var(--ink);
      padding:18px 20px;
      text-decoration:none;color:var(--ink);
      display:flex;flex-direction:column;gap:8px;
      transition:transform .15s,box-shadow .15s;
      position:relative;overflow:hidden;
    }
    .card::before{
      content:'';position:absolute;top:0;left:0;right:0;height:3px;
    }
    .card.c-red::before{background:var(--red)}
    .card.c-blue::before{background:var(--accent)}
    .card.c-gold::before{background:var(--gold)}
    .card:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 var(--ink)}

    .card-top{display:flex;align-items:center;gap:10px}
    .badge{
      font-family:'JetBrains Mono',monospace;font-size:.62rem;font-weight:600;
      padding:3px 8px;border:1.5px solid currentColor;border-radius:3px;
      flex-shrink:0;
    }
    .get {color:var(--accent);border-color:var(--accent);background:rgba(26,26,255,.06)}
    .post{color:var(--red);border-color:var(--red);background:rgba(232,25,44,.06)}

    .card-path{
      font-family:'JetBrains Mono',monospace;font-size:.82rem;font-weight:600;
      white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
    }
    .card-desc{font-size:.78rem;color:var(--muted);line-height:1.5}
    .card-params{
      margin-top:4px;
      font-family:'JetBrains Mono',monospace;font-size:.7rem;
      color:var(--ink);background:#f5f0e8;
      border:1px solid var(--border);border-radius:3px;
      padding:6px 10px;line-height:1.8;
    }
    .card-params b{color:var(--red)}
    .arrow-link{
      margin-top:auto;
      align-self:flex-end;
      font-family:'JetBrains Mono',monospace;font-size:.75rem;
      color:var(--accent);display:flex;align-items:center;gap:4px;
      transition:gap .15s;
    }
    .card:hover .arrow-link{gap:8px}

    /* ── SCHEMA BOX ── */
    .schema-box{
      background:var(--ink);color:#a8ff78;
      border:2px solid var(--ink);
      box-shadow:4px 4px 0 var(--muted);
      padding:24px 28px;
      font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:2;
    }
    .schema-box .key{color:#79c0ff}
    .schema-box .val{color:#ffa657}
    .schema-box .req{color:#ff7b72}
    .schema-box .opt{color:#8b949e}
    .schema-box .comment{color:#3d4450;font-style:italic}

    /* ── EXAMPLE BOX ── */
    .example-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
    @media(max-width:700px){.example-grid{grid-template-columns:1fr}}
    .ex-box{
      border:2px solid var(--border);padding:16px 18px;
      font-family:'JetBrains Mono',monospace;font-size:.75rem;
      line-height:1.8;background:var(--card);
      box-shadow:3px 3px 0 var(--border);
    }
    .ex-box .label{
      font-family:'Bebas Neue',sans-serif;font-size:1rem;letter-spacing:1px;
      margin-bottom:10px;display:flex;align-items:center;gap:8px;
    }
    .ex-box a{color:var(--accent);text-decoration:none}
    .ex-box a:hover{text-decoration:underline}

    /* ── FOOTER ── */
    footer{
      border-top:3px solid var(--ink);background:var(--ink);color:var(--paper);
      padding:20px 40px;
      display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;
    }
    footer span{font-family:'JetBrains Mono',monospace;font-size:.72rem;opacity:.5}
    footer b{color:var(--red);opacity:1}

    @keyframes slideDown{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:none}}
    @keyframes fadeUp   {from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:none}}
    @keyframes blink    {0%,100%{opacity:1}50%{opacity:.2}}
  </style>
</head>
<body>

<header>
  <div class="header-left">
    <div>
      <div class="manga-logo"><span>MANGA</span>API</div>
      <div class="tagline">// REST API · MongoDB Atlas · Flask</div>
    </div>
  </div>
  <div class="status-pill">
    <div class="blink"></div>
    ONLINE · port 5000
  </div>
</header>

<div class="hero-band">
  <span class="hi">&#x30DE;&#x30F3;&#x30AC; DATABASE</span>
  <span>&mdash;</span>
  <span class="hi">CREATE</span><span>&bull;</span>
  <span class="hi">READ</span><span>&bull;</span>
  <span class="hi">SEARCH</span>
  <span>&mdash;</span>
  <span>REST API</span><span>&bull;</span>
  <span>MongoDB</span><span>&bull;</span>
  <span>Python Flask</span>
</div>

<main>

  <!-- CRUD -->
  <div class="section">
    <div class="section-label"><span class="num">01</span> CRUD &mdash; Mangas</div>
    <div class="grid">

      <a href="/items" class="card c-blue">
        <div class="card-top">
          <span class="badge get">GET</span>
          <span class="card-path">/items</span>
        </div>
        <div class="card-desc">Liste paginée de tous les mangas.</div>
        <div class="card-params">
          <b>?page=</b>1 &nbsp;<b>?limit=</b>10
        </div>
        <span class="arrow-link">Tester &#8594;</span>
      </a>

      <div class="card c-blue">
        <div class="card-top">
          <span class="badge get">GET</span>
          <span class="card-path">/items/:id</span>
        </div>
        <div class="card-desc">Récupère un manga par son identifiant MongoDB.</div>
        <div class="card-params">
          <b>:id</b> &nbsp;ObjectId MongoDB
        </div>
      </div>

      <div class="card c-red">
        <div class="card-top">
          <span class="badge post">POST</span>
          <span class="card-path">/items</span>
        </div>
        <div class="card-desc">Crée un nouveau manga dans la base.</div>
        <div class="card-params">
          Body JSON &rarr; voir schéma ci-dessous
        </div>
      </div>

    </div>
  </div>

  <!-- SEARCH -->
  <div class="section">
    <div class="section-label"><span class="num">02</span> RECHERCHE</div>
    <div class="grid">

      <a href="/search?keyword=one" class="card c-gold">
        <div class="card-top">
          <span class="badge get">GET</span>
          <span class="card-path">/search</span>
        </div>
        <div class="card-desc">Recherche sur le titre ET la description via <code>$regex</code> insensible à la casse.</div>
        <div class="card-params">
          <b>?keyword=</b>naruto<br/>
          <b>?genre=</b>shonen &nbsp;<span style="color:#8b949e">(filtre)</span><br/>
          <b>?note_min=</b>8 &nbsp;<span style="color:#8b949e">(filtre note ≥ X)</span>
        </div>
        <span class="arrow-link">Tester &#8594;</span>
      </a>

      <div class="card c-gold">
        <div class="card-top">
          <span class="badge get">GET</span>
          <span class="card-path">/search?genre=shonen</span>
        </div>
        <div class="card-desc">Filtre par genre uniquement (sans keyword).</div>
        <div class="card-params">
          Genres : <b>shonen</b> · <b>shojo</b> · <b>seinen</b> · <b>isekai</b> · <b>mecha</b>
        </div>
      </div>

      <a href="/search?keyword=dragon&note_min=9" class="card c-gold">
        <div class="card-top">
          <span class="badge get">GET</span>
          <span class="card-path">/search?keyword=dragon&amp;note_min=9</span>
        </div>
        <div class="card-desc">Combinaison keyword + filtre note minimale.</div>
        <span class="arrow-link">Tester &#8594;</span>
      </a>

    </div>
  </div>

  <!-- SCHEMA -->
  <div class="section">
    <div class="section-label"><span class="num">03</span> SCHÉMA D'UN MANGA</div>
    <div class="schema-box">
{<br/>
&nbsp;&nbsp;<span class="key">"titre"</span>: <span class="val">"One Piece"</span>, &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="req">// requis</span><br/>
&nbsp;&nbsp;<span class="key">"description"</span>: <span class="val">"Un pirate en quête du trésor ultime..."</span>, <span class="req">// requis</span><br/>
&nbsp;&nbsp;<span class="key">"auteur"</span>: <span class="val">"Eiichiro Oda"</span>, &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="req">// requis</span><br/>
&nbsp;&nbsp;<span class="key">"genre"</span>: <span class="val">"shonen"</span>, &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="req">// requis &mdash; shonen | shojo | seinen | isekai | mecha</span><br/>
&nbsp;&nbsp;<span class="key">"note"</span>: <span class="val">9.5</span>, &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="opt">// optionnel &mdash; 0 à 10</span><br/>
&nbsp;&nbsp;<span class="key">"volumes"</span>: <span class="val">107</span>, &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="opt">// optionnel</span><br/>
&nbsp;&nbsp;<span class="key">"en_cours"</span>: <span class="val">true</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="opt">// optionnel</span><br/>
}
    </div>
  </div>

  <!-- EXEMPLES -->
  <div class="section">
    <div class="section-label"><span class="num">04</span> EXEMPLES DE REQUÊTES</div>
    <div class="example-grid">
      <div class="ex-box">
        <div class="label"><span class="badge get">GET</span> Liste paginée</div>
        <a href="/items?page=1&limit=5">/items?page=1&amp;limit=5</a>
      </div>
      <div class="ex-box">
        <div class="label"><span class="badge get">GET</span> Recherche libre</div>
        <a href="/search?keyword=dragon">/search?keyword=dragon</a>
      </div>
      <div class="ex-box">
        <div class="label"><span class="badge get">GET</span> Filtre genre</div>
        <a href="/search?genre=seinen">/search?genre=seinen</a>
      </div>
      <div class="ex-box">
        <div class="label"><span class="badge get">GET</span> Multi-filtres</div>
        <a href="/search?keyword=hero&genre=shonen&note_min=8">/search?keyword=hero&amp;genre=shonen&amp;note_min=8</a>
      </div>
    </div>
  </div>

</main>

<footer>
  <span>MANGA<b>API</b> &mdash; manga_db · collection mangas</span>
  <span>Flask &middot; PyMongo &middot; MongoDB Atlas</span>
</footer>

</body>
</html>"""


# ══════════════════════════════════════════════════
#  CREATE  —  POST /items
# ══════════════════════════════════════════════════
@app.route("/items", methods=["POST"])
def create_manga():
    data = request.get_json()
    if not data:
        return err("Body JSON requis")

    required = ["titre", "description", "auteur", "genre"]
    for field in required:
        if field not in data or not str(data[field]).strip():
            return err(f"Champ requis manquant : {field}")

    genres_valides = ["shonen", "shojo", "seinen", "isekai", "mecha"]
    if data["genre"].lower() not in genres_valides:
        return err(f"Genre invalide. Valeurs acceptées : {', '.join(genres_valides)}")

    doc = {
        "titre":       data["titre"].strip(),
        "description": data["description"].strip(),
        "auteur":      data["auteur"].strip(),
        "genre":       data["genre"].lower().strip(),
        "note":        float(data["note"])    if "note"     in data else None,
        "volumes":     int(data["volumes"])   if "volumes"  in data else None,
        "en_cours":    bool(data["en_cours"]) if "en_cours" in data else None,
    }
    result = col.insert_one(doc)
    return jsonify({"status": "created", "id": str(result.inserted_id)}), 201


# ══════════════════════════════════════════════════
#  READ  —  GET /items  (liste paginée)
# ══════════════════════════════════════════════════
@app.route("/items", methods=["GET"])
def list_mangas():
    try:
        page  = max(1, int(request.args.get("page",  1)))
        limit = max(1, min(50, int(request.args.get("limit", 10))))
    except ValueError:
        return err("page et limit doivent être des entiers")

    skip  = (page - 1) * limit
    total = col.count_documents({})
    docs  = list(col.find().skip(skip).limit(limit))

    return jsonify({
        "page":        page,
        "limit":       limit,
        "total":       total,
        "total_pages": math.ceil(total / limit),
        "results":     [fix_id(d) for d in docs]
    })


# ══════════════════════════════════════════════════
#  READ  —  GET /items/:id
# ══════════════════════════════════════════════════
@app.route("/items/<id>", methods=["GET"])
def get_manga(id):
    try:
        oid = ObjectId(id)
    except InvalidId:
        return err("ID invalide", 400)

    doc = col.find_one({"_id": oid})
    if not doc:
        return err("Manga introuvable", 404)
    return jsonify(fix_id(doc))


# ══════════════════════════════════════════════════
#  SEARCH  —  GET /search
#  Params : keyword, genre, note_min
# ══════════════════════════════════════════════════
@app.route("/search", methods=["GET"])
def search_mangas():
    keyword  = request.args.get("keyword",  "").strip()
    genre    = request.args.get("genre",    "").strip().lower()
    note_min = request.args.get("note_min", "").strip()

    query = {}

    # Recherche $regex sur titre ET description
    if keyword:
        query["$or"] = [
            {"titre":       {"$regex": keyword, "$options": "i"}},
            {"description": {"$regex": keyword, "$options": "i"}},
        ]

    # Filtre genre
    if genre:
        query["genre"] = {"$regex": f"^{genre}$", "$options": "i"}

    # Filtre note minimale
    if note_min:
        try:
            query["note"] = {"$gte": float(note_min)}
        except ValueError:
            return err("note_min doit être un nombre")

    if not query:
        return err("Au moins un paramètre requis : keyword, genre ou note_min")

    docs = list(col.find(query))
    return jsonify({
        "query":   {"keyword": keyword, "genre": genre, "note_min": note_min},
        "count":   len(docs),
        "results": [fix_id(d) for d in docs]
    })


# ══════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(port=5000, debug=True)