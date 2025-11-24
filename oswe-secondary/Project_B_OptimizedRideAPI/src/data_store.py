"""
Data store for Project B (shared dataset similar to baseline). This file will be minimal — main logic in api.py.
"""
_DATA = {
    'ride_1001': {
        'totalFare': 30.0,
        'fare_items': [
            {'type': 'base', 'label': 'Base fare', 'amount': 20.0},
            {'type': 'service', 'label': 'Service charge', 'amount': 5.0},
            {'type': 'tip', 'label': 'Tip', 'amount': 5.0},
        ]
    },
    'ride_weak1': {
        'totalFare': 40.0,
        'fare_items': [
            {'type': 'base', 'label': 'Base fare', 'amount': 30.0},
            {'type': 'surcharge', 'label': 'Airport', 'amount': 10.0},
        ]
    },
    'ride_malicious': {
        'totalFare': 15.0,
        'fare_items': [
            {'type': 'base', 'label': "<script>alert('x')</script>", 'amount': 10.0},
            {'type': 'bonus', 'label': ['Nested', ['Array']], 'amount': '5.0'}
        ]
    }
}


def get_raw_ride(ride_id):
    return _DATA.get(ride_id)


def list_fare_items(ride_id):
    r = _DATA.get(ride_id)
    if not r:
        return None
    return r.get('fare_items', [])
