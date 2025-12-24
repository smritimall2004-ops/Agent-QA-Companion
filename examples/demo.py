import logging

from orchestration.pipeline import IngestionNormalizationPipeline


def main():
    """
    Demonstration of the ingestion and normalization pipeline.
    """
    import json
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*80)
    print("INGESTION & NORMALIZATION PIPELINE - DEMONSTRATION")
    print("="*80)
    
    # Initialize pipeline
    pipeline = IngestionNormalizationPipeline(
        enable_nlp_enrichment=False,  # Disable for demo
        confidence_threshold=0.5
    )
    
    # Example 1: Process free text
    print("\n" + "="*80)
    print("EXAMPLE 1: Free Text Input")
    print("="*80)
    
    freetext_input = """
    When I click the Submit button on the checkout page, I get a NullPointerException.
    This happens in the PaymentService module.
    
    Steps to reproduce:
    1. Add items to cart
    2. Go to checkout
    3. Enter payment info
    4. Click Submit
    
    Actual behavior: Application crashes with NullPointerException
    Expected behavior: Order should be submitted successfully
    """
    
    bug1 = pipeline.process_freetext(freetext_input)
    
    print("\n📊 Normalized Output:")
    print(f"  Bug ID: {bug1.bug_id}")
    print(f"  Overall Confidence: {bug1.overall_confidence:.2f}")
    print(f"  Fields extracted by RegEx: {bug1.fields_extracted_by_regex}")
    print(f"\n  Error Type: {bug1.error_type.value} (confidence: {bug1.error_type.confidence:.2f})")
    print(f"  Component: {bug1.component_module.value} (confidence: {bug1.component_module.confidence:.2f})")
    print(f"  Repro Steps: {bug1.trigger_repro_steps.value[:100]}... (confidence: {bug1.trigger_repro_steps.confidence:.2f})")
    
    # Example 2: Process Azure DevOps bug
    print("\n" + "="*80)
    print("EXAMPLE 2: Azure DevOps Bug")
    print("="*80)
    
    ado_bug = {
        "id": "67890",
        "fields": {
            "System.Title": "Database connection timeout in UserService",
            "System.Description": "Users experiencing timeouts when logging in during peak hours",
            "Microsoft.VSTS.TCM.ReproSteps": "1. Wait until 9am peak load\n2. Attempt login\n3. Observe TimeoutException",
            "Microsoft.VSTS.Common.AcceptanceCriteria": "Login should complete within 2 seconds"
        }
    }
    
    bug2 = pipeline.process_ado_bug(ado_bug)
    
    print("\n📊 Normalized Output:")
    print(f"  Bug ID: {bug2.bug_id}")
    print(f"  Overall Confidence: {bug2.overall_confidence:.2f}")
    print(f"  Source: {bug2.source_metadata.source_type}")
    print(f"  ADO Work Item: {bug2.source_metadata.ado_work_item_id}")
    print(f"\n  Error Type: {bug2.error_type.value} (confidence: {bug2.error_type.confidence:.2f})")
    print(f"  Component: {bug2.component_module.value} (confidence: {bug2.component_module.confidence:.2f})")
    
    # Example 3: Export to JSON
    print("\n" + "="*80)
    print("EXAMPLE 3: JSON Export (Agent-Ready Output)")
    print("="*80)
    
    json_output = bug1.model_dump_json(indent=2)
    print(json_output[:1000] + "...\n")
    
    # Example 4: Low confidence detection
    print("\n" + "="*80)
    print("EXAMPLE 4: Low Confidence Field Detection")
    print("="*80)
    
    low_conf_fields = bug1.get_low_confidence_fields(threshold=0.6)
    print(f"Fields needing enrichment (< 0.6): {low_conf_fields}")
    
    print("\n" + "="*80)
    print("✅ PIPELINE DEMONSTRATION COMPLETE")
    print("="*80)
    print("\n🎯 Key Takeaways:")
    print("  - All input types normalize to the same schema")
    print("  - Confidence scoring is deterministic and field-level")
    print("  - NLP enrichment can be enabled for low-confidence fields")
    print("  - Output is clean, structured, and agent-ready")
    print("  - No raw text blobs pass through to AI agents")


if __name__ == "__main__":
    main()
