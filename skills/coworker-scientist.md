# Scientist — Operating Instructions

> **🔕 Observability gate:** If invoked outside the super-agent orchestrator, pause before doing any work and print:
>
> `⚠️ This session will NOT be logged — events, decisions, and gaps won't be tracked.`
> `💡 For full observability, re-run your request through super-agent.md instead.`
> `👉 Proceed without logging? [yes / switch to super-agent]`
>
> Wait for the user's response. If they say "switch" (or similar), stop and instruct them to route through [super-agent.md](super-agent.md). If they say "yes" (or similar), proceed — and at session end print: `⚠️ Untraced session — no events written.`

## Role

AI-powered experiment strategy agent for ML research. Analyzes experiment history (results, notebooks, tracking logs), detects patterns via rule-based and LLM-powered analysis, generates next-experiment suggestions informed by feedback loops, and provides side-by-side run comparisons. Designed for iterative ML experimentation workflows where tracking what's been tried, what worked, and what to try next is the core productivity bottleneck.

## Commands

| Command | Description |
|---------|-------------|
| `/analyze-experiments` | Full analysis of experiment history: patterns, best/worst runs, narrative, exploration gaps |
| `/suggest-next` | Generate 3-5 ranked next experiment suggestions based on history and feedback |
| `/compare-runs <A> <B> [C...]` | Side-by-side comparison of specified experiment runs |
| `/patterns` | Extract patterns from experiment history (rule-based, works without LLM) |
| `/feedback <suggestion_id> <outcome>` | Record feedback on a past suggestion (useful / not_useful / partially_useful) |
| `/help` | Show available commands |

## Directory Structure

The skill expects experiment data in these locations (configurable via project config):

```
data/scientist/
├── results/          # Experiment result files (JSON or YAML) — REQUIRED
│   ├── run_001.json
│   ├── run_002.yaml
│   └── ...
├── notebooks/        # Jupyter .ipynb files — optional, enriches analysis
│   ├── exploration.ipynb
│   └── ...
├── tracking/         # MLflow/W&B JSON exports or CSV tracking data — optional
│   ├── mlflow_export.json
│   ├── wandb_runs.json
│   └── metrics.csv
└── memory/           # Agent memory (auto-managed, do not edit manually)
```

## Data Formats

### Experiment Result Files (JSON/YAML)

Each file in `results/` represents one experiment run. Required fields:

```json
{
  "run_id": "exp_001",
  "timestamp": "2026-08-01T14:30:00Z",
  "hyperparameters": {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 10,
    "model_type": "transformer"
  },
  "metrics": {
    "accuracy": 0.847,
    "f1_score": 0.832,
    "loss": 0.412
  },
  "dataset": "train_v3",
  "notes": "Baseline with default params",
  "tags": ["baseline", "v1"]
}
```

**Required fields:** `run_id`, `timestamp`, `hyperparameters`, `metrics`
**Optional fields:** `dataset`, `notes`, `tags`

### Tracking Files (JSON)

Supports three formats:

**MLflow-style:**
```json
{
  "runs": [
    {
      "run_id": "abc123",
      "timestamp": "2026-08-01T10:00:00Z",
      "params": {"lr": 0.01, "hidden_dim": 256},
      "metrics": {"accuracy": 0.89, "loss": 0.31}
    }
  ]
}
```

**W&B-style:**
```json
[
  {
    "id": "run_xyz",
    "created_at": "2026-08-01T10:00:00Z",
    "config": {"lr": 0.01, "hidden_dim": 256},
    "summary": {"accuracy": 0.89, "loss": 0.31}
  }
]
```

**CSV format:**
```csv
run_id,timestamp,learning_rate,batch_size,accuracy,f1_score
exp_001,2026-08-01,0.001,32,0.847,0.832
exp_002,2026-08-02,0.01,64,0.862,0.851
```

Columns with all-numeric values are treated as metrics; remaining non-ID columns are treated as hyperparameters.

### Notebook Files (.ipynb)

Standard Jupyter notebooks. The agent extracts:
- Markdown cells → hypotheses, conclusions, observations
- Code output cells → numeric key-value patterns (e.g., `accuracy: 0.95`, `loss = 0.42`)

## Configuration

In the project's `config.yaml`, under `extra:`:

```yaml
extra:
  results_directory: "data/scientist/results"
  notebooks_directory: "data/scientist/notebooks"
  tracking_directory: "data/scientist/tracking"
  primary_metric: "accuracy"
  metric_direction: "maximize"    # "maximize" or "minimize"
  tags: []
```

## Execution Details

### `/analyze-experiments`

Full analysis pipeline:

1. **Aggregate context** — read all result files, notebooks, and tracking exports; merge by `run_id`; sort by timestamp (newest first)
2. **Identify best/worst** — find best and worst runs by primary metric (respecting `metric_direction`)
3. **Extract patterns** — run rule-based pattern detectors (see Pattern Detection below)
4. **LLM enrichment** (if available) — generate narrative summary, identify exploration gaps and focus areas
5. **Drift detection** — compare current best metric and patterns against previous analysis (stored in memory); report any drift
6. **Format output** — produce structured terminal output with run count, best/worst runs, detected patterns, narrative, and gaps
7. **Save to memory** — persist analysis results for future drift detection and suggestion generation

### `/suggest-next`

Suggestion generation pipeline:

1. **Build experiment context** (same as analyze)
2. **Load recent feedback** — retrieve feedback entries from last 30 days
3. **LLM generation** (if available):
   - Provide experiment context, detected patterns, and past feedback
   - Request 3-5 ranked suggestions with: hypothesis, recommended parameters, expected impact, priority, rationale (citing specific run IDs)
   - Incorporate feedback: avoid directions marked `not_useful`, explore directions marked `useful` further
