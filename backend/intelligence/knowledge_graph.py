"""
Marketing Knowledge Graph — temporal episodes with entity resolution.
Patterns stolen from Graphiti (episodes, edge invalidation) and LightRAG (dual-keyword search).
"""

import json
import time
import hashlib
import sqlite3
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from config import settings

logger = logging.getLogger(__name__)

KG_DB_PATH = settings.db_path.parent / "knowledge_graph.db"


@dataclass
class Episode:
    """A timestamped marketing event — the atomic unit of knowledge.
    Pattern from Graphiti: events enter as episodes with valid_at (when it happened)
    and created_at (when we learned about it).
    """
    id: str
    content: str
    source: str            # "scout", "scorer", "learner", "manual", "competitor"
    source_detail: str     # specific agent or file
    valid_at: float        # when the event actually happened
    created_at: float      # when we ingested it
    entities: List[str] = field(default_factory=list)     # extracted entity names
    relations: List[dict] = field(default_factory=list)   # [{source, target, relation, fact}]


@dataclass
class Entity:
    """A marketing entity — competitor, campaign, segment, channel, product."""
    name: str
    entity_type: str       # "competitor", "campaign", "segment", "channel", "product", "pattern"
    summary: str = ""
    first_seen: float = 0
    last_seen: float = 0
    episode_count: int = 0

    @property
    def id(self) -> str:
        return hashlib.md5(f"{self.entity_type}:{self.name.lower()}".encode()).hexdigest()


@dataclass
class Edge:
    """A relationship between entities, with temporal validity.
    Pattern from Graphiti: edges can be invalidated when facts change.
    """
    source_entity: str     # entity name
    target_entity: str     # entity name
    relation: str          # "competes_with", "targets", "uses", "outperforms", etc.
    fact: str              # natural language description
    valid_at: float        # when this became true
    invalid_at: Optional[float] = None  # when this stopped being true (None = still valid)
    created_at: float = 0

    @property
    def id(self) -> str:
        return hashlib.md5(
            f"{self.source_entity}:{self.relation}:{self.target_entity}".encode()
        ).hexdigest()

    @property
    def is_valid(self) -> bool:
        return self.invalid_at is None


