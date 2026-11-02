def graph_dot(agent_path: list[str]) -> str:
    node_for_step = {
        "Assessment Coordinator": "assessment",
        "Clarification": "clarification",
        "Instructional Support Agent": "support",
        "Teacher Review": "teacher",
        "Direct Response": "direct",
    }
    executed = [node_for_step.get(step) for step in agent_path]
    executed = [node for node in executed if node]
    active = set(executed)
    active_edges = set(zip(executed, executed[1:]))
    if executed:
        active_edges.add(("start", executed[0]))
        if executed[-1] in {"support", "teacher", "direct"}:
            active_edges.add((executed[-1], "end"))

    labels = {
        "start": "Start",
        "assessment": "Assessment Coordinator",
        "clarification": "Ask Clarification",
        "support": "Support Agent",
        "teacher": "Teacher Review",
        "direct": "Direct Response",
        "end": "End",
    }
    lines = [
        "digraph WritingAssistant {",
        'rankdir="TB";',
        'bgcolor="transparent";',
        'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10];',
        'edge [fontname="Helvetica", fontsize=9];',
    ]
    for node, label in labels.items():
        color = "#D1FAE5" if node in active or node == "start" else "#F3F4F6"
        border = "#059669" if node in active else "#9CA3AF"
        lines.append(
            f'{node} [label="{label}", fillcolor="{color}", color="{border}"];'
        )
    edges = [
        ("start", "assessment", ""),
        ("assessment", "clarification", "clarify"),
        ("clarification", "assessment", "answer"),
        ("assessment", "support", "support"),
        ("assessment", "teacher", "human review"),
        ("assessment", "direct", "no issues"),
        ("support", "end", ""),
        ("teacher", "end", ""),
        ("direct", "end", ""),
    ]
    for source, target, label in edges:
        is_active = (source, target) in active_edges
        color = "#059669" if is_active else "#9CA3AF"
        width = "3" if is_active else "1"
        lines.append(
            f'{source} -> {target} [label="{label}", color="{color}", '
            f'fontcolor="{color}", penwidth={width}];'
        )
    lines.append("}")
    return "\n".join(lines)
