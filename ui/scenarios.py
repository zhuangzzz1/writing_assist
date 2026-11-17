import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, cast

from langgraph_core.state import GenreSelection, GradeLevel


SCENARIO_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "scenarios.json"
ACCEPTANCE_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "acceptance.json"
EXPERIMENT_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "live_el_contrasts.json"
SUPPORT_COMPARISON_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "prompt_revision_support.json"
COORDINATOR_TARGETED_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "prompt_revision_coordinator.json"
FINAL_HISTORY_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "final_history_contrasts.json"
FINAL_REGRESSION_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "final_regression_contrasts.json"
READABILITY_COVERAGE_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "readability_coverage.json"
PHASE1_DEVELOPMENT_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "phase1_development.json"
PHASE1_TRANSFER_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "phase1_transfer.json"


@dataclass(frozen=True)
class PracticeScenario:
    scenario_id: str
    name: str
    grade_level: GradeLevel
    genre: GenreSelection
    draft: str
    assignment_prompt: str
    teacher_directions: str
    framework_name: str
    framework_components: tuple[str, ...]
    source_material: str
    student_concerns: str
    fixture_version: str


@dataclass(frozen=True)
class RevisionFixture:
    draft: str
    goal_selection: str
    self_reports: dict[str, str]
    goal_indices: tuple[int, ...] = ()
    goal_references: tuple[str, ...] = ()


@dataclass(frozen=True)
class AcceptanceScenario(PracticeScenario):
    number: int
    acceptance_focus: str
    revisions: tuple[RevisionFixture, ...]
    finish: bool
    genre_correction: str
    clarification_answers: tuple[str, ...]
    expected_outcomes: tuple[str, ...] = ()
    workstreams: tuple[str, ...] = ()
    controlled_round: dict[str, Any] | None = None
    support_only: bool = False
    allow_direct_response_finish: bool = False
    lineage: dict[str, Any] = field(default_factory=dict)
    review_annotations: dict[str, Any] = field(default_factory=dict)


def load_scenarios() -> list[PracticeScenario]:
    data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
    version = data["fixture_version"]
    scenarios = []
    for item in data["scenarios"]:
        scenarios.append(
            PracticeScenario(
                scenario_id=item["scenario_id"],
                name=item["name"],
                grade_level=cast(GradeLevel, item["grade_level"]),
                genre=cast(GenreSelection, item["genre"]),
                draft=item["draft"],
                assignment_prompt=item["assignment_prompt"],
                teacher_directions=item["teacher_directions"],
                framework_name=item.get("framework_name", ""),
                framework_components=tuple(item.get("framework_components", [])),
                source_material=item["source_material"],
                student_concerns=item["student_concerns"],
                fixture_version=version,
            )
        )
    return scenarios


def get_scenario(scenario_id: str) -> PracticeScenario:
    for scenario in load_scenarios():
        if scenario.scenario_id == scenario_id:
            return scenario
    raise KeyError(scenario_id)


