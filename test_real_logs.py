#!/usr/bin/env python
"""
Real-World Error Log Testing Script

This script processes actual error log files and demonstrates
the ingestion & normalization pipeline with production-like data.
"""

import logging
import json
from pathlib import Path
from orchestration.pipeline import IngestionNormalizationPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def print_separator(title=""):
    """Print a formatted separator."""
    print("\n" + "="*80)
    if title:
        print(f"{title}")
        print("="*80)

def print_bug_summary(bug, log_file):
    """Print a formatted summary of the normalized bug."""
    print(f"\n📄 Source File: {log_file}")
    print(f"🆔 Bug ID: {bug.bug_id}")
    print(f"📊 Overall Confidence: {bug.overall_confidence:.2f}")
    print(f"✅ Fields Extracted: {bug.fields_extracted_by_regex}/{bug.total_extractable_fields}")
    print(f"\n📝 Extracted Fields:")
    
    # Error Type
    if bug.error_type.value:
        print(f"   🔴 Error Type: {bug.error_type.value}")
        print(f"      Confidence: {bug.error_type.confidence:.2f} | Source: {bug.error_type.source.value}")
    else:
        print(f"   🔴 Error Type: [NOT DETECTED]")
    
    # Component/Module
    if bug.component_module.value:
        print(f"   🧩 Component: {bug.component_module.value}")
        print(f"      Confidence: {bug.component_module.confidence:.2f} | Source: {bug.component_module.source.value}")
    else:
        print(f"   🧩 Component: [NOT DETECTED]")
    
    # Trigger/Repro Steps
    if bug.trigger_repro_steps.value:
        steps = bug.trigger_repro_steps.value[:100] + "..." if len(bug.trigger_repro_steps.value) > 100 else bug.trigger_repro_steps.value
        print(f"   🔄 Repro Steps: {steps}")
        print(f"      Confidence: {bug.trigger_repro_steps.confidence:.2f} | Source: {bug.trigger_repro_steps.source.value}")
    else:
        print(f"   🔄 Repro Steps: [NOT DETECTED]")
    
    # Observed Behavior
    if bug.observed_behavior.value:
        observed = bug.observed_behavior.value[:100] + "..." if len(bug.observed_behavior.value) > 100 else bug.observed_behavior.value
        print(f"   👁️  Observed: {observed}")
        print(f"      Confidence: {bug.observed_behavior.confidence:.2f} | Source: {bug.observed_behavior.source.value}")
    else:
        print(f"   👁️  Observed: [NOT DETECTED]")
    
    # Expected Behavior
    if bug.expected_behavior.value:
        expected = bug.expected_behavior.value[:100] + "..." if len(bug.expected_behavior.value) > 100 else bug.expected_behavior.value
        print(f"   ✓  Expected: {expected}")
        print(f"      Confidence: {bug.expected_behavior.confidence:.2f} | Source: {bug.expected_behavior.source.value}")
    else:
        print(f"   ✓  Expected: [NOT DETECTED]")
    
    # Low confidence fields
    low_conf_fields = bug.get_low_confidence_fields(threshold=0.6)
    if low_conf_fields:
        print(f"\n⚠️  Fields needing enrichment (< 0.6): {', '.join(low_conf_fields)}")

def save_json_output(bug, output_file):
    """Save normalized bug as JSON."""
    json_output = bug.model_dump_json(indent=2)
    with open(output_file, 'w') as f:
        f.write(json_output)
    print(f"💾 JSON output saved to: {output_file}")

def main():
    """Main testing function."""
    print_separator("🚀 REAL-WORLD ERROR LOG TESTING")
    
    # Initialize pipeline
    print("\n🔧 Initializing Pipeline...")
    pipeline = IngestionNormalizationPipeline(
        enable_nlp_enrichment=False,  # Can enable for low-confidence fields
        confidence_threshold=0.5
    )
    print("✅ Pipeline initialized successfully")
    
    # Define test data directory
    test_data_dir = Path(__file__).parent / "test_data"
    
    if not test_data_dir.exists():
        print(f"\n❌ Error: test_data directory not found at {test_data_dir}")
        print("Please ensure error log files are in the test_data/ directory")
        return
    
    # Get all log files
    log_files = list(test_data_dir.glob("*.log")) + list(test_data_dir.glob("*.txt"))
    
    if not log_files:
        print(f"\n❌ No log files found in {test_data_dir}")
        print("Please add .log or .txt files to the test_data/ directory")
        return
    
    print(f"\n📂 Found {len(log_files)} log file(s) to process")
    
    # Process each log file
    results = []
    for idx, log_file in enumerate(log_files, 1):
        print_separator(f"TEST {idx}/{len(log_files)}: Processing {log_file.name}")
        
        try:
            # Process the error log
            bug = pipeline.process_error_log(str(log_file))
            results.append({
                'file': log_file.name,
                'bug': bug,
                'success': True
            })
            
            # Print summary
            print_bug_summary(bug, log_file.name)
            
            # Save JSON output
            output_file = test_data_dir / f"{log_file.stem}_normalized.json"
            save_json_output(bug, output_file)
            
        except Exception as e:
            print(f"\n❌ Error processing {log_file.name}: {e}")
            results.append({
                'file': log_file.name,
                'bug': None,
                'success': False,
                'error': str(e)
            })
    
    # Print overall statistics
    print_separator("📊 PROCESSING STATISTICS")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n✅ Successfully Processed: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        confidences = [r['bug'].overall_confidence for r in successful]
        avg_confidence = sum(confidences) / len(confidences)
        
        print(f"\n📈 Confidence Metrics:")
        print(f"   Average: {avg_confidence:.2f}")
        print(f"   Highest: {max(confidences):.2f}")
        print(f"   Lowest: {min(confidences):.2f}")
        
        # Classification breakdown
        high_conf = sum(1 for c in confidences if c >= 0.8)
        medium_conf = sum(1 for c in confidences if 0.5 <= c < 0.8)
        low_conf = sum(1 for c in confidences if c < 0.5)
        
        print(f"\n🎯 Confidence Distribution:")
        print(f"   HIGH (≥0.8): {high_conf} ({high_conf/len(successful)*100:.0f}%)")
        print(f"   MEDIUM (0.5-0.79): {medium_conf} ({medium_conf/len(successful)*100:.0f}%)")
        print(f"   LOW (<0.5): {low_conf} ({low_conf/len(successful)*100:.0f}%)")
        
        # Field extraction statistics
        total_fields_extracted = sum(r['bug'].fields_extracted_by_regex for r in successful)
        total_possible = len(successful) * 5  # 5 core fields per bug
        extraction_rate = (total_fields_extracted / total_possible) * 100
        
        print(f"\n🔍 Field Extraction Rate:")
        print(f"   {total_fields_extracted}/{total_possible} fields extracted ({extraction_rate:.1f}%)")
    
    if failed:
        print(f"\n⚠️  Failed Files:")
        for r in failed:
            print(f"   - {r['file']}: {r.get('error', 'Unknown error')}")
    
    print_separator("✅ TESTING COMPLETE")
    print("\n💡 Next Steps:")
    print("   1. Review JSON outputs in test_data/ directory")
    print("   2. Check low-confidence fields for potential NLP enrichment")
    print("   3. Add more patterns to pattern_registry.py if needed")
    print("   4. Enable NLP enrichment for better coverage")
    print("\n🎯 All normalized bugs are ready for AI agent consumption!")

if __name__ == "__main__":
    main()
