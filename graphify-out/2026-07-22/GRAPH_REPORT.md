# Graph Report - FileFlow  (2026-07-22)

## Corpus Check
- 8 files · ~15,513 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 104 nodes · 136 edges · 15 communities (7 shown, 8 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- HeroFolderCard
- FileFlowApp
- graphify Rules
- UI Styling Skill
- ._worker
- phase1_organize
- revert_organize
- get_file_date
- Slide System
- CIP Design
- Icon Design
- Logo Design
- Accessibility Rules
- Navigation Patterns
- Performance Rules

## God Nodes (most connected - your core abstractions)
1. `FileFlowApp` - 21 edges
2. `phase1_organize()` - 9 edges
3. `FileFlow 🔥` - 8 edges
4. `graphify Rules` - 8 edges
5. `HeroFolderCard` - 6 edges
6. `StatCard` - 6 edges
7. `get_file_hash()` - 5 edges
8. `revert_organize()` - 5 edges
9. `get_unique_filename()` - 4 edges
10. `get_file_date()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `graphify Workflow` --conceptually_related_to--> `graphify Rules`  [INFERRED]
  .agents/workflows/graphify.md → .agents/rules/graphify.md
- `Design Skill` --references--> `Design System`  [EXTRACTED]
  .agents/rules/design.md → .agents/rules/design-system.md
- `Design System` --conceptually_related_to--> `UI Styling Skill`  [EXTRACTED]
  .agents/rules/design-system.md → .agents/rules/ui-styling.md
- `Design Skill` --references--> `UI Styling Skill`  [EXTRACTED]
  .agents/rules/design.md → .agents/rules/ui-styling.md
- `Banner Design` --calls--> `UI/UX Pro Max`  [EXTRACTED]
  .agents/rules/design.md → .agents/rules/ui-ux-pro-max.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Design Orchestration Flow** — agents_rules_design_design, agents_rules_design_system_design_system, agents_rules_ui_styling_ui_styling, agents_rules_ui_ux_pro_max_ui_ux_pro_max [INFERRED 0.90]
- **Token-Driven UI Implementation** — agents_rules_design_system_token_architecture, agents_rules_ui_styling_tailwind_css, agents_rules_ui_styling_shadcn_ui [EXTRACTED 0.85]
- **graphify Tooling Suite** — _agents_rules_graphify_graphify_query, _agents_rules_graphify_query_graph, _agents_rules_graphify_graphify_path, _agents_rules_graphify_shortest_path, _agents_rules_graphify_graphify_explain, _agents_rules_graphify_get_node, _agents_rules_graphify_graphify_update [EXTRACTED 1.00]

## Communities (15 total, 8 thin omitted)

### Community 0 - "HeroFolderCard"
Cohesion: 0.18
Nodes (6): HeroFolderCard, Hero folder selection card with glass styling & gradient button., Premium 28px card metric display with circular icon container., Render elegant empty state illustration., Overview page — folder selectors, pipeline, stats, activity, action buttons., StatCard

### Community 1 - "FileFlowApp"
Cohesion: 0.16
Nodes (10): FileFlowApp, Pipeline page — detailed two-phase progress view., Statistics page — larger dedicated view of all 8 stat cards., Activity page — full activity log/history., Settings page — default paths, theme toggle, version info., Toggle between Dark and Light appearance mode., FileFlow Main Window – Premium Modern Desktop UI., Add recent activity item (keeping max 5). Also populates full log. (+2 more)

### Community 2 - "graphify Rules"
Cohesion: 0.22
Nodes (9): get_node, graphify Rules, graphify explain, graphify path, graphify query, graphify update, query_graph, shortest_path (+1 more)

### Community 3 - "UI Styling Skill"
Cohesion: 0.29
Nodes (8): Banner Design, Design Skill, Social Photos, Design System, shadcn/ui, Tailwind CSS, UI Styling Skill, UI/UX Pro Max

### Community 4 - "._worker"
Cohesion: 0.29
Nodes (4): get_folder_size(), Update Pipeline page stat labels from _stats dict., Update Statistics page stat cards from _stats dict., Recursive size in bytes.

### Community 5 - "phase1_organize"
Cohesion: 0.12
Nodes (22): format_size(), get_category(), get_file_date(), get_file_hash(), get_image_date(), get_unique_filename(), log(), phase1_organize() (+14 more)

### Community 6 - "revert_organize"
Cohesion: 0.18
Nodes (10): 🔨 Building the executable yourself, 🤝 Contributing, ✨ Features, FileFlow 🔥, 🚀 Installation, 📄 License, Option 1: Run from source (recommended), Option 2: Standalone executable (Windows) (+2 more)

## Knowledge Gaps
- **27 isolated node(s):** `✨ Features`, `📋 Requirements`, `Option 1: Run from source (recommended)`, `Option 2: Standalone executable (Windows)`, `🎯 Usage` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FileFlowApp` connect `FileFlowApp` to `HeroFolderCard`, `._worker`, `phase1_organize`, `get_file_date`?**
  _High betweenness centrality (0.239) - this node is a cross-community bridge._
- **Why does `HeroFolderCard` connect `HeroFolderCard` to `phase1_organize`, `get_file_date`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `StatCard` connect `HeroFolderCard` to `FileFlowApp`, `._worker`, `phase1_organize`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **What connects `✨ Features`, `📋 Requirements`, `Option 1: Run from source (recommended)` to the rest of the system?**
  _27 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `phase1_organize` be split into smaller, more focused modules?**
  _Cohesion score 0.12318840579710146 - nodes in this community are weakly interconnected._