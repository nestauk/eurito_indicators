import json

from eurito_indicators import project_dir


LOOKUP_DIR = f'{project_dir}/inputs/sdg/official'


def sdg_name_lookup():
    """Loads lookup between goal numbers and their full names.

    Returns:
        A dict with integer keys 1 - 17 and their corresponding SDG names.
    """
    return _sdg_lookup("sdg_names.json")


def sdg_hex_color_lookup():
    """Loads lookup between goal numbers and their official hex color codes. 
    
    Returns:
        A dict with integer keys 1 - 17 and their corresponding official hex 
        color codes.
    """
    return _sdg_lookup("sdg_hex_color_codes.json")


def _sdg_lookup(lookup_file):
    """Reads and returns a lookup with property values for SDGs.
    
    Returns:
        A dict with integer keys and values of the corresponding lookup.
    """
    with open(LOOKUP_DIR / lookup_file, "rt") as f:
       lookup  = json.load(f)
    return {int(k): v for k, v in lookup.items()}
