"""Criteria and risk register entry. [slide] = from Team_I10_Risk_Reduction_Plan.pptx; [default] = our choice."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Criteria:
    limit_m: float = 0.10          # [slide 9] error <= 10 cm at every point (I4, P5)
    min_readings: int = 20         # [slide 9] >= 20 readings per point
    grid_spacing_m: float = 0.5    # [slide 9] marked grid, 0.5 m spacing
    min_points: int = 9            # [default] at least a 3 x 3 grid
    confidence: float = 0.95       # [default] for the exceedance bound


# Slides 2, 3, and 9 of the plan
RISK = {
    "id": "R2",
    "name": "Indoor localization",
    "chance": "Medium",
    "impact": "High",
    "owner": "Dayana",
    "response": "Prevent: prototype onboard sensing early and measure position error",
    "warning_signal": "Bench position error above 10 cm",
    "if_fails": "Add markers or a second sensor and retest",
}
