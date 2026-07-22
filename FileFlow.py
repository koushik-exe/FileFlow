#!/usr/bin/env python
# ----------------------------------------------------------------------
# FileFlow - Smart File Organizer
# Entry point
# ----------------------------------------------------------------------
# This file is kept as a thin entry point for backward compatibility.
# All application logic now lives in the fileflow/ package.
# ----------------------------------------------------------------------
from fileflow.ui.main_window import FileFlowApp

if __name__ == "__main__":
    app = FileFlowApp()
    app.mainloop()
