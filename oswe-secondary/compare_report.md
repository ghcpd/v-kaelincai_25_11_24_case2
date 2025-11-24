# Compare Report - Baseline vs Optimized

## Summary Metrics
* Baseline avg latency: **350.2 ms***
* Optimized avg latency: **175.2 ms***
* Latency reduction (pre - post): **175.0 ms***

### Pass / Fail
- Baseline passed: 4 / 4
- Optimized passed: 4 / 4

## Per-scenario analysis
|scenario|baseline latency(ms)|optimized latency(ms)|baseline calls|optimized calls|baseline pass|optimized pass|notes|
|---|---:|---:|---:|---:|---|---|---|
|baseline_normal|0.019311904907226562|-|2|-|True|-||
|hidden_vulnerability_attempt|0.01430511474609375|0.029325485229492188|2|1|True|True|requests_saved=1|
|malformed_input|0.026226043701171875|0.0095367431640625|0|0|True|True|requests_saved=0|
|optimized_normal|-|0.042438507080078125|-|1|-|True||
|weak_network_stress|1400.669813156128|700.5414962768555|2|1|True|True|requests_saved=1|

## Edge-case/resilience notes
- hidden_vulnerability_attempt: baseline -> {'id': 'hidden_vulnerability_attempt', 'status': 'ok', 'latency_ms': 0.01430511474609375, 'metrics': {'calls': 2}, 'pass': True, 'errors': [], 'payload_snapshot': {'rideId': 'ride_malicious', 'totalFare': 15.0, 'fareBreakdown_requested_separately': True, 'fareBreakdown': [{'type': 'base', 'label': "<script>alert('x')</script>", 'amount': 10.0}, {'type': 'bonus', 'label': ['Nested', ['Array']], 'amount': '5.0'}]}}
  optimized -> {'id': 'hidden_vulnerability_attempt', 'status': 'ok', 'latency_ms': 0.029325485229492188, 'metrics': {'data_access_calls': 1}, 'pass': True, 'errors': [], 'payload_snapshot': {'rideId': 'ride_malicious', 'totalFare': 15.0, 'fareBreakdown': [{'type': 'base', 'label': '&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;', 'amount': 10.0}, {'type': 'bonus', 'label': 'Nested Array', 'amount': 5.0}], 'validation_errors': []}}
- malformed_input: baseline -> {'id': 'malformed_input', 'status': 'error', 'latency_ms': 0.026226043701171875, 'metrics': {'calls': 0}, 'pass': True, 'errors': [], 'payload_snapshot': None}
  optimized -> {'id': 'malformed_input', 'status': 'error', 'latency_ms': 0.0095367431640625, 'metrics': {'data_access_calls': 0}, 'pass': True, 'errors': [], 'payload_snapshot': None}
