"""Read-only import of parent's independently verified GF2 repair implementation."""
from pathlib import Path
import sys,importlib.util
sys.dont_write_bytecode=True
PATH=Path(__file__).resolve().parents[1]/'independent'/'penalty_bound.py'
spec=importlib.util.spec_from_file_location('parent_verified_repair_api',PATH);REPAIR=importlib.util.module_from_spec(spec);spec.loader.exec_module(REPAIR)
