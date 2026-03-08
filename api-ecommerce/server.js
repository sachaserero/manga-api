const express = require("express");
const { MongoClient, ObjectId } = require("mongodb");
require("dotenv").config();

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3001;
const DB_NAME = process.env.DB_NAME || "ecommerce";
const COLLECTION = process.env.COLLECTION || "Product";

let col = null;

// Page de test
app.get("/", (req, res) => res.send("API e-commerce OK ✅ (essaie /items ou /search)"));

function requireDb(req, res, next) {
  if (!col) return res.status(503).json({ error: "MongoDB pas connecté (vérifie MONGO_URI dans .env)" });
  next();
}

// CREATE: POST /items
app.post("/items", requireDb, async (req, res) => {
  try {
    const { nom, prix, categorie, description } = req.body;
    if (!nom || prix === undefined) {
      return res.status(400).json({ error: "Champs requis: nom, prix" });
    }
    const doc = {
      nom,
      prix: Number(prix),
      categorie: categorie || null,
      description: description || "",
      createdAt: new Date()
    };
    const r = await col.insertOne(doc);
    res.status(201).json({ _id: r.insertedId, ...doc });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// READ: GET /items/:id
app.get("/items/:id", requireDb, async (req, res) => {
  try {
    const { id } = req.params;
    if (!ObjectId.isValid(id)) return res.status(400).json({ error: "ID invalide" });
    const item = await col.findOne({ _id: new ObjectId(id) });
    if (!item) return res.status(404).json({ error: "Introuvable" });
    res.json(item);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// LIST: GET /items?page=1&limit=10 (facultatif)
app.get("/items", requireDb, async (req, res) => {
  try {
    const page = Math.max(parseInt(req.query.page || "1", 10), 1);
    const limit = Math.min(Math.max(parseInt(req.query.limit || "10", 10), 1), 50);
    const skip = (page - 1) * limit;

    const items = await col.find({}).skip(skip).limit(limit).toArray();
    res.json({ page, limit, count: items.length, items });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// SEARCH: GET /search?keyword=... (regex sur 2 champs) + filtre categorie/prixMax
app.get("/search", requireDb, async (req, res) => {
  try {
    const keyword = (req.query.keyword || "").trim();
    const categorie = (req.query.categorie || "").trim();
    const prixMax = req.query.prixMax ? Number(req.query.prixMax) : null;

    if (!keyword) return res.status(400).json({ error: "keyword est obligatoire" });

    const regex = new RegExp(keyword, "i");

    const query = {
      $or: [
        { nom: { $regex: regex } },
        { description: { $regex: regex } }
      ]
    };

    // filtre additionnel (au moins 1 possible)
    if (categorie) {
      query.$and = query.$and || [];
      query.$and.push({ $or: [{ categorie }, { Categorie: categorie }] }); // compat si tu as "Categorie" majuscule
    }
    if (prixMax !== null && !Number.isNaN(prixMax)) query.prix = { $lte: prixMax };

    const results = await col.find(query).limit(20).toArray();
    res.json({ count: results.length, results });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Démarre l'API (localhost répond même si Mongo a un souci)
app.listen(PORT, "127.0.0.1", () => console.log(`🚀 API: http://localhost:${PORT}`));

// Connect Mongo
(async () => {
  try {
    if (!process.env.MONGO_URI) throw new Error("MONGO_URI manquant dans .env");
    const client = new MongoClient(process.env.MONGO_URI);
    await client.connect();
    col = client.db(DB_NAME).collection(COLLECTION);
    console.log(`✅ Mongo connecté : ${DB_NAME}.${COLLECTION}`);
  } catch (e) {
    console.log("❌ Mongo error:", e.message);
  }
})();
