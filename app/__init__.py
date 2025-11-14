"""App package initializer.

Ensures Python treats the `app` directory as a package in all environments.
Exports commonly used modules for convenience.
"""

# Re-export frequently used modules (optional convenience)
try:
    from . import auth  # noqa: F401
    from . import middleware  # noqa: F401
except Exception:
    # In case of partial environments during build, ignore import errors here.
    pass
