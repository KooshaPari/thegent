# ANTE: Agent Organization

> Extracted from Ante docs. Fetched 2026-02-20

Ante home page

Search...



Navigation

Agent Org

Agent Organization (Experimental)
Agent Org
Agent Organization (Experimental)
Multi-agent architecture patterns for orchestrating collaborative AI agents
Ante supports multiple patterns for organizing agents to work together. Each architecture trades off between autonomy, coordination overhead, and result quality.
​

Independent
Agents work in parallel on the same problem with no interaction. An aggregator synthesizes their outputs at the end.
Best for: tasks where diverse independent perspectives improve quality (brainstorming, redundant verification).









#mermaid-_r_s_-1771584168161{font-family:inherit;font-size:16px;fill:#ccc;}#mermaid-_r_s_-1771584168161 .error-icon{fill:#a44141;}#mermaid-_r_s_-1771584168161 .error-text{fill:#ddd;stroke:#ddd;}#mermaid-_r_s_-1771584168161 .edge-thickness-normal{stroke-width:1px;}#mermaid-_r_s_-1771584168161 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-_r_s_-1771584168161 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-_r_s_-1771584168161 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-_r_s_-1771584168161 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-_r_s_-1771584168161 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-_r_s_-1771584168161 .marker{fill:lightgrey;stroke:lightgrey;}#mermaid-_r_s_-1771584168161 .marker.cross{stroke:lightgrey;}#mermaid-_r_s_-1771584168161 svg{font-family:inherit;font-size:16px;}#mermaid-_r_s_-1771584168161 p{margin:0;}#mermaid-_r_s_-1771584168161 .label{font-family:inherit;color:#ccc;}#mermaid-_r_s_-1771584168161 .cluster-label text{fill:#F9FFFE;}#mermaid-_r_s_-1771584168161 .cluster-label span{color:#F9FFFE;}#mermaid-_r_s_-1771584168161 .cluster-label span p{background-color:transparent;}#mermaid-_r_s_-1771584168161 .label text,#mermaid-_r_s_-1771584168161 span{fill:#ccc;color:#ccc;}#mermaid-_r_s_-1771584168161 .node rect,#mermaid-_r_s_-1771584168161 .node circle,#mermaid-_r_s_-1771584168161 .node ellipse,#mermaid-_r_s_-1771584168161 .node polygon,#mermaid-_r_s_-1771584168161 .node path{fill:#1f2020;stroke:#ccc;stroke-width:1px;}#mermaid-_r_s_-1771584168161 .rough-node .label text,#mermaid-_r_s_-1771584168161 .node .label text,#mermaid-_r_s_-1771584168161 .image-shape .label,#mermaid-_r_s_-1771584168161 .icon-shape .label{text-anchor:middle;}#mermaid-_r_s_-1771584168161 .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#mermaid-_r_s_-1771584168161 .rough-node .label,#mermaid-_r_s_-1771584168161 .node .label,#mermaid-_r_s_-1771584168161 .image-shape .label,#mermaid-_r_s_-1771584168161 .icon-shape .label{text-align:center;}#mermaid-_r_s_-1771584168161 .node.clickable{cursor:pointer;}#mermaid-_r_s_-1771584168161 .root .anchor path{fill:lightgrey!important;stroke-width:0;stroke:lightgrey;}#mermaid-_r_s_-1771584168161 .arrowheadPath{fill:lightgrey;}#mermaid-_r_s_-1771584168161 .edgePath .path{stroke:lightgrey;stroke-width:2.0px;}#mermaid-_r_s_-1771584168161 .flowchart-link{stroke:lightgrey;fill:none;}#mermaid-_r_s_-1771584168161 .edgeLabel{background-color:hsl(0, 0%, 34.4117647059%);text-align:center;}#mermaid-_r_s_-1771584168161 .edgeLabel p{background-color:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_s_-1771584168161 .edgeLabel rect{opacity:0.5;background-color:hsl(0, 0%, 34.4117647059%);fill:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_s_-1771584168161 .labelBkg{background-color:rgba(87.75, 87.75, 87.75, 0.5);}#mermaid-_r_s_-1771584168161 .cluster rect{fill:hsl(180, 1.5873015873%, 28.3529411765%);stroke:rgba(255, 255, 255, 0.25);stroke-width:1px;}#mermaid-_r_s_-1771584168161 .cluster text{fill:#F9FFFE;}#mermaid-_r_s_-1771584168161 .cluster span{color:#F9FFFE;}#mermaid-_r_s_-1771584168161 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:inherit;font-size:12px;background:hsl(20, 1.5873015873%, 12.3529411765%);border:1px solid rgba(255, 255, 255, 0.25);border-radius:2px;pointer-events:none;z-index:100;}#mermaid-_r_s_-1771584168161 .flowchartTitleText{text-anchor:middle;font-size:18px;fill:#ccc;}#mermaid-_r_s_-1771584168161 rect.text{fill:none;stroke-width:0;}#mermaid-_r_s_-1771584168161 .icon-shape,#mermaid-_r_s_-1771584168161 .image-shape{background-color:hsl(0, 0%, 34.4117647059%);text-align:center;}#mermaid-_r_s_-1771584168161 .icon-shape p,#mermaid-_r_s_-1771584168161 .image-shape p{background-color:hsl(0, 0%, 34.4117647059%);padding:2px;}#mermaid-_r_s_-1771584168161 .icon-shape rect,#mermaid-_r_s_-1771584168161 .image-shape rect{opacity:0.5;background-color:hsl(0, 0%, 34.4117647059%);fill:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_s_-1771584168161 :root{--mermaid-font-family:inherit;}#mermaid-_r_s_-1771584168161 .control>*{fill:#e1f5ff!important;stroke:#4aa3df!important;color:#00324d!important;}#mermaid-_r_s_-1771584168161 .control span{fill:#e1f5ff!important;stroke:#4aa3df!important;color:#00324d!important;}#mermaid-_r_s_-1771584168161 .control tspan{fill:#00324d!important;}#mermaid-_r_s_-1771584168161 .agent>*{fill:#fff4e6!important;stroke:#e0a96d!important;color:#4a2c00!important;}#mermaid-_r_s_-1771584168161 .agent span{fill:#fff4e6!important;stroke:#e0a96d!important;color:#4a2c00!important;}#mermaid-_r_s_-1771584168161 .agent tspan{fill:#4a2c00!important;}#mermaid-_r_s_-1771584168161 .agg>*{fill:#e6f3ff!important;stroke:#6ea8fe!important;color:#002b55!important;}#mermaid-_r_s_-1771584168161 .agg span{fill:#e6f3ff!important;stroke:#6ea8fe!important;color:#002b55!important;}#mermaid-_r_s_-1771584168161 .agg tspan{fill:#002b55!important;}









