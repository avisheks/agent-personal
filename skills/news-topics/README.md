# News Topic Configs

Each YAML file defines a topic specialization for the `news-summarizer` skill.

## Schema

```yaml
name: Human-readable topic name
slug: kebab-case-identifier (used in invocation and filenames)
description: One-paragraph description of the topic scope

output_dir: relative path for output files
file_prefix: prefix for output filenames (e.g., "agentic-ai" → "agentic-ai-2026-07-WK30-news.md")

topics_of_interest:
  Category Name:
    - Subtopic 1
    - Subtopic 2

trusted_sources:
  prefer:
    - Source 1
    - Source 2
  avoid:
    - Anti-pattern 1

personalized_relevance:
  weight_highest:
    - Topic A
  weight_medium:
    - Topic B
  weight_lower:
    - Topic C

implications_sections:
  - title: "Section Title"
    focus: What this section should analyze
```

## Adding a New Topic

1. Copy an existing YAML as a starting point
2. Update all fields for the new domain
3. Create the output directory in `.local/data/`
4. Invoke with: `Run news-summarizer with topic: your-slug`
