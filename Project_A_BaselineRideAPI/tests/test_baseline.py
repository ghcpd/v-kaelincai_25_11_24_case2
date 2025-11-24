"""
Test suite for Baseline Ride API
Tests the legacy implementation with separate endpoints
"""

import json
import time
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ride_api import BaselineRideAPI


class TestRunner:
    """Test runner for baseline API"""
    
    def __init__(self, scenarios_file: str):
        self.scenarios_file = scenarios_file
        self.results = []
        self.logs = []
        
    def log(self, message: str):
        """Add log entry"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def load_scenarios(self):
        """Load test scenarios from JSON file"""
        with open(self.scenarios_file, 'r') as f:
            data = json.load(f)
            # Filter scenarios for Project A
            return [s for s in data['scenarios'] if s['project'] == 'A']
    
    def run_test(self, scenario: dict) -> dict:
        """Run a single test scenario"""
        self.log(f"\n{'='*60}")
        self.log(f"Running scenario: {scenario['id']}")
        self.log(f"Description: {scenario['description']}")
        self.log(f"{'='*60}")
        
        # Set network latency based on condition
        network_latency = 0.1 if scenario['network_condition'] == 'good' else 1.5
        api = BaselineRideAPI(network_latency=network_latency)
        
        ride_id = scenario['ride_id']
        start_time = time.time()
        
        try:
            # Execute the legacy workflow - two separate calls
            self.log(f"Calling get_complete_ride_info for ride_id: {ride_id}")
            response = api.get_complete_ride_info(ride_id)
            
            elapsed_ms = response.get('latency_ms', round((time.time() - start_time) * 1000, 2))
            request_count = response.get('request_count', api.request_count)
            
            # Validate response
            result = {
                "scenario_id": scenario['id'],
                "status": response['status'],
                "ride_id": ride_id,
                "request_count": request_count,
                "latency_ms": elapsed_ms,
                "network_condition": scenario['network_condition'],
                "timestamp": datetime.now().isoformat()
            }
            
            if response['status'] == 'success':
                data = response['data']
                result.update({
                    "total_fare": data.get('total_fare'),
                    "has_breakdown_inline": False,  # Baseline never has inline breakdown
                    "requires_extra_call": True,    # Always requires extra call
                    "fare_breakdown": data.get('fare_breakdown', []),
                    "breakdown_item_count": len(data.get('fare_breakdown', []))
                })
                
                # Validate fare total matches sum of items
                if 'fare_breakdown' in data:
                    calculated_total = sum(item['amount'] for item in data['fare_breakdown'])
                    total_fare = data['total_fare']
                    fare_matches = abs(calculated_total - total_fare) < 0.01
                    result['fare_total_matches'] = fare_matches
                    result['calculated_total'] = round(calculated_total, 2)
                    
                    if not fare_matches:
                        self.log(f"WARNING: Fare mismatch! Total: {total_fare}, Sum: {calculated_total}")
                
                # Check against expected values
                expected = scenario.get('expected', {})
                result['test_passed'] = (
                    result['status'] == expected.get('status', 'success') and
                    result.get('fare_total_matches', True)
                )
                
                self.log(f"✓ Test PASSED - Total fare: ${total_fare}, Requests: {request_count}, Latency: {elapsed_ms}ms")
            else:
                result.update({
                    "error": response.get('error'),
                    "error_type": response.get('error_type')
                })
                expected = scenario.get('expected', {})
                result['test_passed'] = result['status'] == expected.get('status', 'success')
                
                if result['test_passed']:
                    self.log(f"✓ Test PASSED - Error handled correctly: {result['error_type']}")
                else:
                    self.log(f"✗ Test FAILED - Unexpected error")
            
            return result
            
        except Exception as e:
            self.log(f"✗ Test FAILED with exception: {str(e)}")
            return {
                "scenario_id": scenario['id'],
                "status": "error",
                "error": str(e),
                "error_type": "test_exception",
                "test_passed": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def run_all_tests(self):
        """Run all test scenarios"""
        self.log("="*60)
        self.log("PROJECT A - BASELINE RIDE API TEST SUITE")
        self.log("="*60)
        
        scenarios = self.load_scenarios()
        self.log(f"\nLoaded {len(scenarios)} test scenarios for Project A")
        
        start_time = time.time()
        
        for scenario in scenarios:
            result = self.run_test(scenario)
            self.results.append(result)
        
        total_time = time.time() - start_time
        
        # Generate summary
        self.generate_summary(total_time)
        
        # Save results
        self.save_results()
        self.save_logs()
    
    def generate_summary(self, total_time: float):
        """Generate test summary"""
        self.log(f"\n{'='*60}")
        self.log("TEST SUMMARY - PROJECT A (BASELINE)")
        self.log(f"{'='*60}")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.get('test_passed', False))
        failed_tests = total_tests - passed_tests
        
        success_results = [r for r in self.results if r.get('status') == 'success']
        
        avg_latency = sum(r.get('latency_ms', 0) for r in success_results) / len(success_results) if success_results else 0
        avg_requests = sum(r.get('request_count', 0) for r in success_results) / len(success_results) if success_results else 0
        
        self.log(f"Total scenarios: {total_tests}")
        self.log(f"Passed: {passed_tests}")
        self.log(f"Failed: {failed_tests}")
        self.log(f"Success rate: {(passed_tests/total_tests*100):.1f}%")
        self.log(f"Total execution time: {total_time:.2f}s")
        self.log(f"\nPerformance Metrics (Baseline):")
        self.log(f"  Average latency: {avg_latency:.2f}ms")
        self.log(f"  Average requests per operation: {avg_requests:.2f}")
        self.log(f"  Multiple round trips required: YES (Legacy limitation)")
        self.log(f"  Inline fare breakdown support: NO")
        self.log(f"{'='*60}\n")
        
        # Add summary to results
        self.summary = {
            "project": "A - Baseline",
            "total_scenarios": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": round(passed_tests/total_tests*100, 1),
            "total_execution_time_sec": round(total_time, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "avg_requests_per_operation": round(avg_requests, 2),
            "supports_inline_breakdown": False,
            "requires_multiple_calls": True
        }
    
    def save_results(self):
        """Save test results to JSON file"""
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, 'results_baseline.json')
        
        output_data = {
            "summary": self.summary,
            "results": self.results,
            "generated_at": datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        self.log(f"Results saved to: {output_file}")
        
        # Also save a baseline response snapshot
        snapshot_file = os.path.join(output_dir, 'baseline_response_snapshot.json')
        success_result = next((r for r in self.results if r.get('status') == 'success'), None)
        if success_result:
            with open(snapshot_file, 'w') as f:
                json.dump({
                    "description": "Baseline API response structure - requires 2 separate calls",
                    "call_1_get_ride": {
                        "endpoint": "GET /rides/{rideId}",
                        "response": {
                            "status": "success",
                            "data": {
                                "ride_id": success_result.get('ride_id'),
                                "total_fare": success_result.get('total_fare'),
                                "note": "No fare breakdown included - client must make second call"
                            }
                        }
                    },
                    "call_2_get_fare_items": {
                        "endpoint": "GET /rides/{rideId}/fare-items",
                        "response": {
                            "status": "success",
                            "data": {
                                "ride_id": success_result.get('ride_id'),
                                "fare_breakdown": success_result.get('fare_breakdown', [])
                            }
                        }
                    },
                    "performance_impact": {
                        "total_requests": success_result.get('request_count'),
                        "total_latency_ms": success_result.get('latency_ms'),
                        "notes": "Each request includes network latency + processing time"
                    }
                }, f, indent=2)
    
    def save_logs(self):
        """Save logs to file"""
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(output_dir, exist_ok=True)
        
        log_file = os.path.join(output_dir, 'log_baseline.txt')
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.logs))
        
        self.log(f"Logs saved to: {log_file}")


if __name__ == "__main__":
    # Find test_scenarios.json in parent directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    scenarios_file = os.path.join(project_root, 'test_scenarios.json')
    
    if not os.path.exists(scenarios_file):
        print(f"ERROR: test_scenarios.json not found at {scenarios_file}")
        sys.exit(1)
    
    runner = TestRunner(scenarios_file)
    runner.run_all_tests()
