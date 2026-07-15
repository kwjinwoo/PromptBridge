---
id: project-terminology
title: Project Terminology
type: glossary
status: proposed
authority: canonical
relations:
  - type: part-of
    target: product-overview
  - type: defines
    target: protected-elements
last_reviewed: 2026-07-15
---

# Project Terminology

| Term | Meaning |
|---|---|
| Source prompt | Korean developer instruction selected by the user |
| Transformed prompt | English prompt produced by PromptBridge |
| Protected element | Technical content that must satisfy an exact preservation rule |
| Protected token | Placeholder associated with a protected element |
| Transformation | Translation or refinement without answering the instruction |
| Translate Mode | Default mode that changes language without adding requirements |
| Refine Mode | Explicit mode that restructures reasonably clear intent |
| Preservation validation | Deterministic comparison of protected source and output elements |
| Requirement coverage | Whether all requested actions and constraints remain represented |
| Automatic application | Replacing the selected source text without manual confirmation |
| Runtime | Local service or library that performs LLM inference |
| Target context | Application and input location from which the source prompt was copied |
