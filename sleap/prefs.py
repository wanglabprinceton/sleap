"""
Handles SLEAP preferences.

Importing this module creates `prefs`, instance of `Preferences` class.
"""

from sleap import util
import yaml # !!!
from yaml.representer import RepresenterError # !!!

class Preferences(object):
    """Class for accessing SLEAP preferences."""

    _prefs = None
    _defaults = {
        "medium step size": 10,
        "large step size": 100,
        "color predicted": False,
        "propagate track labels": True,
        "palette": "standard",
        "bold lines": False,
        "trail length": 0,
        "trail shade": "Normal",
        "trail width": 4.0,
        "trail node count": 1,
        "marker size": 4,
        "edge style": "Line",
        "window state": b"",
        "node label size": 12,
        "show non-visible nodes": True,
        "share usage data": True,
        "node marker sizes": (1, 2, 3, 4, 6, 8, 12),
        "node label sizes": (6, 9, 12, 18, 24, 36),
    }
    _filename = "preferences.yaml"

    def __init__(self):
        self.load()

    def load(self):
        """Load preferences from file, if not already loaded."""
        if self._prefs is None:
            self.load_()

    def load_(self):
        """Load preferences from file (regardless of whether loaded already)."""
        try:
            self._prefs = util.get_config_yaml(self._filename)
        except FileNotFoundError:
            pass

        self._prefs = self._prefs or {}

        for k, v in self._defaults.items():
            if k not in self._prefs:
                self._prefs[k] = v

    def save(self):
        # """Save preferences to file."""
        # util.save_config_yaml(self._filename, self._prefs) # !!! Commented out from original code -- see below
        """Save preferences to file, avoiding unserializable Python objects."""
        # Remove Qt window state before saving since it may serialize as a non-importable object
        # (e.g., `!!python/object/apply:None._unpickle_type`) which causes PyYAML to crash on load.
        def sanitize(obj):
            if isinstance(obj, dict):
                new_dict = {}
                for k, v in obj.items():
                    # Skip PyQt5 GUI state
                    if k == "window state":
                        continue
                    new_dict[k] = sanitize(v)
                return new_dict
            elif isinstance(obj, list):
                return [sanitize(v) for v in obj]
            else:
                try:
                    yaml.dump(obj)
                    return obj
                except (RepresenterError, TypeError, AttributeError):
                    return None
        try:
            cleaned_prefs = sanitize(self._prefs)
            util.save_config_yaml(self._filename, cleaned_prefs)
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def reset_to_default(self):
        """Reset preferences to default."""
        util.save_config_yaml(self._filename, self._defaults)
        self.load()

    def _validate_key(self, key):
        if key not in self._defaults:
            raise KeyError(f"No preference matching '{key}'")

    def __contains__(self, item) -> bool:
        return item in self._defaults

    def __getitem__(self, key):
        self.load()
        self._validate_key(key)
        return self._prefs.get(key, self._defaults[key])

    def __setitem__(self, key, value):
        self.load()
        self._validate_key(key)
        self._prefs[key] = value


prefs = Preferences()

# save preference so that user editable file is created if it doesn't exist
prefs.save()