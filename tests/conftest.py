import sys
import pathlib

# Ensure workspace root is in sys.path for test discovery
root_dir = pathlib.Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