def _load_review_scenarios(path: Path) -> list[AcceptanceScenario]:
    data = json.loads(path.read_text(encoding="utf-8"))
    snapshots = data.get("snapshots", {})
    bases = {scenario.scenario_id: scenario for scenario in load_scenarios()}
    controlled_rounds = {
        item["number"]: item.get("controlled_round") for item in data["scenarios"]
    }

    def resolve_draft(item: dict[str, Any], default: str = "") -> str:
        snapshot_id = item.get("draft_snapshot", "")
        if snapshot_id:
            return snapshots[snapshot_id]
        return item.get("draft", default)

    scenarios = []
    for item in data["scenarios"]:
        base = bases.get(item.get("base_scenario", ""))

        def value(key: str) -> Any:
            return item.get(key, getattr(base, key, "") if base else "")

        controlled_round = (
            item.get("controlled_round")
            or controlled_rounds.get(item.get("controlled_round_from"))
        )
        if controlled_round:
            controlled_round = dict(controlled_round)
            original_snapshot = controlled_round.get("original_draft_snapshot", "")
            if original_snapshot:
                controlled_round["original_draft"] = snapshots[original_snapshot]

        scenarios.append(
            AcceptanceScenario(
                number=item["number"],
                scenario_id=item["scenario_id"],
                name=item["name"],
                grade_level=cast(GradeLevel, value("grade_level")),
                genre=cast(GenreSelection, value("genre")),
                draft=resolve_draft(item, value("draft")),
                assignment_prompt=value("assignment_prompt"),
                teacher_directions=value("teacher_directions"),
                framework_name=value("framework_name"),
                framework_components=tuple(value("framework_components") or ()),
                source_material=value("source_material"),
                student_concerns=value("student_concerns"),
                fixture_version=data["fixture_version"],
                acceptance_focus=item["acceptance_focus"],
                revisions=tuple(
                    RevisionFixture(
                        draft=resolve_draft(revision),
                        goal_selection=revision.get("goal_selection", "first"),
                        self_reports=revision.get("self_reports", {}),
                        goal_indices=tuple(revision.get("goal_indices", [])),
                        goal_references=tuple(revision.get("goal_references", [])),
                    )
                    for revision in item.get("revisions", [])
                ),
                finish=item.get("finish", False),
                genre_correction=item.get("genre_correction", ""),
                clarification_answers=tuple(item.get("clarification_answers", [])),
                expected_outcomes=tuple(item.get("expected_outcomes", [])),
                workstreams=tuple(item.get("workstreams", [])),
                controlled_round=controlled_round,
                support_only=item.get("support_only", False),
                allow_direct_response_finish=item.get(
                    "allow_direct_response_finish", False
                ),
                lineage=item.get("lineage", {}),
                review_annotations=item.get("review_annotations", {}),
            )
        )
    return scenarios


def load_acceptance_scenarios() -> list[AcceptanceScenario]:
    return _load_review_scenarios(ACCEPTANCE_PATH)


def load_experiment_scenarios() -> list[AcceptanceScenario]:
    return _load_review_scenarios(EXPERIMENT_PATH)


def load_support_comparison_scenarios() -> list[AcceptanceScenario]:
    existing = [
        scenario for scenario in load_experiment_scenarios() if scenario.support_only
    ]
    additional = _load_review_scenarios(SUPPORT_COMPARISON_PATH)
    return [
        replace(scenario, number=number)
        for number, scenario in enumerate([*existing, *additional], start=1)
    ]


def load_coordinator_targeted_scenarios() -> list[AcceptanceScenario]:
    targeted = _load_review_scenarios(COORDINATOR_TARGETED_PATH)
    strong = replace(
        get_acceptance_scenario(10),
        expected_outcomes=(
            "Affirm the strong draft without manufacturing a revision issue.",
        ),
        workstreams=("CR",),
    )
    imaginative = replace(get_experiment_scenario(16), workstreams=("CR",))
    combined = [*targeted, strong, imaginative]
    return [
        replace(scenario, number=number)
        for number, scenario in enumerate(combined, start=1)
    ]


def load_final_history_scenarios() -> list[AcceptanceScenario]:
    return _load_review_scenarios(FINAL_HISTORY_PATH)


def load_final_regression_scenarios() -> list[AcceptanceScenario]:
    return _load_review_scenarios(FINAL_REGRESSION_PATH)


def load_readability_coverage_scenarios() -> list[AcceptanceScenario]:
    return _load_review_scenarios(READABILITY_COVERAGE_PATH)


def load_phase1_development_scenarios() -> list[AcceptanceScenario]:
    return _load_review_scenarios(PHASE1_DEVELOPMENT_PATH)


def load_phase1_transfer_scenarios() -> list[AcceptanceScenario]:
    return _load_review_scenarios(PHASE1_TRANSFER_PATH)


def get_acceptance_scenario(number: int) -> AcceptanceScenario:
    for scenario in load_acceptance_scenarios():
        if scenario.number == number:
            return scenario
    raise KeyError(number)


def get_experiment_scenario(number: int) -> AcceptanceScenario:
    for scenario in load_experiment_scenarios():
        if scenario.number == number:
            return scenario
    raise KeyError(number)