Start
Parallel fan-out
Agent 1
Agent 2
Agent 3
Barrier / sync
Aggregator Synthesis
End
​

Decentralized
Agents run in parallel rounds, reading each other’s prior outputs and proposing refinements. After a fixed number of rounds, consensus is formed without a central coordinator.
Best for: debate-style reasoning, peer review, or negotiation where no single authority should dominate.









#mermaid-_r_t_-1771584168162{font-family:inherit;font-size:16px;fill:#ccc;}#mermaid-_r_t_-1771584168162 .error-icon{fill:#a44141;}#mermaid-_r_t_-1771584168162 .error-text{fill:#ddd;stroke:#ddd;}#mermaid-_r_t_-1771584168162 .edge-thickness-normal{stroke-width:1px;}#mermaid-_r_t_-1771584168162 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-_r_t_-1771584168162 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-_r_t_-1771584168162 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-_r_t_-1771584168162 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-_r_t_-1771584168162 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-_r_t_-1771584168162 .marker{fill:lightgrey;stroke:lightgrey;}#mermaid-_r_t_-1771584168162 .marker.cross{stroke:lightgrey;}#mermaid-_r_t_-1771584168162 svg{font-family:inherit;font-size:16px;}#mermaid-_r_t_-1771584168162 p{margin:0;}#mermaid-_r_t_-1771584168162 .label{font-family:inherit;color:#ccc;}#mermaid-_r_t_-1771584168162 .cluster-label text{fill:#F9FFFE;}#mermaid-_r_t_-1771584168162 .cluster-label span{color:#F9FFFE;}#mermaid-_r_t_-1771584168162 .cluster-label span p{background-color:transparent;}#mermaid-_r_t_-1771584168162 .label text,#mermaid-_r_t_-1771584168162 span{fill:#ccc;color:#ccc;}#mermaid-_r_t_-1771584168162 .node rect,#mermaid-_r_t_-1771584168162 .node circle,#mermaid-_r_t_-1771584168162 .node ellipse,#mermaid-_r_t_-1771584168162 .node polygon,#mermaid-_r_t_-1771584168162 .node path{fill:#1f2020;stroke:#ccc;stroke-width:1px;}#mermaid-_r_t_-1771584168162 .rough-node .label text,#mermaid-_r_t_-1771584168162 .node .label text,#mermaid-_r_t_-1771584168162 .image-shape .label,#mermaid-_r_t_-1771584168162 .icon-shape .label{text-anchor:middle;}#mermaid-_r_t_-1771584168162 .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#mermaid-_r_t_-1771584168162 .rough-node .label,#mermaid-_r_t_-1771584168162 .node .label,#mermaid-_r_t_-1771584168162 .image-shape .label,#mermaid-_r_t_-1771584168162 .icon-shape .label{text-align:center;}#mermaid-_r_t_-1771584168162 .node.clickable{cursor:pointer;}#mermaid-_r_t_-1771584168162 .root .anchor path{fill:lightgrey!important;stroke-width:0;stroke:lightgrey;}#mermaid-_r_t_-1771584168162 .arrowheadPath{fill:lightgrey;}#mermaid-_r_t_-1771584168162 .edgePath .path{stroke:lightgrey;stroke-width:2.0px;}#mermaid-_r_t_-1771584168162 .flowchart-link{stroke:lightgrey;fill:none;}#mermaid-_r_t_-1771584168162 .edgeLabel{background-color:hsl(0, 0%, 34.4117647059%);text-align:center;}#mermaid-_r_t_-1771584168162 .edgeLabel p{background-color:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_t_-1771584168162 .edgeLabel rect{opacity:0.5;background-color:hsl(0, 0%, 34.4117647059%);fill:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_t_-1771584168162 .labelBkg{background-color:rgba(87.75, 87.75, 87.75, 0.5);}#mermaid-_r_t_-1771584168162 .cluster rect{fill:hsl(180, 1.5873015873%, 28.3529411765%);stroke:rgba(255, 255, 255, 0.25);stroke-width:1px;}#mermaid-_r_t_-1771584168162 .cluster text{fill:#F9FFFE;}#mermaid-_r_t_-1771584168162 .cluster span{color:#F9FFFE;}#mermaid-_r_t_-1771584168162 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:inherit;font-size:12px;background:hsl(20, 1.5873015873%, 12.3529411765%);border:1px solid rgba(255, 255, 255, 0.25);border-radius:2px;pointer-events:none;z-index:100;}#mermaid-_r_t_-1771584168162 .flowchartTitleText{text-anchor:middle;font-size:18px;fill:#ccc;}#mermaid-_r_t_-1771584168162 rect.text{fill:none;stroke-width:0;}#mermaid-_r_t_-1771584168162 .icon-shape,#mermaid-_r_t_-1771584168162 .image-shape{background-color:hsl(0, 0%, 34.4117647059%);text-align:center;}#mermaid-_r_t_-1771584168162 .icon-shape p,#mermaid-_r_t_-1771584168162 .image-shape p{background-color:hsl(0, 0%, 34.4117647059%);padding:2px;}#mermaid-_r_t_-1771584168162 .icon-shape rect,#mermaid-_r_t_-1771584168162 .image-shape rect{opacity:0.5;background-color:hsl(0, 0%, 34.4117647059%);fill:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_t_-1771584168162 :root{--mermaid-font-family:inherit;}#mermaid-_r_t_-1771584168162 .control>*{fill:#e1f5ff!important;stroke:#4aa3df!important;color:#00324d!important;}#mermaid-_r_t_-1771584168162 .control span{fill:#e1f5ff!important;stroke:#4aa3df!important;color:#00324d!important;}#mermaid-_r_t_-1771584168162 .control tspan{fill:#00324d!important;}#mermaid-_r_t_-1771584168162 .agent>*{fill:#fff4e6!important;stroke:#e0a96d!important;color:#4a2c00!important;}#mermaid-_r_t_-1771584168162 .agent span{fill:#fff4e6!important;stroke:#e0a96d!important;color:#4a2c00!important;}#mermaid-_r_t_-1771584168162 .agent tspan{fill:#4a2c00!important;}#mermaid-_r_t_-1771584168162 .state>*{fill:#f3f4f6!important;stroke:#9ca3af!important;color:#111827!important;}#mermaid-_r_t_-1771584168162 .state span{fill:#f3f4f6!important;stroke:#9ca3af!important;color:#111827!important;}#mermaid-_r_t_-1771584168162 .state tspan{fill:#111827!important;}#mermaid-_r_t_-1771584168162 .decision>*{fill:#ffe6f0!important;stroke:#f472b6!important;color:#4a044e!important;}#mermaid-_r_t_-1771584168162 .decision span{fill:#ffe6f0!important;stroke:#f472b6!important;color:#4a044e!important;}#mermaid-_r_t_-1771584168162 .decision tspan{fill:#4a044e!important;}












