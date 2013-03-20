"""Utlity functions."""

def check_insteon_id(ident):
    """Check if `ident` matches insteon identifier constraints."""
    if type(ident) != bytes:
        return False

    if len(ident) != 3:
        return False

    return True
