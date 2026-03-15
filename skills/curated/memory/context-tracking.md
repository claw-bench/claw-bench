# Context Tracking Skill

## Overview
This skill covers techniques for maintaining, updating, and querying context
and state across multiple interactions or processing steps.

## Entity Registry

### Tracking Named Entities
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Entity:
    id: str
    attributes: dict = field(default_factory=dict)
    relationships: list = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

registry: dict[str, Entity] = {}
```

## Fact Management

### Triple Store Pattern
Store facts as (subject, predicate, object) for flexible querying:
```python
facts = []  # list of (subject, predicate, object, timestamp)

def add_fact(subj, pred, obj):
    facts.append((subj, pred, obj, datetime.now()))

def query_facts(subj=None, pred=None):
    return [(s, p, o) for s, p, o, _ in facts
            if (subj is None or s == subj) and (pred is None or p == pred)]
```
When contradictions arise, later facts take precedence over earlier ones.

## Conversation State Tracking

- Keep the last N interactions in full detail; summarize older ones.
- Use a key-value store for quick state lookups with provenance tracking.
- Merge snapshots periodically to prevent unbounded growth.

## Relationship Graphs
- Model as adjacency lists: `{entity: [(related_entity, relation_type)]}`.
- Support bidirectional lookups by maintaining reverse edges.
- Add temporal validity (`valid_from`, `valid_to`) for time-sensitive relationships.

## Tips
- Always record provenance (source and timestamp) alongside each fact or state update.
- Resolve ambiguous entity references by fuzzy-matching against the registry.
- Use event sourcing to reconstruct any historical state from the log of changes.
- Periodically prune stale entries to keep the context store manageable.
- Test context tracking logic with multi-step scenarios that include updates and contradictions.