No
Yes

Start
Initialize
Shared board proposals so far
Parallel: read & propose
Agent 1 Read board + propose delta
Agent 2 Read board + propose delta
Agent 3 Read board + propose delta
Barrier / sync
Append deltas to board
Stop? round limit or convergence
Consensus formation from board
End
​

Centralized Iterative
A central orchestrator decomposes the problem, dispatches agents in parallel, evaluates their results, and decides whether to refine or finish.
Best for: complex tasks that benefit from top-down planning with quality gates (code generation with review, multi-step research).









#mermaid-_r_u_-1771584168163{font-family:inherit;font-size:16px;fill:#ccc;}#mermaid-_r_u_-1771584168163 .error-icon{fill:#a44141;}#mermaid-_r_u_-1771584168163 .error-text{fill:#ddd;stroke:#ddd;}#mermaid-_r_u_-1771584168163 .edge-thickness-normal{stroke-width:1px;}#mermaid-_r_u_-1771584168163 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-_r_u_-1771584168163 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-_r_u_-1771584168163 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-_r_u_-1771584168163 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-_r_u_-1771584168163 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-_r_u_-1771584168163 .marker{fill:lightgrey;stroke:lightgrey;}#mermaid-_r_u_-1771584168163 .marker.cross{stroke:lightgrey;}#mermaid-_r_u_-1771584168163 svg{font-family:inherit;font-size:16px;}#mermaid-_r_u_-1771584168163 p{margin:0;}#mermaid-_r_u_-1771584168163 .label{font-family:inherit;color:#ccc;}#mermaid-_r_u_-1771584168163 .cluster-label text{fill:#F9FFFE;}#mermaid-_r_u_-1771584168163 .cluster-label span{color:#F9FFFE;}#mermaid-_r_u_-1771584168163 .cluster-label span p{background-color:transparent;}#mermaid-_r_u_-1771584168163 .label text,#mermaid-_r_u_-1771584168163 span{fill:#ccc;color:#ccc;}#mermaid-_r_u_-1771584168163 .node rect,#mermaid-_r_u_-1771584168163 .node circle,#mermaid-_r_u_-1771584168163 .node ellipse,#mermaid-_r_u_-1771584168163 .node polygon,#mermaid-_r_u_-1771584168163 .node path{fill:#1f2020;stroke:#ccc;stroke-width:1px;}#mermaid-_r_u_-1771584168163 .rough-node .label text,#mermaid-_r_u_-1771584168163 .node .label text,#mermaid-_r_u_-1771584168163 .image-shape .label,#mermaid-_r_u_-1771584168163 .icon-shape .label{text-anchor:middle;}#mermaid-_r_u_-1771584168163 .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#mermaid-_r_u_-1771584168163 .rough-node .label,#mermaid-_r_u_-1771584168163 .node .label,#mermaid-_r_u_-1771584168163 .image-shape .label,#mermaid-_r_u_-1771584168163 .icon-shape .label{text-align:center;}#mermaid-_r_u_-1771584168163 .node.clickable{cursor:pointer;}#mermaid-_r_u_-1771584168163 .root .anchor path{fill:lightgrey!important;stroke-width:0;stroke:lightgrey;}#mermaid-_r_u_-1771584168163 .arrowheadPath{fill:lightgrey;}#mermaid-_r_u_-1771584168163 .edgePath .path{stroke:lightgrey;stroke-width:2.0px;}#mermaid-_r_u_-1771584168163 .flowchart-link{stroke:lightgrey;fill:none;}#mermaid-_r_u_-1771584168163 .edgeLabel{background-color:hsl(0, 0%, 34.4117647059%);text-align:center;}#mermaid-_r_u_-1771584168163 .edgeLabel p{background-color:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_u_-1771584168163 .edgeLabel rect{opacity:0.5;background-color:hsl(0, 0%, 34.4117647059%);fill:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_u_-1771584168163 .labelBkg{background-color:rgba(87.75, 87.75, 87.75, 0.5);}#mermaid-_r_u_-1771584168163 .cluster rect{fill:hsl(180, 1.5873015873%, 28.3529411765%);stroke:rgba(255, 255, 255, 0.25);stroke-width:1px;}#mermaid-_r_u_-1771584168163 .cluster text{fill:#F9FFFE;}#mermaid-_r_u_-1771584168163 .cluster span{color:#F9FFFE;}#mermaid-_r_u_-1771584168163 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:inherit;font-size:12px;background:hsl(20, 1.5873015873%, 12.3529411765%);border:1px solid rgba(255, 255, 255, 0.25);border-radius:2px;pointer-events:none;z-index:100;}#mermaid-_r_u_-1771584168163 .flowchartTitleText{text-anchor:middle;font-size:18px;fill:#ccc;}#mermaid-_r_u_-1771584168163 rect.text{fill:none;stroke-width:0;}#mermaid-_r_u_-1771584168163 .icon-shape,#mermaid-_r_u_-1771584168163 .image-shape{background-color:hsl(0, 0%, 34.4117647059%);text-align:center;}#mermaid-_r_u_-1771584168163 .icon-shape p,#mermaid-_r_u_-1771584168163 .image-shape p{background-color:hsl(0, 0%, 34.4117647059%);padding:2px;}#mermaid-_r_u_-1771584168163 .icon-shape rect,#mermaid-_r_u_-1771584168163 .image-shape rect{opacity:0.5;background-color:hsl(0, 0%, 34.4117647059%);fill:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_u_-1771584168163 :root{--mermaid-font-family:inherit;}#mermaid-_r_u_-1771584168163 .control>*{fill:#e1f5ff!important;stroke:#4aa3df!important;color:#00324d!important;}#mermaid-_r_u_-1771584168163 .control span{fill:#e1f5ff!important;stroke:#4aa3df!important;color:#00324d!important;}#mermaid-_r_u_-1771584168163 .control tspan{fill:#00324d!important;}#mermaid-_r_u_-1771584168163 .agent>*{fill:#fff4e6!important;stroke:#e0a96d!important;color:#4a2c00!important;}#mermaid-_r_u_-1771584168163 .agent span{fill:#fff4e6!important;stroke:#e0a96d!important;color:#4a2c00!important;}#mermaid-_r_u_-1771584168163 .agent tspan{fill:#4a2c00!important;}#mermaid-_r_u_-1771584168163 .orch>*{fill:#e6f3ff!important;stroke:#6ea8fe!important;color:#002b55!important;}#mermaid-_r_u_-1771584168163 .orch span{fill:#e6f3ff!important;stroke:#6ea8fe!important;color:#002b55!important;}#mermaid-_r_u_-1771584168163 .orch tspan{fill:#002b55!important;}#mermaid-_r_u_-1771584168163 .eval>*{fill:#ffe6e6!important;stroke:#fb7185!important;color:#4c0519!important;}#mermaid-_r_u_-1771584168163 .eval span{fill:#ffe6e6!important;stroke:#fb7185!important;color:#4c0519!important;}#mermaid-_r_u_-1771584168163 .eval tspan{fill:#4c0519!important;}#mermaid-_r_u_-1771584168163 .state>*{fill:#f3f4f6!important;stroke:#9ca3af!important;color:#111827!important;}#mermaid-_r_u_-1771584168163 .state span{fill:#f3f4f6!important;stroke:#9ca3af!important;color:#111827!important;}#mermaid-_r_u_-1771584168163 .state tspan{fill:#111827!important;}#mermaid-_r_u_-1771584168163 .decision>*{fill:#ffe6f0!important;stroke:#f472b6!important;color:#4a044e!important;}#mermaid-_r_u_-1771584168163 .decision span{fill:#ffe6f0!important;stroke:#f472b6!important;color:#4a044e!important;}#mermaid-_r_u_-1771584168163 .decision tspan{fill:#4a044e!important;}