def _get_kg_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(KG_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS episodes (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            source TEXT NOT NULL,
            source_detail TEXT,
            valid_at REAL NOT NULL,
            created_at REAL NOT NULL,
            entities_json TEXT,
            relations_json TEXT
        );
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            summary TEXT,
            first_seen REAL,
            last_seen REAL,
            episode_count INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS edges (
            id TEXT PRIMARY KEY,
            source_entity TEXT NOT NULL,
            target_entity TEXT NOT NULL,
            relation TEXT NOT NULL,
            fact TEXT,
            valid_at REAL NOT NULL,
            invalid_at REAL,
            created_at REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
        CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
        CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_entity);
        CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_entity);
        CREATE INDEX IF NOT EXISTS idx_edges_valid ON edges(invalid_at);
        CREATE INDEX IF NOT EXISTS idx_episodes_source ON episodes(source);
        CREATE INDEX IF NOT EXISTS idx_episodes_valid ON episodes(valid_at);
    """)
    conn.commit()
    return conn


class KnowledgeGraph:
    """Marketing knowledge graph with temporal episodes and entity resolution."""

    def __init__(self):
        self._db = _get_kg_db()

    def add_episode(
        self,
        content: str,
        source: str,
        source_detail: str = "",
        valid_at: float = None,
        entities: List[dict] = None,
        relations: List[dict] = None,
    ) -> Episode:
        """Add a marketing event to the knowledge graph.

        entities: [{"name": "Competitor X", "type": "competitor"}, ...]
        relations: [{"source": "Competitor X", "target": "Product Y", "relation": "launched", "fact": "..."}, ...]
        """
        now = time.time()
        episode_id = hashlib.md5(f"{content}:{now}".encode()).hexdigest()

        ep = Episode(
            id=episode_id,
            content=content,
            source=source,
            source_detail=source_detail,
            valid_at=valid_at or now,
            created_at=now,
            entities=[e["name"] for e in (entities or [])],
            relations=relations or [],
        )

        # Store episode
        self._db.execute(
            "INSERT OR REPLACE INTO episodes "
            "(id, content, source, source_detail, valid_at, created_at, entities_json, relations_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                ep.id, ep.content, ep.source, ep.source_detail,
                ep.valid_at, ep.created_at,
                json.dumps(ep.entities), json.dumps(ep.relations),
            ),
        )

        # Upsert entities with deduplication
        for e in (entities or []):
            entity = Entity(name=e["name"], entity_type=e.get("type", "unknown"))
            existing = self._db.execute(
                "SELECT * FROM entities WHERE name = ? COLLATE NOCASE", (entity.name,)
            ).fetchone()

            if existing:
                # Update existing — Graphiti pattern: merge, don't duplicate
                self._db.execute(
                    "UPDATE entities SET last_seen = ?, episode_count = episode_count + 1 "
                    "WHERE name = ? COLLATE NOCASE",
                    (now, entity.name),
                )
            else:
                self._db.execute(
                    "INSERT INTO entities "
                    "(id, name, entity_type, summary, first_seen, last_seen, episode_count) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (entity.id, entity.name, entity.entity_type, "", now, now, 1),
                )

        # Add edges with invalidation check
        for rel in (relations or []):
            edge = Edge(
                source_entity=rel["source"],
                target_entity=rel["target"],
                relation=rel["relation"],
                fact=rel.get("fact", ""),
                valid_at=ep.valid_at,
                created_at=now,
            )

            # Graphiti pattern: check for contradicting edges and invalidate them
            existing_edges = self._db.execute(
                "SELECT id, fact FROM edges "
                "WHERE source_entity = ? AND target_entity = ? AND relation = ? AND invalid_at IS NULL",
                (edge.source_entity, edge.target_entity, edge.relation),
            ).fetchall()

            for old_edge in existing_edges:
                if old_edge["fact"] != edge.fact:
                    # Invalidate old edge — fact changed
                    self._db.execute(
                        "UPDATE edges SET invalid_at = ? WHERE id = ?",
                        (now, old_edge["id"]),
                    )
                    logger.info(f"Invalidated edge: {old_edge['fact']} -> {edge.fact}")

            self._db.execute(
                "INSERT OR REPLACE INTO edges "
                "(id, source_entity, target_entity, relation, fact, valid_at, invalid_at, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    edge.id, edge.source_entity, edge.target_entity, edge.relation,
                    edge.fact, edge.valid_at, edge.invalid_at, edge.created_at,
                ),
            )

        self._db.commit()
        logger.info(f"Episode added: {len(ep.entities)} entities, {len(ep.relations)} relations")
        return ep

    def search(self, query: str, entity_type: str = None, limit: int = 20) -> dict:
        """Search the knowledge graph.

        LightRAG pattern: dual-level search — entities (local) + episodes (global).
        """
        results: dict = {"entities": [], "edges": [], "episodes": []}

        # Local search: find matching entities
        if entity_type:
            entities = self._db.execute(
                "SELECT * FROM entities WHERE entity_type = ? AND name LIKE ? "
                "ORDER BY episode_count DESC LIMIT ?",
                (entity_type, f"%{query}%", limit),
            ).fetchall()
        else:
            entities = self._db.execute(
                "SELECT * FROM entities WHERE name LIKE ? OR summary LIKE ? "
                "ORDER BY episode_count DESC LIMIT ?",
                (f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        results["entities"] = [dict(e) for e in entities]

        # Get edges for found entities (only valid ones)
        entity_names = [e["name"] for e in entities]
        if entity_names:
            placeholders = ",".join("?" * len(entity_names))
            edges = self._db.execute(
                f"SELECT * FROM edges "
                f"WHERE (source_entity IN ({placeholders}) OR target_entity IN ({placeholders})) "
                f"AND invalid_at IS NULL ORDER BY valid_at DESC LIMIT ?",
                entity_names + entity_names + [limit],
            ).fetchall()
            results["edges"] = [dict(e) for e in edges]

        # Global search: find matching episodes
        episodes = self._db.execute(
            "SELECT * FROM episodes WHERE content LIKE ? ORDER BY valid_at DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
        results["episodes"] = [dict(e) for e in episodes]

        return results

    def get_entity_timeline(self, entity_name: str) -> List[dict]:
        """Get all episodes mentioning an entity, ordered by time."""
        episodes = self._db.execute(
            "SELECT * FROM episodes WHERE entities_json LIKE ? ORDER BY valid_at DESC",
            (f'%"{entity_name}"%',),
        ).fetchall()
        return [dict(e) for e in episodes]

    def get_competitor_graph(self, competitor_name: str) -> dict:
        """Get full graph around a competitor — all entities and edges connected to them."""
        edges = self._db.execute(
            "SELECT * FROM edges "
            "WHERE (source_entity = ? OR target_entity = ?) AND invalid_at IS NULL",
            (competitor_name, competitor_name),
        ).fetchall()

        connected_names = set()
        for e in edges:
            connected_names.add(e["source_entity"])
            connected_names.add(e["target_entity"])

        entities = []
        if connected_names:
            placeholders = ",".join("?" * len(connected_names))
            entities = self._db.execute(
                f"SELECT * FROM entities WHERE name IN ({placeholders})",
                list(connected_names),
            ).fetchall()

        return {
            "entities": [dict(e) for e in entities],
            "edges": [dict(e) for e in edges],
        }

    def get_stats(self) -> dict:
        """Return knowledge graph statistics."""
        return {
            "total_episodes": self._db.execute("SELECT COUNT(*) FROM episodes").fetchone()[0],
            "total_entities": self._db.execute("SELECT COUNT(*) FROM entities").fetchone()[0],
            "total_edges": self._db.execute(
                "SELECT COUNT(*) FROM edges WHERE invalid_at IS NULL"
            ).fetchone()[0],
            "invalidated_edges": self._db.execute(
                "SELECT COUNT(*) FROM edges WHERE invalid_at IS NOT NULL"
            ).fetchone()[0],
            "entity_types": [
                dict(r) for r in self._db.execute(
                    "SELECT entity_type, COUNT(*) as count FROM entities GROUP BY entity_type"
                ).fetchall()
            ],
        }
