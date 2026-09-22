from __future__ import annotations


class SafetyPolicy:
    """Adds visible guardrails without presenting them as manual-derived evidence."""

    HIGH_ENERGY_TERMS = {
        "electrical",
        "voltage",
        "energized",
        "motor",
        "breaker",
        "wiring",
        "panel",
        "rotating",
        "pressure",
        "hydraulic",
    }
    SAFEGUARD_PATTERNS = (
        "bypass",
        "disable interlock",
        "defeat interlock",
        "override interlock",
        "disable safeguard",
        "remove guard",
    )

    def is_safeguard_bypass(self, question: str) -> bool:
        lowered = question.casefold()
        direct_match = any(pattern in lowered for pattern in self.SAFEGUARD_PATTERNS)
        unsafe_verb = any(verb in lowered for verb in ("bypass", "disable", "defeat", "override"))
        safeguard_noun = any(
            noun in lowered
            for noun in ("guard", "interlock", "thermal switch", "safeguard", "relay")
        )
        return direct_match or (unsafe_verb and safeguard_noun)

    def warnings_for(self, question: str) -> list[str]:
        lowered = question.casefold()
        warnings: list[str] = []
        if any(term in lowered for term in self.HIGH_ENERGY_TERMS):
            warnings.append(
                "Safety gate: follow the site's lockout/tagout, PPE, and qualified-personnel "
                "requirements before inspection or intervention."
            )
        if self.is_safeguard_bypass(question):
            warnings.append(
                "The assistant will not recommend bypassing safeguards or protective interlocks."
            )
        return warnings
