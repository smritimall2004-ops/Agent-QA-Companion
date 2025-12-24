from orchestration.pipeline import IngestionNormalizationPipeline


def batch_process_example():
    """Example of batch processing multiple inputs."""
    
    print("\n" + "="*80)
    print("BATCH PROCESSING EXAMPLE")
    print("="*80)
    
    pipeline = IngestionNormalizationPipeline(enable_nlp_enrichment=False)
    
    # Sample inputs from different sources
    inputs = [
        {
            "type": "freetext",
            "data": "TimeoutException in DatabaseService when querying users table"
        },
        {
            "type": "freetext",
            "data": "App crashes with NullPointerException in LoginController"
        },
        {
            "type": "ado",
            "data": {
                "id": "12345",
                "fields": {
                    "System.Title": "SQLException in ReportGenerator",
                    "System.Description": "Database connection fails during report generation",
                    "Microsoft.VSTS.TCM.ReproSteps": "1. Navigate to Reports\n2. Click Generate\n3. Observe SQLException"
                }
            }
        }
    ]
    
    # Process all inputs
    results = []
    for idx, input_item in enumerate(inputs, 1):
        try:
            if input_item["type"] == "freetext":
                bug = pipeline.process_freetext(input_item["data"])
            elif input_item["type"] == "ado":
                bug = pipeline.process_ado_bug(input_item["data"])
            
            results.append(bug)
            print(f"\n✅ Processed input {idx}: {bug.error_type.value} "
                  f"(confidence: {bug.overall_confidence:.2f})")
        
        except Exception as e:
            print(f"\n❌ Failed to process input {idx}: {e}")
    
    # Aggregate statistics
    print(f"\n📊 Batch Statistics:")
    print(f"  Total processed: {len(results)}")
    print(f"  Average confidence: {sum(b.overall_confidence for b in results) / len(results):.2f}")
    print(f"  High confidence (≥0.8): {sum(1 for b in results if b.overall_confidence >= 0.8)}")
    print(f"  Medium confidence (0.5-0.79): {sum(1 for b in results if 0.5 <= b.overall_confidence < 0.8)}")
    print(f"  Low confidence (<0.5): {sum(1 for b in results if b.overall_confidence < 0.5)}")

