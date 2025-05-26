import os
import sys

# Prepend the project root directory to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import tkinter
from main import ScaffoldApp

# Stub out GUI init/destroy so tests don't load Tcl/Tk
ScaffoldApp.__init__ = lambda self: None
ScaffoldApp.destroy  = lambda self: None