No: refine
Yes

Start
Setup
Workspace tasks + results
Orchestrator Decompose / refine plan
Parallel: execute tasks
Agent 1
Agent 2
Agent 3
Barrier / sync
Write results to workspace
Orchestrator Evaluate quality
Done?
Final Synthesis
End
​

Hybrid Iterative
Combines centralized orchestration with decentralized peer refinement. The orchestrator plans and dispatches agents, then agents refine each other’s work in a peer round before the orchestrator evaluates.
Best for: high-quality collaborative output where both structured planning and peer feedback matter (collaborative writing, architecture design).









#mermaid-_r_v_-1771584168163{font-family:inherit;font-size:16px;fill:#ccc;}#mermaid-_r_v_-1771584168163 .error-icon{fill:#a44141;}#mermaid-_r_v_-1771584168163 .error-text{fill:#ddd;stroke:#ddd;}#mermaid-_r_v_-1771584168163 .edge-thickness-normal{stroke-width:1px;}#mermaid-_r_v_-1771584168163 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-_r_v_-1771584168163 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-_r_v_-1771584168163 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-_r_v_-1771584168163 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-_r_v_-1771584168163 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-_r_v_-1771584168163 .marker{fill:lightgrey;stroke:lightgrey;}#mermaid-_r_v_-1771584168163 .marker.cross{stroke:lightgrey;}#mermaid-_r_v_-1771584168163 svg{font-family:inherit;font-size:16px;}#mermaid-_r_v_-1771584168163 p{margin:0;}#mermaid-_r_v_-1771584168163 .label{font-family:inherit;color:#ccc;}#mermaid-_r_v_-1771584168163 .cluster-label text{fill:#F9FFFE;}#mermaid-_r_v_-1771584168163 .cluster-label span{color:#F9FFFE;}#mermaid-_r_v_-1771584168163 .cluster-label span p{background-color:transparent;}#mermaid-_r_v_-1771584168163 .label text,#mermaid-_r_v_-1771584168163 span{fill:#ccc;color:#ccc;}#mermaid-_r_v_-1771584168163 .node rect,#mermaid-_r_v_-1771584168163 .node circle,#mermaid-_r_v_-1771584168163 .node ellipse,#mermaid-_r_v_-1771584168163 .node polygon,#mermaid-_r_v_-1771584168163 .node path{fill:#1f2020;stroke:#ccc;stroke-width:1px;}#mermaid-_r_v_-1771584168163 .rough-node .label text,#mermaid-_r_v_-1771584168163 .node .label text,#mermaid-_r_v_-1771584168163 .image-shape .label,#mermaid-_r_v_-1771584168163 .icon-shape .label{text-anchor:middle;}#mermaid-_r_v_-1771584168163 .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#mermaid-_r_v_-1771584168163 .rough-node .label,#mermaid-_r_v_-1771584168163 .node .label,#mermaid-_r_v_-1771584168163 .image-shape .label,#mermaid-_r_v_-1771584168163 .icon-shape .label{text-align:center;}#mermaid-_r_v_-1771584168163 .node.clickable{cursor:pointer;}#mermaid-_r_v_-1771584168163 .root .anchor path{fill:lightgrey!important;stroke-width:0;stroke:lightgrey;}#mermaid-_r_v_-1771584168163 .arrowheadPath{fill:lightgrey;}#mermaid-_r_v_-1771584168163 .edgePath .path{stroke:lightgrey;stroke-width:2.0px;}#mermaid-_r_v_-1771584168163 .flowchart-link{stroke:lightgrey;fill:none;}#mermaid-_r_v_-1771584168163 .edgeLabel{background-color:hsl(0, 0%, 34.4117647059%);text-align:center;}#mermaid-_r_v_-1771584168163 .edgeLabel p{background-color:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_v_-1771584168163 .edgeLabel rect{opacity:0.5;background-color:hsl(0, 0%, 34.4117647059%);fill:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_v_-1771584168163 .labelBkg{background-color:rgba(87.75, 87.75, 87.75, 0.5);}#mermaid-_r_v_-1771584168163 .cluster rect{fill:hsl(180, 1.5873015873%, 28.3529411765%);stroke:rgba(255, 255, 255, 0.25);stroke-width:1px;}#mermaid-_r_v_-1771584168163 .cluster text{fill:#F9FFFE;}#mermaid-_r_v_-1771584168163 .cluster span{color:#F9FFFE;}#mermaid-_r_v_-1771584168163 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:inherit;font-size:12px;background:hsl(20, 1.5873015873%, 12.3529411765%);border:1px solid rgba(255, 255, 255, 0.25);border-radius:2px;pointer-events:none;z-index:100;}#mermaid-_r_v_-1771584168163 .flowchartTitleText{text-anchor:middle;font-size:18px;fill:#ccc;}#mermaid-_r_v_-1771584168163 rect.text{fill:none;stroke-width:0;}#mermaid-_r_v_-1771584168163 .icon-shape,#mermaid-_r_v_-1771584168163 .image-shape{background-color:hsl(0, 0%, 34.4117647059%);text-align:center;}#mermaid-_r_v_-1771584168163 .icon-shape p,#mermaid-_r_v_-1771584168163 .image-shape p{background-color:hsl(0, 0%, 34.4117647059%);padding:2px;}#mermaid-_r_v_-1771584168163 .icon-shape rect,#mermaid-_r_v_-1771584168163 .image-shape rect{opacity:0.5;background-color:hsl(0, 0%, 34.4117647059%);fill:hsl(0, 0%, 34.4117647059%);}#mermaid-_r_v_-1771584168163 :root{--mermaid-font-family:inherit;}#mermaid-_r_v_-1771584168163 .control>*{fill:#e1f5ff!important;stroke:#4aa3df!important;color:#00324d!important;}#mermaid-_r_v_-1771584168163 .control span{fill:#e1f5ff!important;stroke:#4aa3df!important;color:#00324d!important;}#mermaid-_r_v_-1771584168163 .control tspan{fill:#00324d!important;}#mermaid-_r_v_-1771584168163 .agent>*{fill:#fff4e6!important;stroke:#e0a96d!important;color:#4a2c00!important;}#mermaid-_r_v_-1771584168163 .agent span{fill:#fff4e6!important;stroke:#e0a96d!important;color:#4a2c00!important;}#mermaid-_r_v_-1771584168163 .agent tspan{fill:#4a2c00!important;}#mermaid-_r_v_-1771584168163 .peer>*{fill:#f0e6ff!important;stroke:#a78bfa!important;color:#2e1065!important;}#mermaid-_r_v_-1771584168163 .peer span{fill:#f0e6ff!important;stroke:#a78bfa!important;color:#2e1065!important;}#mermaid-_r_v_-1771584168163 .peer tspan{fill:#2e1065!important;}#mermaid-_r_v_-1771584168163 .orch>*{fill:#e6f3ff!important;stroke:#6ea8fe!important;color:#002b55!important;}#mermaid-_r_v_-1771584168163 .orch span{fill:#e6f3ff!important;stroke:#6ea8fe!important;color:#002b55!important;}#mermaid-_r_v_-1771584168163 .orch tspan{fill:#002b55!important;}#mermaid-_r_v_-1771584168163 .eval>*{fill:#ffe6e6!important;stroke:#fb7185!important;color:#4c0519!important;}#mermaid-_r_v_-1771584168163 .eval span{fill:#ffe6e6!important;stroke:#fb7185!important;color:#4c0519!important;}#mermaid-_r_v_-1771584168163 .eval tspan{fill:#4c0519!important;}#mermaid-_r_v_-1771584168163 .state>*{fill:#f3f4f6!important;stroke:#9ca3af!important;color:#111827!important;}#mermaid-_r_v_-1771584168163 .state span{fill:#f3f4f6!important;stroke:#9ca3af!important;color:#111827!important;}#mermaid-_r_v_-1771584168163 .state tspan{fill:#111827!important;}#mermaid-_r_v_-1771584168163 .decision>*{fill:#ffe6f0!important;stroke:#f472b6!important;color:#4a044e!important;}#mermaid-_r_v_-1771584168163 .decision span{fill:#ffe6f0!important;stroke:#f472b6!important;color:#4a044e!important;}#mermaid-_r_v_-1771584168163 .decision tspan{fill:#4a044e!important;}























No: continue
Yes

Start
Setup
Workspace drafts + notes
Orchestrator Plan
Parallel: draft
Agent 1
Agent 2
Agent 3
Barrier / sync
Write drafts to workspace
Parallel: peer refine
Peer 1 Refine using others
Peer 2 Refine using others
Peer 3 Refine using others
Barrier / sync
Write refinements to workspace
Orchestrator Evaluate quality
Done?
Final Synthesis
End
​

Choosing an architecture
Architecture
Coordination
Iteration
Use when
Independent
None
Single pass
You need diverse perspectives without interaction overhead
Decentralized
Peer-to-peer
Fixed rounds
Agents should self-organize without a central authority
Centralized Iterative
Orchestrator-driven
Quality-gated
You need structured decomposition with evaluation checkpoints
Hybrid Iterative
Orchestrator + peers
Quality-gated
You want both top-down planning and bottom-up peer refinement

Previous
Offline Mode (Experimental)

Next

Powered by



Assistant



Responses are generated using AI and may contain mistakes.




