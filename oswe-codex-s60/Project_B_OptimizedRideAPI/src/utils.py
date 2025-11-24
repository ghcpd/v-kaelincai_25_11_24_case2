from typing import Any, Dict, List


def flatten_breakdown(raw: Any) -> List[Dict[str, Any]]:
    """Flatten nested breakdown arrays into a flat list of dicts.

    Ignores non-dict, non-list items.
    """
    flat: List[Dict[str, Any]] = []

    def _recurse(item: Any):
        if item is None:
            return
        if isinstance(item, dict):
            flat.append(item)
        elif isinstance(item, (list, tuple)):
            for sub in item:
                _recurse(sub)
        # ignore other types

    _recurse(raw)
    return flat
