"""
Configuration loader and utility helper functions.
Supports environment variables and yaml configs.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict


def get_project_root() -> Path:
    """Returns the absolute root directory of the project."""
    return Path(__file__).resolve().parent.parent.parent


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Loads YAML configuration file.
    Allows overriding dataset root path via DATASET_ROOT environment variable.
    """
    if config_path is None:
        env_config = os.getenv("CONFIG_PATH")
        if env_config and os.path.exists(env_config):
            config_path = env_config
        else:
            config_path = str(get_project_root() / "configs" / "config.yaml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Handle environment variable overrides for paths
    env_data_root = os.getenv("DATASET_ROOT")
    if env_data_root:
        config["paths"]["data_root"] = env_data_root
        config["paths"]["raw_dir"] = os.path.join(env_data_root, "raw")
        config["paths"]["samples_dir"] = os.path.join(env_data_root, "samples")
        config["paths"]["splits_dir"] = os.path.join(env_data_root, "raw", "splits")

    return config


def get_device() -> str:
    """
    Auto-detects the best available computational device:
    CUDA (NVIDIA GPU) -> MPS (Apple Silicon GPU) -> CPU.
    """
    import torch

    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"
