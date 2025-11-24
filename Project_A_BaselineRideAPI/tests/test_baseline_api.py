"""
Test Suite for Project A: Baseline Ride Fare API
Tests the legacy multi-endpoint approach
"""
import json
import os
import sys
import time
import logging
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from baseline_api import BaselineRideAPI, load_test_data


class BaselineRideAPITests:
    """Test suite for Baseline Ride API"""

    def __init__(self, test_scenarios_path: str, results_path: str, logs_path: str):
        self.test_scenarios_path = test_scenarios_path
        self.results_path = results_path
        self.logs_path = logs_path
        self.test_results: List[Dict[str, Any]] = []
        self.summary: Dict[str, Any] = {}

    def load_test_data(self) -> Dict[str, Any]:
        """Load test scenarios and test data"""
        with open(self.test_scenarios_path, 'r') as f:
            return json.load(f)

    def run_test_scenario(self, api: BaselineRideAPI, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test scenario.
        
        Args:
            api: The BaselineRideAPI instance
            scenario: The test scenario configuration
            
        Returns:
            Test result with metrics
        """
        scenario_id = scenario["scenario_id"]
        ride_id = scenario["ride_id"]
        expected_output = scenario.get("expected_output", {})
        edge_case_flags = scenario.get("edge_case_flags", [])

        logger.info(f"\n{'='*60}")
        logger.info(f"Running scenario: {scenario_id}")
        logger.info(f"Description: {scenario['description']}")
        logger.info(f"Ride ID: {ride_id}")
        logger.info(f"Edge cases: {edge_case_flags if edge_case_flags else 'None'}")

        api.reset_metrics()
        test_start = time.time()

        try:
            # Baseline test: Don't include breakdown
            response = api.get_ride(ride_id)
            
            expected_status = expected_output.get("status", 200)
            if response.get("status") != expected_status:
                logger.warning(f"Status mismatch: expected {expected_status}, got {response.get('status')}")
                if expected_status != 200:
                    # This is an expected error response
                    if response.get("error_code") == expected_output.get("error_code"):
                        logger.info(f"Status: PASSED (expected error {expected_status})")
                        metrics = api.get_metrics()
                        test_duration_ms = (time.time() - test_start) * 1000
                        return {
                            "scenario_id": scenario_id,
                            "status": "PASSED",
                            "passed": True,
                            "errors": [],
                            "response": response,
                            "metrics": metrics,
                            "test_duration_ms": test_duration_ms,
                            "edge_case_flags": edge_case_flags
                        }
                    else:
                        return {
                            "scenario_id": scenario_id,
                            "status": "FAILED",
                            "passed": False,
                            "error": f"Expected error code {expected_output.get('error_code')}, got {response.get('error_code')}",
                            "test_duration_ms": (time.time() - test_start) * 1000
                        }
                else:
                    return {
                        "scenario_id": scenario_id,
                        "status": "FAILED",
                        "error": f"Status {expected_status} expected but got {response.get('status')}",
                        "passed": False,
                        "test_duration_ms": (time.time() - test_start) * 1000
                    }

            # Validate response
            passed = True
            errors = []

            # Check schema
            if expected_output.get("schema_contains_breakdown") == False:
                if "fareBreakdown" in response:
                    errors.append("Response should not contain fareBreakdown in baseline mode")
                    passed = False

            # Check required fields
            required_fields = expected_output.get("expected_fields", [])
            for field in required_fields:
                if field not in response:
                    errors.append(f"Missing required field: {field}")
                    passed = False

            # Check totalFare value
            if "expected_fare_total" in expected_output:
                if response.get("totalFare") != expected_output["expected_fare_total"]:
                    errors.append(f"Fare mismatch: expected {expected_output['expected_fare_total']}, got {response.get('totalFare')}")
                    passed = False

            metrics = api.get_metrics()
            test_duration_ms = (time.time() - test_start) * 1000

            logger.info(f"Status: {'PASSED' if passed else 'FAILED'}")
            logger.info(f"Backend calls: {metrics['backend_calls']}")
            logger.info(f"Total latency: {metrics['total_latency_ms']} ms")
            if errors:
                logger.warning(f"Errors: {errors}")

            return {
                "scenario_id": scenario_id,
                "status": "PASSED" if passed else "FAILED",
                "passed": passed,
                "errors": errors,
                "response": response,
                "metrics": metrics,
                "test_duration_ms": test_duration_ms,
                "edge_case_flags": edge_case_flags
            }

        except Exception as e:
            logger.error(f"Exception in scenario {scenario_id}: {str(e)}")
            return {
                "scenario_id": scenario_id,
                "status": "ERROR",
                "passed": False,
                "error": str(e),
                "test_duration_ms": (time.time() - test_start) * 1000
            }

    def run_all_tests(self) -> None:
        """Run all test scenarios"""
        logger.info("="*60)
        logger.info("PROJECT A: BASELINE RIDE FARE API - TEST EXECUTION")
        logger.info("="*60)

        # Load data
        test_data = self.load_test_data()
        data_store = load_test_data(self.test_scenarios_path)

        # Initialize API
        api = BaselineRideAPI(data_store=data_store, network_latency_ms=50)

        # Run tests
        scenarios = test_data.get("test_scenarios", [])
        baseline_scenarios = [s for s in scenarios if "baseline" in s["scenario_id"] or "malformed" in s["scenario_id"]]

        for scenario in baseline_scenarios:
            result = self.run_test_scenario(api, scenario)
            self.test_results.append(result)

        # Calculate summary
        passed = sum(1 for r in self.test_results if r.get("passed", False))
        failed = sum(1 for r in self.test_results if not r.get("passed", False))
        total_latency = sum(r.get("metrics", {}).get("total_latency_ms", 0) for r in self.test_results)
        total_backend_calls = sum(r.get("metrics", {}).get("backend_calls", 0) for r in self.test_results)

        self.summary = {
            "total_scenarios": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/len(self.test_results)*100):.1f}%" if self.test_results else "0%",
            "total_latency_ms": total_latency,
            "total_backend_calls": total_backend_calls,
            "avg_latency_per_scenario_ms": total_latency / len(self.test_results) if self.test_results else 0,
            "edge_case_coverage": self._calculate_edge_case_coverage()
        }

        self._save_results()
        self._print_summary()

    def _calculate_edge_case_coverage(self) -> Dict[str, int]:
        """Calculate edge case coverage"""
        coverage = {}
        for result in self.test_results:
            for flag in result.get("edge_case_flags", []):
                coverage[flag] = coverage.get(flag, 0) + (1 if result.get("passed") else 0)
        return coverage

    def _save_results(self) -> None:
        """Save results to JSON file"""
        os.makedirs(self.results_path, exist_ok=True)
        results_file = os.path.join(self.results_path, "results_pre.json")
        
        output = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": self.summary,
            "test_results": self.test_results
        }

        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"\nResults saved to {results_file}")

    def _print_summary(self) -> None:
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY - PROJECT A (BASELINE)")
        logger.info("="*60)
        logger.info(f"Total Scenarios: {self.summary['total_scenarios']}")
        logger.info(f"Passed: {self.summary['passed']}")
        logger.info(f"Failed: {self.summary['failed']}")
        logger.info(f"Pass Rate: {self.summary['pass_rate']}")
        logger.info(f"Total Backend Calls: {self.summary['total_backend_calls']}")
        logger.info(f"Total Latency: {self.summary['total_latency_ms']:.0f} ms")
        logger.info(f"Avg Latency/Scenario: {self.summary['avg_latency_per_scenario_ms']:.2f} ms")
        logger.info(f"Edge Case Coverage: {self.summary['edge_case_coverage']}")
        logger.info("="*60)


def main():
    """Main test execution"""
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(project_dir)
    
    test_scenarios_path = os.path.join(root_dir, "test_scenarios.json")
    results_path = os.path.join(project_dir, "results")
    logs_path = os.path.join(project_dir, "logs")

    # Run tests
    test_suite = BaselineRideAPITests(test_scenarios_path, results_path, logs_path)
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
