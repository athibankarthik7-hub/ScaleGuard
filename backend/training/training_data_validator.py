#!/usr/bin/env python3
"""
Training Data Validator for ScaleGuard AI Model
Validates generated training data for quality and consistency
"""

import json
import re
from typing import Dict, List, Any
from dataclasses import dataclass
from statistics import mean, median

@dataclass
class ValidationResult:
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]

class TrainingDataValidator:
    
    def __init__(self):
        self.required_fields = {
            "input_data": ["system_state", "bottlenecks", "cascading_failures"],
            "system_state": ["risk_score", "total_services", "critical_count", "time_context"],
            "bottleneck": ["name", "type", "cpu_usage", "memory_usage", "risk_score", "reason"]
        }
        
        self.valid_service_types = ["database", "api", "cache", "queue", "external", "compute"]
        self.valid_severities = ["low", "medium", "high", "critical"]
        self.valid_time_contexts = ["peak_hours", "maintenance", "normal"]
    
    def validate_example(self, example: Dict[str, Any]) -> ValidationResult:
        """Validate a single training example"""
        issues = []
        warnings = []
        metrics = {}
        
        # Check top-level structure
        if not all(field in example for field in ["input_data", "expected_analysis", "expected_recommendations"]):
            issues.append("Missing required top-level fields")
            return ValidationResult(False, issues, warnings, metrics)
        
        input_data = example["input_data"]
        expected_analysis = example["expected_analysis"]
        expected_recommendations = example["expected_recommendations"]
        
        # Validate input data structure
        issues.extend(self._validate_input_data(input_data))
        
        # Validate analysis quality
        analysis_issues, analysis_metrics = self._validate_analysis(expected_analysis)
        issues.extend(analysis_issues)
        metrics.update(analysis_metrics)
        
        # Validate recommendations
        rec_issues, rec_metrics = self._validate_recommendations(expected_recommendations)
        issues.extend(rec_issues)
        metrics.update(rec_metrics)
        
        # Check consistency between input and output
        consistency_issues = self._check_consistency(input_data, expected_analysis, expected_recommendations)
        issues.extend(consistency_issues)
        
        return ValidationResult(len(issues) == 0, issues, warnings, metrics)
    
    def _validate_input_data(self, input_data: Dict[str, Any]) -> List[str]:
        """Validate input data structure and values"""
        issues = []
        
        # Check required fields
        for field in self.required_fields["input_data"]:
            if field not in input_data:
                issues.append(f"Missing input field: {field}")
        
        if "system_state" in input_data:
            system_state = input_data["system_state"]
            
            # Validate system state fields
            for field in self.required_fields["system_state"]:
                if field not in system_state:
                    issues.append(f"Missing system_state field: {field}")
            
            # Validate risk score range
            if "risk_score" in system_state:
                risk_score = system_state["risk_score"]
                if not (0 <= risk_score <= 100):
                    issues.append(f"Risk score out of range: {risk_score} (should be 0-100)")
            
            # Validate time context
            if "time_context" in system_state:
                time_context = system_state["time_context"]
                if time_context not in self.valid_time_contexts:
                    issues.append(f"Invalid time context: {time_context}")
        
        if "bottlenecks" in input_data:
            bottlenecks = input_data["bottlenecks"]
            
            if not isinstance(bottlenecks, list) or len(bottlenecks) == 0:
                issues.append("Bottlenecks should be a non-empty list")
            else:
                for i, bottleneck in enumerate(bottlenecks):
                    # Validate bottleneck fields
                    for field in self.required_fields["bottleneck"]:
                        if field not in bottleneck:
                            issues.append(f"Bottleneck {i} missing field: {field}")
                    
                    # Validate service type
                    if "type" in bottleneck and bottleneck["type"] not in self.valid_service_types:
                        issues.append(f"Invalid service type in bottleneck {i}: {bottleneck['type']}")
                    
                    # Validate usage percentages
                    for usage_field in ["cpu_usage", "memory_usage"]:
                        if usage_field in bottleneck:
                            usage = bottleneck[usage_field]
                            if not (0 <= usage <= 100):
                                issues.append(f"Bottleneck {i} {usage_field} out of range: {usage}")
                    
                    # Validate risk score
                    if "risk_score" in bottleneck:
                        risk_score = bottleneck["risk_score"]
                        if not (0 <= risk_score <= 100):
                            issues.append(f"Bottleneck {i} risk score out of range: {risk_score}")
        
        return issues
    
    def _validate_analysis(self, analysis: str) -> tuple[List[str], Dict[str, Any]]:
        """Validate analysis text quality"""
        issues = []
        metrics = {}
        
        if not isinstance(analysis, str) or len(analysis.strip()) == 0:
            issues.append("Analysis is empty or not a string")
            return issues, metrics
        
        # Check minimum length
        if len(analysis) < 200:
            issues.append("Analysis too short (should be at least 200 characters)")
        
        # Check for required sections
        required_sections = ["Root Cause", "Business Impact", "Actions"]
        for section in required_sections:
            if section not in analysis:
                issues.append(f"Analysis missing section: {section}")
        
        # Check for technical depth
        technical_terms = ["CPU", "memory", "database", "API", "cache", "scale", "optimization"]
        found_terms = sum(1 for term in technical_terms if term.lower() in analysis.lower())
        if found_terms < 3:
            issues.append("Analysis lacks technical depth (few technical terms found)")
        
        # Calculate metrics
        metrics["analysis_length"] = len(analysis)
        metrics["analysis_sections"] = len([s for s in required_sections if s in analysis])
        metrics["technical_terms_count"] = found_terms
        
        return issues, metrics
    
    def _validate_recommendations(self, recommendations: List[str]) -> tuple[List[str], Dict[str, Any]]:
        """Validate recommendations quality"""
        issues = []
        metrics = {}
        
        if not isinstance(recommendations, list):
            issues.append("Recommendations should be a list")
            return issues, metrics
        
        if len(recommendations) != 6:
            issues.append(f"Should have exactly 6 recommendations, found {len(recommendations)}")
        
        # Validate each recommendation
        action_words = ["scale", "implement", "optimize", "deploy", "add", "set up", "review", "enable"]
        actionable_count = 0
        
        for i, rec in enumerate(recommendations):
            if not isinstance(rec, str) or len(rec.strip()) == 0:
                issues.append(f"Recommendation {i+1} is empty or not a string")
                continue
            
            # Check minimum length
            if len(rec) < 20:
                issues.append(f"Recommendation {i+1} too short")
            
            # Check for actionable language
            if any(word in rec.lower() for word in action_words):
                actionable_count += 1
            else:
                issues.append(f"Recommendation {i+1} not actionable (missing action words)")
        
        # Calculate metrics
        metrics["recommendations_count"] = len(recommendations)
        metrics["actionable_recommendations"] = actionable_count
        metrics["avg_recommendation_length"] = mean([len(r) for r in recommendations]) if recommendations else 0
        
        return issues, metrics
    
    def _check_consistency(self, input_data: Dict[str, Any], analysis: str, 
                          recommendations: List[str]) -> List[str]:
        """Check consistency between input and expected outputs"""
        issues = []
        
        # Check if primary bottleneck is mentioned in analysis
        if "bottlenecks" in input_data and input_data["bottlenecks"]:
            primary_bottleneck = input_data["bottlenecks"][0]
            bottleneck_name = primary_bottleneck.get("name", "")
            bottleneck_type = primary_bottleneck.get("type", "")
            
            if bottleneck_name and bottleneck_name not in analysis:
                issues.append("Primary bottleneck name not mentioned in analysis")
            
            if bottleneck_type and bottleneck_type not in analysis.lower():
                issues.append("Primary bottleneck type not mentioned in analysis")
        
        # Check if risk level in analysis matches input risk score
        if "system_state" in input_data and "risk_score" in input_data["system_state"]:
            risk_score = input_data["system_state"]["risk_score"]
            expected_level = ""
            
            if risk_score >= 90:
                expected_level = "CRITICAL"
            elif risk_score >= 75:
                expected_level = "HIGH"
            elif risk_score >= 50:
                expected_level = "MEDIUM"
            else:
                expected_level = "LOW"
            
            if expected_level not in analysis.upper():
                issues.append(f"Analysis doesn't reflect risk level (expected {expected_level} for score {risk_score})")
        
        # Check if recommendations address the primary bottleneck type
        if "bottlenecks" in input_data and input_data["bottlenecks"]:
            bottleneck_type = input_data["bottlenecks"][0].get("type", "")
            recommendations_text = " ".join(recommendations).lower()
            
            expected_terms = {
                "database": ["database", "db", "query", "replica", "index"],
                "api": ["api", "scale", "instance", "load balancer"],
                "cache": ["cache", "redis", "memory", "eviction"],
                "queue": ["queue", "message", "consumer", "throughput"]
            }
            
            if bottleneck_type in expected_terms:
                terms = expected_terms[bottleneck_type]
                if not any(term in recommendations_text for term in terms):
                    issues.append(f"Recommendations don't address {bottleneck_type} bottleneck properly")
        
        return issues
    
    def validate_dataset(self, dataset_file: str) -> Dict[str, Any]:
        """Validate an entire training dataset"""
        with open(dataset_file, 'r') as f:
            dataset = json.load(f)
        
        if "examples" not in dataset:
            return {"valid": False, "error": "Dataset missing 'examples' field"}
        
        examples = dataset["examples"]
        total_examples = len(examples)
        valid_examples = 0
        all_issues = []
        all_metrics = []
        
        print(f"Validating {total_examples} examples...")
        
        for i, example in enumerate(examples):
            result = self.validate_example(example)
            
            if result.is_valid:
                valid_examples += 1
            else:
                example_issues = [f"Example {i+1}: {issue}" for issue in result.issues]
                all_issues.extend(example_issues)
            
            all_metrics.append(result.metrics)
            
            if (i + 1) % 100 == 0:
                print(f"Validated {i + 1}/{total_examples} examples...")
        
        # Calculate aggregate metrics
        overall_metrics = {}
        if all_metrics:
            overall_metrics = {
                "avg_analysis_length": mean([m.get("analysis_length", 0) for m in all_metrics]),
                "avg_recommendations_count": mean([m.get("recommendations_count", 0) for m in all_metrics]),
                "avg_actionable_recommendations": mean([m.get("actionable_recommendations", 0) for m in all_metrics]),
                "avg_technical_terms": mean([m.get("technical_terms_count", 0) for m in all_metrics])
            }
        
        # Generate summary
        validation_summary = {
            "dataset_file": dataset_file,
            "total_examples": total_examples,
            "valid_examples": valid_examples,
            "invalid_examples": total_examples - valid_examples,
            "validity_percentage": (valid_examples / total_examples * 100) if total_examples > 0 else 0,
            "issues": all_issues[:50],  # Limit to first 50 issues
            "total_issues": len(all_issues),
            "metrics": overall_metrics
        }
        
        return validation_summary

