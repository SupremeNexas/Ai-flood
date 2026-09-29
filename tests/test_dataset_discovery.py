"""
Unit tests for Sen1Floods11 dataset discovery and integrity.
"""

import os
import pytest
from src.data.validation import discover_chips, validate_single_chip


def test_discover_chips():
    data_dir = "data/samples"
    chips = discover_chips(data_dir)
    assert len(chips) > 0, "No chips discovered in sample directory"

    # Check that discovered stems have valid layer paths
    for stem, layers in chips.items():
        assert "S1Hand" in layers or "LabelHand" in layers
        for lyr_name, path in layers.items():
            assert os.path.exists(path), f"Path does not exist: {path}"


def test_validate_single_chip():
    data_dir = "data/samples"
    chips = discover_chips(data_dir)
    first_stem = list(chips.keys())[0]

    is_valid, stats, issues = validate_single_chip(first_stem, chips[first_stem])
    assert is_valid is True, f"Chip {first_stem} failed validation: {issues}"
    assert stats["s1_bands"] == 2
    assert stats["s1_height"] == 512
    assert stats["s1_width"] == 512
    assert stats["label_height"] == 512
    assert stats["label_width"] == 512
