"""Guideline-category and input-validation tests for educational TOF interpretation."""
import math
import pytest
from neuromuscular_blockade_train_of_four_agent.tof import interpret_tof


@pytest.mark.parametrize("count,ptc,ratio,category", [
    (0, None, None, "INDETERMINATE"),
    (0, 0, None, "COMPLETE"),
    (0, 1, None, "DEEP"),
    (0, 9, None, "DEEP"),
    (1, None, None, "MODERATE"),
    (2, None, None, "MODERATE"),
    (3, None, None, "MODERATE"),
    (4, None, None, "INDETERMINATE"),
    (4, None, 0.3999, "SHALLOW"),
    (4, None, 0.4, "MINIMAL"),
    (4, None, 0.8999, "MINIMAL"),
    (4, None, 0.9, "RECOVERED"),
    (4, None, 1.0, "RECOVERED"),
])
def test_tof_classification(count, ptc, ratio, category):
    result = interpret_tof(count, ptc, ratio)
    assert result["category"] == category
    assert result["recovery_threshold_met"] is (category == "RECOVERED")


@pytest.mark.parametrize("count,ptc,ratio", [
    (-1, None, None), (5, None, None), (2.5, None, None),
    (True, None, None), (0, -1, None), (0, 31, None),
    (1, 1, None), (4, 1, None), (2, None, 0.5),
    (4, None, -0.1), (4, None, 1.51), (4, None, float("nan")),
    (4, None, float("inf")), (4, None, True),
])
def test_tof_rejects_invalid_or_incompatible_inputs(count, ptc, ratio):
    with pytest.raises(ValueError):
        interpret_tof(count, ptc, ratio)