def main():
    """Main validation function"""
    validator = TrainingDataValidator()
    
    # Validate different dataset files
    dataset_files = [
        "training_data_small.json", 
        "training_data_medium.json",
        "training_data_large.json"
    ]
    
    for dataset_file in dataset_files:
        try:
            print(f"\n{'='*60}")
            print(f"VALIDATING: {dataset_file}")
            print(f"{'='*60}")
            
            summary = validator.validate_dataset(dataset_file)
            
            print(f"\nVALIDATION SUMMARY:")
            print(f"Total Examples: {summary['total_examples']}")
            print(f"Valid Examples: {summary['valid_examples']}")
            print(f"Invalid Examples: {summary['invalid_examples']}")
            print(f"Validity Percentage: {summary['validity_percentage']:.1f}%")
            print(f"Total Issues Found: {summary['total_issues']}")
            
            if summary.get('metrics'):
                print(f"\nQUALITY METRICS:")
                metrics = summary['metrics']
                print(f"Avg Analysis Length: {metrics.get('avg_analysis_length', 0):.0f} chars")
                print(f"Avg Recommendations: {metrics.get('avg_recommendations_count', 0):.1f}")
                print(f"Avg Actionable Recs: {metrics.get('avg_actionable_recommendations', 0):.1f}")
                print(f"Avg Technical Terms: {metrics.get('avg_technical_terms', 0):.1f}")
            
            if summary.get('issues'):
                print(f"\nFIRST FEW ISSUES:")
                for issue in summary['issues'][:10]:
                    print(f"- {issue}")
                if summary['total_issues'] > 10:
                    print(f"... and {summary['total_issues'] - 10} more issues")
            
            # Quality assessment
            validity_score = summary['validity_percentage']
            if validity_score >= 95:
                quality = "EXCELLENT"
            elif validity_score >= 85:
                quality = "GOOD"
            elif validity_score >= 70:
                quality = "ACCEPTABLE"
            else:
                quality = "NEEDS IMPROVEMENT"
            
            print(f"\nOVERALL QUALITY: {quality}")
            
        except FileNotFoundError:
            print(f"File not found: {dataset_file}")
        except Exception as e:
            print(f"Error validating {dataset_file}: {e}")

if __name__ == "__main__":
    main()