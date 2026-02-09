# run_as_module.py
import runpy
import sys
from pathlib import Path

# Get the file path from the first argument
file_path = Path(sys.argv[1]).resolve()
workspace = Path(__file__).parent.resolve()

# Convert file path to module path
module_path = (
    file_path.relative_to(workspace).with_suffix("").as_posix().replace("/", ".")
)

# Run it as a module
runpy.run_module(module_path, run_name="__main__")
