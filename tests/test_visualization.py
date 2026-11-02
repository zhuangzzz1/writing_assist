from ui.visualization import graph_dot


def test_graph_visualization_marks_executed_path():
    dot = graph_dot(["Assessment Coordinator", "Instructional Support Agent"])

    assert "Assessment Coordinator" in dot
    assert "clarification -> assessment" in dot
    assert ('assessment -> support [label="support", color="#059669"' in dot)
    assert ('assessment -> teacher [label="human review", color="#9CA3AF"' in dot)
