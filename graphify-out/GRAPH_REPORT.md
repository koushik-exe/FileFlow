# Graph Report - FileFlow  (2026-07-22)

## Corpus Check
- 8 files · ~17,280 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 150 nodes · 204 edges · 17 communities (9 shown, 8 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.9)
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
- ._set_theme
- Slide System
- CIP Design
- Icon Design
- Logo Design
- Accessibility Rules
- Navigation Patterns
- Performance Rules
- _Theme

## God Nodes (most connected - your core abstractions)
1. `FileFlowApp` - 26 edges
2. `HoverMixin` - 9 edges
3. `phase1_organize()` - 9 edges
4. `FileFlow 🔥` - 8 edges
5. `graphify Rules` - 8 edges
6. `HeroFolderCard` - 7 edges
7. `StatCard` - 7 edges
8. `get_file_hash()` - 5 edges
9. `revert_organize()` - 5 edges
10. `Animator` - 4 edges

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

## Communities (17 total, 8 thin omitted)

### Community 0 - "HeroFolderCard"
Cohesion: 0.14
Nodes (10): Animator, HoverMixin, Manages smooth property transitions for widgets using after() callbacks., Smoothly transition a widget property from current to end value., Smoothly transition widget dimensions., Adds hover scale + lift + border glow to any CTkFrame-based card., Override in subclass for specific hover behavior., Override in subclass for specific hover behavior. (+2 more)

### Community 1 - "FileFlowApp"
Cohesion: 0.11
Nodes (15): crossfade_switch(), FileFlowApp, Render elegant empty state illustration., Add recent activity item (keeping max 5). Also populates full log., Main thread queue drainer for activity updates., Switch to the given page and highlight the active nav button., Direct page switch without animation (used by crossfade)., Overview page - folder selectors, pipeline, stats, activity, action buttons. (+7 more)

### Community 2 - "graphify Rules"
Cohesion: 0.22
Nodes (9): get_node, graphify Rules, graphify explain, graphify path, graphify query, graphify update, query_graph, shortest_path (+1 more)

### Community 3 - "UI Styling Skill"
Cohesion: 0.29
Nodes (8): Banner Design, Design Skill, Social Photos, Design System, shadcn/ui, Tailwind CSS, UI Styling Skill, UI/UX Pro Max

### Community 4 - "._worker"
Cohesion: 0.15
Nodes (10): animate_counter(), format_size(), get_folder_size(), Update Pipeline page stat labels from _stats dict., Update Statistics page stat cards from _stats dict., Animate a label's text from 0 to target value., Show an expanding success ring animation., Recursive size in bytes. (+2 more)

### Community 5 - "phase1_organize"
Cohesion: 0.11
Nodes (22): get_category(), get_file_date(), get_file_hash(), get_image_date(), get_unique_filename(), is_reduce_motion_enabled(), log(), phase1_organize() (+14 more)

### Community 6 - "revert_organize"
Cohesion: 0.17
Nodes (11): 🔨 Building the executable yourself, 🤝 Contributing, ✨ Features, FileFlow 🔥, 🚀 Installation, Known Issue: Windows Smart App Control, 📄 License, Option 1: Run from source (recommended) (+3 more)

### Community 7 - "get_file_date"
Cohesion: 0.13
Nodes (9): HeroFolderCard, make_button_premium(), Update Pipeline page phase badges (phase1/phase2/complete)., Add press/release and hover glow animations to a CTkButton., Add focus border glow to a CTkEntry., Shake a widget horizontally., Hero folder selection card with glass styling & gradient button., setup_input_focus() (+1 more)

### Community 8 - "._set_theme"
Cohesion: 0.25
Nodes (4): Toggle theme from the header button., Set theme mode and update all UI elements., Toggle between Dark and Light appearance mode (from Settings)., Reapply theme colors to all major containers after theme switch.

## Knowledge Gaps
- **28 isolated node(s):** `✨ Features`, `📋 Requirements`, `Option 1: Run from source (recommended)`, `Option 2: Standalone executable (Windows)`, `Known Issue: Windows Smart App Control` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FileFlowApp` connect `FileFlowApp` to `._set_theme`, `._worker`, `phase1_organize`, `get_file_date`?**
  _High betweenness centrality (0.272) - this node is a cross-community bridge._
- **Why does `HoverMixin` connect `HeroFolderCard` to `phase1_organize`, `get_file_date`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `Animator` connect `HeroFolderCard` to `phase1_organize`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **What connects `✨ Features`, `📋 Requirements`, `Option 1: Run from source (recommended)` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `HeroFolderCard` be split into smaller, more focused modules?**
  _Cohesion score 0.13725490196078433 - nodes in this community are weakly interconnected._
- **Should `FileFlowApp` be split into smaller, more focused modules?**
  _Cohesion score 0.11375661375661375 - nodes in this community are weakly interconnected._
- **Should `phase1_organize` be split into smaller, more focused modules?**
  _Cohesion score 0.10541310541310542 - nodes in this community are weakly interconnected._