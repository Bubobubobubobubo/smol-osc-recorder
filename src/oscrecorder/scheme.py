def dirt_basic(address: str, *args) -> dict:
    """Basic schema for recording OSC messages."""
    args = args[0]
    return {"address": address, "args": args}


def dirt_strip(address: str, *args) -> dict:
    """Return only odd arguments from args"""
    args = args[0][1::2]
    return {"address": address, "args": args}


def basic(address: str, *args) -> dict:
    """Basic schema for recording OSC messages."""
    return {"address": address, "args": args}


def only_numbers(address: str, *args) -> dict:
    """Return only numbers from args."""
    return {
        "address": address,
        "args": [arg for arg in args if isinstance(arg, (int, float))],
    }


ALL_SCHEMES = {
    "dirt_basic": dirt_basic,
    "dirt_strip": dirt_strip,
    "basic": basic,
    "only_numbers": only_numbers,
}
