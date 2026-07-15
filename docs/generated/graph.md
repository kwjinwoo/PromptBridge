---
id: generated-knowledge-graph
title: Generated Knowledge Graph
type: generated
status: active
authority: derived
relations:
  - type: related-to
    target: docs-index
last_reviewed: 2026-07-15
---

# Generated Knowledge Graph

This view is derived from canonical document frontmatter. It provides a compact
overview; canonical frontmatter remains the complete relation source. The
[`document-index.json`](document-index.json) file maps stable IDs to paths.

## Product and architecture

```mermaid
graph TD
    overview["Product Overview"] -->|"defines"| invariants["Product Invariants"]
    overview -->|"defines"| terms["Project Terminology"]
    overview -->|"constrains"| system["System Overview"]

    invariants -->|"constrains"| translate["Translate Mode"]
    invariants -->|"constrains"| refine["Refine Mode"]
    invariants -->|"constrains"| pipeline["Prompt Pipeline"]
    invariants -->|"constrains"| validator["Preservation Validator"]
    invariants -->|"constrains"| clipboard["Clipboard State Machine"]
    invariants -->|"constrains"| failure["Failure Policy"]
    invariants -->|"constrains"| privacy["Privacy Boundary"]

    translate -->|"depends-on"| protected["Protected Elements"]
    refine -->|"depends-on"| protected
    protected -->|"informs"| pipeline
    pipeline -->|"triggers"| validator
    clipboard -->|"depends-on"| pipeline
    failure -->|"constrains"| pipeline
    failure -->|"constrains"| clipboard
    privacy -->|"constrains"| system
    privacy -->|"constrains"| clipboard
```

## Evaluation and decisions

```mermaid
graph LR
    method["Evaluation Methodology"] -->|"validates"| translate["Translate Mode"]
    method -->|"validates"| validator["Preservation Validator"]
    method -->|"informs"| models["Local Model Comparison"]
    method -->|"informs"| compatibility["Application Compatibility"]
    models -->|"informs"| ollama["ADR-0002: Ollama MVP"]
    local["ADR-0001: Local First"] -->|"informs"| ollama
    local -->|"constrains"| system["System Overview"]
```

## Roadmap

```mermaid
graph LR
    roadmap["Project Roadmap"] --> phase1["Phase 1: Quality"]
    roadmap --> phase2["Phase 2: Preservation"]
    roadmap --> phase3["Phase 3: Hotkey"]
    roadmap --> phase4["Phase 4: macOS App"]
    roadmap --> phase5["Phase 5: Refine"]
    roadmap --> phase6["Phase 6: Improvements"]
    phase1 --> phase2 --> phase3 --> phase4 --> phase5 --> phase6
    status["Project Status"] -->|"tracks"| roadmap
```

## Development tooling

```mermaid
graph LR
    precommit["Pre-commit Conventions"] -->|"validates"| graph["Knowledge Graph"]
    precommit -->|"informs"| status["Project Status"]
    commit["Commit Convention"] -->|"part-of"| precommit
    style["Code Documentation Convention"] -->|"part-of"| precommit
    skills["Agent Workflow Skills"] -->|"depends-on"| precommit
    skills -->|"related-to"| status
    index["Documentation Index"] -->|"related-to"| precommit
    index -->|"related-to"| commit
    index -->|"related-to"| style
    index -->|"related-to"| skills
```
