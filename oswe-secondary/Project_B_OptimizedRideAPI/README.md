Project B - Optimized Ride API

Enhanced endpoint supports includeFareBreakdown=true to return a full fare breakdown in a single call.
Features:
- Single-call breakdown support preserving backward compatibility when flag is absent.
- Internal caching (configurable) to reduce repeated downstream fetches.
- Strict validation & sanitization for fare items (type, label, amount) and nested structures.

Run tests: `./run_tests.sh` (or `python tests/runner.py`). Results written to `results/results_post.json` and `logs/log_post.txt`.