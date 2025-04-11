"""
StableVITON Model Runner
Author: Zhihao Cao
Maintainer: Zixin Ding and Zhihao Cao

This utility module is responsible for invoking the StableVITON model
to generate virtual try-on images using subprocess from within the Flask backend.

It spawns a new console and executes `app.py` inside the StableVITON model folder,
passing the necessary image paths and clothing category as arguments.

Usage:
    run_stableviton(input_image_path, cloth_path, category)
"""

import os
import subprocess
import sys
from pathlib import Path

# Get stableviton path relative to this utils file
stableviton_path = Path(__file__).resolve().parent.parent / "models" / "StableVITON"

#current_file_path = Path(__file__).absolute()
#stableviton_path = current_file_path.parent.parent / "models" / "StableVITON"

ENV_NAMES = {
    "main": "OVDR",         
    "model": "StableViton"   
}

def run_in_conda(env_name, command_args):
    """change the virtual environment and run the python file in the same virtual environment
    
    Args:
        env_name (str): environment name
        command_args (list): python file name and arguments
    Returns:
        subprocess.Popen: subprocess object
    """
    conda_env = ENV_NAMES[env_name]
    
    
    full_cmd = [
        "cmd.exe", "/c",
        "conda", "activate", conda_env,
        "&&",
        "python",
        *command_args
    ]
    
    return subprocess.Popen(
        " ".join(full_cmd),
        cwd=str(stableviton_path),
        env=os.environ.copy(),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

def run_stableviton(input_image_path, cloth_path, category):
    """
    Launch StableVITON's app.py to process try-on generation.

    Args:
        input_image_path (str): Absolute path to the user's full-body image.
        cloth_path (str): Absolute path to the selected clothing image.
        category (str): Clothing type (e.g. "tops", "bottoms", "dresses").

    Raises:
        RuntimeError: If StableVITON script exits with a non-zero code.
    """

    result = run_in_conda(
            env_name="model",
            command_args=[
                "app.py",
                os.path.abspath(input_image_path),
                os.path.abspath(cloth_path),
                category
            ]
        )
    # the env,cwd and sys.executable ensure that execute the python file in the same virtual environment
    result.wait()

    if result.returncode != 0:
        raise RuntimeError("StableVITON execution failed")
    
    return True
