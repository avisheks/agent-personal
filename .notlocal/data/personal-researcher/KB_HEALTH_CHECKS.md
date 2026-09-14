# Knowledge Base Health Checks

Periodic checks to catch inconsistencies, staleness, and structural decay as the KB grows.

## Quick Commands (run from project root)

```bash
# Orphan pages (no incoming wiki-links)
grep -roh '\[\[[^]]*\]\]' data/researcher/knowledge/ | sort -u | \
  sed 's/\[\[//;s/\]\]//' > /tmp/linked.txt
find data/researcher/knowledge -name "*.md" -not -path "*/index.md" -not -path "*/queries/*" | \
  xargs -I{} basename {} .md | sort -u > /tmp/all.txt
comm -23 /tmp/all.txt /tmp/linked.txt  # orphans

# Broken wiki-links (link targets that don't exist as files)
grep -roh '\[\[[^]]*\]\]' data/researcher/knowledge/ | sort -u | \
  sed 's/\[\[//;s/\]\]//' | while read name; do
    find data/researcher/knowledge -iname "*$(echo $name | tr ' ' '*')*" -print -quit | \
      grep -q . || echo "BROKEN: [[$name]]"
  done

# Stale pages (not modified in 90+ days)
find data/researcher/knowledge -name "*.md" -mtime +90

# Missing frontmatter fields
for f in $(find data/researcher/knowledge -name "*.md" -not -name "index.md"); do
  grep -L "^title:" "$f" && echo "  ^ missing title"
done

# Duplicate titles
grep -rh "^title:" data/researcher/knowledge/ | sort | uniq -d

# Index vs actual files mismatch
find data/researcher/knowledge -name "*.md" -not -name "index.md" -not -path "*/queries/*" | wc -l
grep -c "^\- \[" data/researcher/knowledge/index.md
# These numbers should roughly match
```

## Layered Health Check Strategy

### Layer 1: On Every Commit (CI / Pre-commit Hook)

| Check | What It Catches | Tool |
|-------|----------------|------|
| Frontmatter schema validation | Missing required fields (title, summary, sources, dates) | Custom script or `obsidian-linter` rules |
| Broken wiki-links | `[[Page Name]]` that doesn't resolve to a file | `marksman` LSP or grep script above |
| Markdown lint | Inconsistent heading levels, trailing whitespace, list formatting | `markdownlint` |
| Spelling | Typos in page titles and summaries | `cspell` |

### Layer 2: Weekly (Scheduled)

| Check | What It Catches | How |
|-------|----------------|-----|
| Orphan pages | Knowledge pages with zero incoming links | Script: cross-reference all `[[links]]` vs all files |
| Index sync | Pages that exist but aren't listed in `knowledge/index.md` | Diff file list vs index entries |
| Topic consistency | Sources in `sources/{topic}/` without corresponding knowledge pages | Compare source dirs vs knowledge dirs |
| Report staleness | Reports whose changelog is >30 days old while topic has new sources | Check latest changelog date vs latest source `ingestedAt` |
| Near-duplicate detection | Pages with >80% title or content similarity | Embedding similarity or TF-IDF cosine |

### Layer 3: Monthly (LLM-Assisted)

| Check | What It Catches | How |
|-------|----------------|-----|
| Contradiction detection | Page A says "X outperforms Y", Page B says opposite | LLM reads pairs of related pages, flags inconsistencies |
| Claim staleness | Facts that may have changed (benchmark scores, model releases, pricing) | LLM identifies time-sensitive claims, flags for re-verification |
| Topic fragmentation | Topics that have grown too broad or overlap significantly | Review `topics.md` against actual knowledge page count per topic |
| Merge candidates | Pages that cover nearly the same concept from different angles | Embedding similarity >0.85 + manual review |
| Source provenance check | Knowledge pages whose cited sources no longer exist or have changed | Validate URLs in source frontmatter (link checker) |

## What Karpathy's Approach Teaches Us

Karpathy's `autoresearch` uses three principles directly applicable to KB maintenance:

1. **Single immutable evaluation metric** — Define a "KB health score" (e.g., % of pages with complete frontmatter + zero broken links + recent update). Track it over time.

2. **Constrained mutation surface** — Don't let maintenance touch everything at once. Run focused fixes: "this week, fix all broken links" or "this week, update all pages missing `updatedAt`."

3. **Keep/discard logic** — For proposed merges or deletions, require a clear signal (e.g., zero references + >90 days stale + not linked from any report). Don't delete on gut feeling.

## Suggested Automation Stack

### Minimal (what you can do today)

```bash
# Add to a weekly cron or run manually
#!/bin/bash
echo "=== KB Health Check $(date) ==="

echo -e "\n--- Orphan Pages (no incoming links) ---"
# [orphan detection script above]

echo -e "\n--- Stale Pages (90+ days) ---"
find data/researcher/knowledge -name "*.md" -mtime +90 | wc -l

echo -e "\n--- Missing Frontmatter ---"
find data/researcher/knowledge -name "*.md" -not -name "index.md" \
  -exec grep -L "^title:" {} \; | wc -l

echo -e "\n--- Index Entries vs Actual Pages ---"
echo "Pages: $(find data/researcher/knowledge -name "*.md" -not -name "index.md" -not -path "*/queries/*" | wc -l)"
echo "Index entries: $(grep -c '^\- \[' data/researcher/knowledge/index.md)"

echo -e "\n--- Topics with Sources but No Knowledge Pages ---"
for d in data/researcher/sources/*/; do
  topic=$(basename "$d")
  [ ! -d "data/researcher/knowledge/$topic" ] && echo "  $topic"
done
```

### Intermediate (Obsidian plugins)

If viewing in Obsidian, enable:
- **Obsidian Linter** — frontmatter formatting, YAML dedup, timestamp management
- **Find Unlinked Files** — orphan detection + cleanup
- **Smart Connections** — AI-powered duplicate/similarity detection
- **Graph Analysis** — structural health metrics (clustering coefficient, isolated nodes)
- **Dataview** — custom queries for staleness, missing fields, etc.

### Advanced (LLM-powered, future)

- **Contradiction scanner**: For each topic, have an LLM read all pages and flag claims that conflict
- **Freshness scorer**: LLM identifies time-sensitive claims ("as of 2024", benchmark numbers, pricing) and flags for re-verification
- **Auto-linker**: LLM reads a page and suggests missing `[[wiki-links]]` to existing pages it should reference
- **Coverage critic**: LLM reads topic index + reports and identifies gaps ("topic X has no knowledge page covering Y")

## Health Metrics to Track

| Metric | Target | Red Flag |
|--------|--------|----------|
| % pages with complete frontmatter | >95% | <80% |
| Broken wiki-links | 0 | >10 |
| Orphan pages (zero inlinks) | <5% of total | >15% |
| Index entries vs actual pages | Within 5% | >20% mismatch |
| Average page staleness | <60 days | >120 days |
| Reports with outdated changelog | 0 | >3 |
| Near-duplicate pairs (>0.85 similarity) | 0 | >5 pairs |
| Topics in `topics.md` vs actual dirs | Match | Mismatch |

## Anti-Patterns to Avoid

- **Don't over-tag** — Tags rot faster than content. Use wiki-links for cross-references.
- **Don't version knowledge pages** — Only reports get versioned. Knowledge pages are living documents (update in place).
- **Don't delete aggressively** — Archive with a `deprecated: true` frontmatter flag before removing.
- **Don't batch-fix everything** — One category of fix per session. Breadth causes new inconsistencies.
- **Don't trust LLM fixes blindly** — LLM-suggested merges/corrections need human confirmation before applying.