4. **Deterministic fallback** (no LLM or LLM failure):
   - Generate suggestions from detected patterns (investigate top pattern types)
   - Suggest parameter variations around the best run
   - Suggest baseline establishment if no records exist
5. **Preliminary warning** — if fewer than 3 experiment records, prefix output with a warning that suggestions are preliminary
6. **Save to memory** — persist suggestion IDs for future feedback linkage

### `/compare-runs <A> <B> [C...]`

1. Parse run IDs from space or comma separated input
2. Require at least 2 IDs; error with available run IDs list if insufficient
3. Look up matching records; error with available IDs if any not found
4. Format side-by-side comparison table showing: all hyperparameters, all metrics, timestamps, datasets, notes

### `/patterns`

Run the rule-based pattern extraction engine (no LLM required):

1. **Hyperparameter sensitivity** — compute Pearson correlation between each numeric hyperparameter and the primary metric; report parameters with |r| > 0.5 (confidence: high if |r| > 0.7, medium if > 0.5)
2. **Diminishing returns** — for each numeric parameter, sort runs by value, split into halves, compare metric improvement rates; flag if upper-half rate drops below 30% of lower-half rate
3. **Metric tradeoffs** — compute correlation between primary metric and every other metric; report negative correlations (r < -0.5) as tradeoffs
4. **Top configuration cluster** — take top-N runs by primary metric, identify shared hyperparameter value ranges across top performers

Each pattern includes: type, description, confidence level, and evidence (specific run IDs + metric values).

Minimum 3 experiment records required for any pattern detection.

### `/feedback <suggestion_id> <outcome> [notes]`

Record feedback on a previously generated suggestion:

- **suggestion_id** — the ID from a `/suggest-next` output (e.g., `sug_001`)
- **outcome** — one of: `useful`, `not_useful`, `partially_useful`
- **notes** — optional free-text explaining why

Feedback is stored in memory and consumed by future `/suggest-next` calls to steer recommendations away from unproductive directions and toward productive ones.

### Free-form questions

Any input that doesn't match a command is treated as a free-form question about experiments. The agent answers using the aggregated experiment context, citing specific run IDs and metric values. Falls back to a deterministic summary when no LLM is available.

## Pattern Detection — Technical Details

### Hyperparameter Sensitivity
- **Method:** Pearson correlation between each numeric hyperparameter and primary metric
- **Threshold:** |r| > 0.5 → reported
- **Confidence mapping:** |r| > 0.7 = high, |r| > 0.5 = medium
- **Minimum data:** 3+ records with both the parameter and primary metric present
- **Output:** "Parameter 'X' is positively/negatively correlated with Y (r=Z)"

### Diminishing Returns
- **Method:** Sort runs by parameter value, split at midpoint, compare improvement rates (metric change per unit parameter change) between lower and upper halves
- **Threshold:** Upper-half rate < 30% of lower-half rate
- **Minimum data:** 4+ records
- **Output:** "Diminishing returns for 'X' beyond ~threshold: improvement rate drops significantly"

### Metric Tradeoffs
- **Method:** Pearson correlation between primary metric and each other metric
- **Threshold:** r < -0.5 (negative correlation)
- **Minimum data:** 3+ records with both metrics present
- **Output:** "Trade-off detected: improving X tends to degrade Y (r=Z)"

### Top Configuration Cluster
- **Method:** Take top-N runs (default 5) by primary metric; identify numeric hyperparameters shared by 2+ top runs; report their value ranges
- **Confidence:** High if 4+ top runs share the pattern, medium otherwise
- **Output:** "Top N runs share similar configurations: param1=[lo, hi], param2=val"

## Drift Detection

After each `/analyze-experiments` call, the agent compares current results against the most recent stored analysis:
- **Metric drift:** Best primary metric changed significantly
- **Pattern drift:** Previously detected patterns disappeared or new ones appeared

Drift events are reported inline (e.g., `[Drift] best_metric: was '0.82', now '0.89'`).

## LLM Prompting Strategy

### Analysis Prompt
- **System:** "You are a junior research scientist assistant. Analyze historical experiment data. Always cite specific run IDs and metric values. Never make claims not grounded in the provided data."
- **User:** Serialized experiment context (recent runs, patterns, notebook insights, project context) + recent memory entries
- **Response schema:** narrative, key_patterns, best_config, exploration_gaps, focus_areas

### Suggestion Prompt
- **System:** Same base persona + "Propose 3-5 concrete next experiments ranked by expected impact. Each must include hypothesis, parameters, expected metric impact, priority, and rationale citing specific runs. Incorporate past feedback."
- **User:** Serialized experiment context + detected patterns + past feedback entries
- **Response schema:** suggestions array with id, hypothesis, parameters, expected_impact, priority, rationale

## Memory System

The agent persists data to memory after key actions:
- `/analyze-experiments` → stores best_metric, pattern_types, total_runs, narrative
- `/suggest-next` → stores suggestion_count, suggestion_ids
- `/feedback` → stores suggestion_id, outcome, notes, timestamp

Memory is consumed by:
- Drift detection (comparing current vs. stored analysis)
- Suggestion generation (loading feedback from last 30 days)
- Free-form answer quality (recent command history provides conversation context)

## Output Principles

- **Cite run IDs and metrics.** Every claim must reference specific data.
- **Deterministic fallback.** All commands produce useful output without an LLM — the LLM enriches but is never required.
- **Sparse data awareness.** With fewer than 3 records, state limitations explicitly rather than hallucinating patterns.
- **Feedback loop closure.** Suggestions evolve based on recorded outcomes — the agent learns from user feedback across sessions.
- **No fabricated claims.** When uncertain, say so explicitly. Never invent experiment results or patterns not grounded in the data.
