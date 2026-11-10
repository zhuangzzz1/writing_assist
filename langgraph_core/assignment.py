import re

from agents.utils import InputValidationError


FRAMEWORK_COMPONENTS = {
    "CER": ("Claim", "Evidence", "Reasoning"),
    "RACE": ("Restate", "Answer", "Cite", "Explain"),
    "RACES": ("Restate", "Answer", "Cite", "Explain", "Sum up"),
    "MEAL": ("Main idea", "Evidence", "Analysis", "Link"),
}
MAX_FRAMEWORK_NAME_CHARS = 80
MAX_FRAMEWORK_COMPONENT_CHARS = 80
MAX_FRAMEWORK_COMPONENTS = 12


def _canonical_framework(value: str) -> str:
    normalized = " ".join(value.split())
    for name in FRAMEWORK_COMPONENTS:
        if normalized.casefold() == name.casefold():
            return name
    return normalized


def _negated_framework(directions: str, start: int, end: int) -> bool:
    prefix = directions[max(0, start - 48):start].lower()
    suffix = directions[end:end + 32].lower()
    if re.search(r"(?:do not|don't|avoid|without|no|not)\s+(?:\w+\s+){0,3}$", prefix):
        return True
    return bool(
        re.match(
            r"\s+(?:(?:is|are|isn't|aren't)\s+)?(?:not\s+(?:required|needed)|optional)\b",
            suffix,
        )
    )


def detect_framework(teacher_directions: str) -> tuple[str, list[str]]:
    matches = []
    for match in re.finditer(r"\bRACES?\b|\bCER\b|\bMEAL\b", teacher_directions, re.I):
        if not _negated_framework(teacher_directions, match.start(), match.end()):
            name = _canonical_framework(match.group())
            if name not in matches:
                matches.append(name)
    if len(matches) > 1:
        raise InputValidationError(
            "Use the framework fields to identify one required framework and its components."
        )
    if not matches:
        return "", []
    name = matches[0]
    return name, list(FRAMEWORK_COMPONENTS[name])


def resolve_framework(
    framework_name: str,
    framework_components: list[str] | None,
    teacher_directions: str,
) -> tuple[str, list[str]]:
    if not isinstance(framework_name, str):
        raise InputValidationError("Framework name must be text.")
    name = _canonical_framework(framework_name)
    if len(name) > MAX_FRAMEWORK_NAME_CHARS:
        raise InputValidationError("Framework name is too long.")
    if framework_components is None:
        if name:
            if name not in FRAMEWORK_COMPONENTS:
                raise InputValidationError(
                    "List the required components for a custom framework."
                )
            return name, list(FRAMEWORK_COMPONENTS[name])
        return detect_framework(teacher_directions)
    if not isinstance(framework_components, list) or any(
        not isinstance(component, str) for component in framework_components
    ):
        raise InputValidationError("Framework components must be a list of text values.")
    components = [" ".join(component.split()) for component in framework_components]
    components = [component for component in components if component]
    if components and not name:
        raise InputValidationError("Name the framework that uses these components.")
    if not components:
        if not name:
            return "", []
        if name not in FRAMEWORK_COMPONENTS:
            raise InputValidationError(
                "List the required components for a custom framework."
            )
        components = list(FRAMEWORK_COMPONENTS[name])
    if len(components) > MAX_FRAMEWORK_COMPONENTS:
        raise InputValidationError("Use no more than 12 framework components.")
    if any(len(component) > MAX_FRAMEWORK_COMPONENT_CHARS for component in components):
        raise InputValidationError("A framework component name is too long.")
    identities = [component.casefold() for component in components]
    if len(identities) != len(set(identities)):
        raise InputValidationError("Framework components must be unique.")
    return name, components


def language_corrections_optional(teacher_directions: str) -> bool:
    patterns = (
        r"\blanguage\s+(?:corrections|fixes)\s+(?:are\s+)?optional\b",
        r"\bgrammar\s+(?:corrections|fixes)\s+(?:are\s+)?optional\b",
        r"\bmechanics\s+(?:are\s+)?optional\b",
        r"\b(?:do not|don't)\s+focus\s+on\s+(?:language|grammar|mechanics)\b",
        r"\b(?:mechanics|grammar|language\s+errors)\s+are\s+not\s+graded\b",
    )
    return any(re.search(pattern, teacher_directions, re.I) for pattern in patterns)
