#!/usr/bin/env python3
import json
import time
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.api import BaselineAPI

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = Path(ROOT, '..', 'test_scenarios.json').resolve()
LOG = Path(ROOT, 'logs', 'log_pre.txt')
RESULTS = Path(ROOT, 'results')
RESULTS.mkdir(exist_ok=True)


def load_scenarios():
    return json.load(open(SCENARIOS))


def run():
    api = BaselineAPI()
    scenarios = load_scenarios()
    results = []
    total_latency = 0.0
    passed = 0
    for s in scenarios:
        if s['project'] not in ('A', 'both'):
            continue
        rideId = s['input'].get('rideId')
        simulate_ms = s['input'].get('simulate_network_ms', 0)
        start = time.time()
        res = api.fetch_ride_with_legacy_flow(rideId, simulate_network_ms=simulate_ms)
        latency_ms = (time.time() - start) * 1000.0
        total_latency += latency_ms
        # Validate
        expected = s['expected']
        pass_flag = False
        errors = []
        if expected.get('status') == 'ok' and res.get('status') == 'ok':
            payload = res['payload']
            # check totalFare vs breakdown sum
            t = payload.get('totalFare')
            breakdown = payload.get('fareBreakdown', [])
            sum_breakdown = 0.0
            for it in breakdown:
                try:
                    sum_breakdown += float(it.get('amount', 0))
                except Exception:
                    sum_breakdown += 0.0
            if abs((t or 0) - sum_breakdown) < 0.001:
                pass_flag = True
            else:
                errors.append('total_mismatch')
        else:
            # expect an error
            if expected.get('status') == 'error' and res.get('status') == 'error':
                pass_flag = True
            else:
                errors.append('unexpected_status')

        if pass_flag:
            passed += 1

        results.append({
            'id': s['id'],
            'status': res.get('status'),
            'latency_ms': latency_ms,
            'metrics': res.get('metrics'),
            'pass': pass_flag,
            'errors': errors,
            'payload_snapshot': res.get('payload')
        })

    avg_latency = total_latency / max(1, len(results))
    summary = {
        'total_cases': len(results),
        'pass_count': passed,
        'average_latency_ms': avg_latency,
        'results': results
    }
    with open(RESULTS / 'results_pre.json', 'w') as fh:
        json.dump(summary, fh, indent=2)
    with open(LOG, 'w') as fh:
        fh.write(json.dumps(summary, indent=2))
    # print sample snapshot
    try:
        sample = results[0]['payload_snapshot']
        with open(RESULTS / 'baseline_response_snapshot.json', 'w') as fh:
            json.dump(sample, fh, indent=2)
    except Exception:
        pass
    print('Wrote results:', RESULTS / 'results_pre.json')


if __name__ == '__main__':
    run()
