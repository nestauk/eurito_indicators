import json
<<<<<<< HEAD
import os
=======
>>>>>>> 6c8262a397be18ae12876ff7b4f70c3f50f5ad2f

from eurito_indicators import PROJECT_DIR


LOOKUP_DIR = f'{PROJECT_DIR}/inputs/sdg/official'


def stringify_sdg_number(sdg):
    """Converts integer to string and zero pads to 2 digits. Used for saving 
    and loading individual goal data.
    
    Args:
        sdg (int): Typically 1 - 17

    Returns:
        (str): e.g. '06'
    """
    return str(sdg).zfill(2)


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
