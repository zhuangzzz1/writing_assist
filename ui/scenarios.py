import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from langgraph_core.state import GenreSelection, GradeLevel


SCENARIO_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "scenarios.json"
ACCEPTANCE_PATH = Path(__file__).resolve().parents[1] / "test_cases" / "v3" / "acceptance.json"


@dataclass(frozen=True)
class PracticeScenario:
    scenario_id: str
    name: str
    grade_level: GradeLevel
    genre: GenreSelection
    draft: str
    assignment_prompt: str
    teacher_directions: str
    source_material: str
    student_concerns: str
    fixture_version: str


@dataclass(frozen=True)
class RevisionFixture:
    draft: str
    goal_selection: str
    self_reports: dict[str, str]


@dataclass(frozen=True)
class AcceptanceScenario(PracticeScenario):
    number: int
    acceptance_focus: str
    revisions: tuple[RevisionFixture, ...]
    finish: bool
    genre_correction: str
    clarification_answers: tuple[str, ...]


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


def load_acceptance_scenarios() -> list[AcceptanceScenario]:
    data = json.loads(ACCEPTANCE_PATH.read_text(encoding="utf-8"))
    bases = {scenario.scenario_id: scenario for scenario in load_scenarios()}
    scenarios = []
    for item in data["scenarios"]:
        base = bases.get(item.get("base_scenario", ""))

        def value(key: str) -> Any:
            return item.get(key, getattr(base, key, "") if base else "")

        scenarios.append(
            AcceptanceScenario(
                number=item["number"],
                scenario_id=item["scenario_id"],
                name=item["name"],
                grade_level=cast(GradeLevel, value("grade_level")),
                genre=cast(GenreSelection, value("genre")),
                draft=value("draft"),
                assignment_prompt=value("assignment_prompt"),
                teacher_directions=value("teacher_directions"),
                source_material=value("source_material"),
                student_concerns=value("student_concerns"),
                fixture_version=data["fixture_version"],
                acceptance_focus=item["acceptance_focus"],
                revisions=tuple(
                    RevisionFixture(
                        draft=revision["draft"],
                        goal_selection=revision.get("goal_selection", "first"),
                        self_reports=revision.get("self_reports", {}),
                    )
                    for revision in item.get("revisions", [])
                ),
                finish=item.get("finish", False),
                genre_correction=item.get("genre_correction", ""),
                clarification_answers=tuple(item.get("clarification_answers", [])),
            )
        )
    return scenarios


def get_acceptance_scenario(number: int) -> AcceptanceScenario:
    for scenario in load_acceptance_scenarios():
        if scenario.number == number:
            return scenario
    raise KeyError(number)
