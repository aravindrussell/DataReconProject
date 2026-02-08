"""
Compatibility shim for Oracle drivers.

Tries to import `cx_Oracle` first; if unavailable, falls back to `oracledb`.
Provides `makedsn` and `connect` functions with a stable interface used by
the project's Oracle connector.
"""
from typing import Optional

_driver = None
_driver_name = None

try:
    import cx_Oracle as _drv  # type: ignore
    _driver = _drv
    _driver_name = 'cx_Oracle'
except Exception:
    try:
        import oracledb as _drv  # type: ignore
        _driver = _drv
        _driver_name = 'oracledb'
    except Exception:
        _driver = None
        _driver_name = None


def _ensure_driver():
    if _driver is None:
        raise ImportError("No Oracle driver found. Install 'oracledb' or 'cx_Oracle'.")


def makedsn(host: str, port: int, service_name: Optional[str] = None, sid: Optional[str] = None) -> str:
    """Create a DSN string.

    Attempts to call the underlying driver's `makedsn` if provided; otherwise
    falls back to a simple host:port/service pattern which works for thin
    connections in many cases.
    """
    _ensure_driver()
    if hasattr(_driver, 'makedsn'):
        try:
            # Try signature with service_name first
            return _driver.makedsn(host, port, service_name=service_name)  # type: ignore
        except TypeError:
            # Fallback to positional or sid-based signature
            if sid is not None:
                return _driver.makedsn(host, port, sid)  # type: ignore
            return _driver.makedsn(host, port)  # type: ignore

    # Fallback simple DSN
    if service_name:
        return f"{host}:{port}/{service_name}"
    if sid:
        return f"{host}:{port}/{sid}"
    return f"{host}:{port}"


def connect(user: str, password: str, dsn: str, **kwargs):
    """Connect using the underlying Oracle driver.

    Returns the raw connection object from whichever driver is available.
    """
    _ensure_driver()
    # Both cx_Oracle and oracledb expose a connect function with similar args
    return _driver.connect(user=user, password=password, dsn=dsn, **kwargs)


def driver_name() -> Optional[str]:
    return _driver_name
