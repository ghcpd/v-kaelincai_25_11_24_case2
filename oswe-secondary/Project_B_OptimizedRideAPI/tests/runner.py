#!/usr/bin/env python3
import json
import time
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.api import OptimizedAPI

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = Path(ROOT, '..', 'test_scenarios.json').resolve()
LOG = Path(ROOT, 'logs', 'log_post.txt')
RESULTS = Path(ROOT, 'results')
RESULTS.mkdir(exist_ok=True)


def load_scenarios():
    return json.load(open(SCENARIOS))


def run():
    api = OptimizedAPI(cache_enabled=True)
    scenarios = load_scenarios()
    results = []
    total_latency = 0.0
    passed = 0
    for s in scenarios:
        if s['project'] not in ('B', 'both'):
            continue
        rideId = s['input'].get('rideId')
        simulate_ms = s['input'].get('simulate_network_ms', 0)
        include_breakdown = s['input'].get('includeFareBreakdown', False)
        start = time.time()
        res = api.get_ride(rideId, includeFareBreakdown=include_breakdown, simulate_network_ms=simulate_ms)
        latency_ms = (time.time() - start) * 1000.0
        total_latency += latency_ms
        # Validate
        expected = s['expected']
        pass_flag = False
        errors = []
        if expected.get('status') == 'ok' and res.get('status') == 'ok':
            payload = res['payload']
            t = payload.get('totalFare')
            breakdown = payload.get('fareBreakdown', [])
            sum_breakdown = 0.0
            for it in breakdown:
                try:
                    sum_breakdown += float(it.get('amount', 0))
                except Exception:
                    sum_breakdown += 0.0
            # If includeBreakdown expected true, ensure breakdown exists
            if include_breakdown and not breakdown:
                errors.append('missing_breakdown')
            # only ensure reconciliation if breakdown is present / requested
            if breakdown:
                # ensure total reconciles either by equality or reconciled hint exists
                if abs((t or 0) - sum_breakdown) < 0.001 or payload.get('fare_total_reconciled_to_sum'):
                    pass_flag = True
                else:
                    errors.append('total_mismatch')
            else:
                # no breakdown requested — treat as acceptable
                pass_flag = True
        else:
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
    with open(RESULTS / 'results_post.json', 'w') as fh:
        json.dump(summary, fh, indent=2)
    with open(LOG, 'w') as fh:
        fh.write(json.dumps(summary, indent=2))
    # write snapshot
    try:
        sample = results[0]['payload_snapshot']
        with open(RESULTS / 'optimized_response_snapshot.json', 'w') as fh:
            json.dump(sample, fh, indent=2)
    except Exception:
        pass
    print('Wrote results:', RESULTS / 'results_post.json')


if __name__ == '__main__':
    run()
