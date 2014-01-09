"""
Utlity functions.
"""

def check_insteon_id(identifier):
    """
    Makes sure an identifier is a reasonable one for INSTEON devices.

    :param identifier: ID to check.
    :type identifier: bytes
    """
    if type(identifier) != bytes:
        return False

    if len(identifier) != 3:
        return False

    return True
