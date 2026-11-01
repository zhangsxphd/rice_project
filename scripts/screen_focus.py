"""Compatibility entry point for screening v2. Requires explicit input and new output.

The prior fixed-row implementation remains available in Git history and the
unmodified local historical screen_focus.py. It must not determine inclusion.
"""
try:
    from .screen_v2 import main
except ImportError:
    from screen_v2 import main

if __name__ == '__main__':
    main()
