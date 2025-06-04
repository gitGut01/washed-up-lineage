from datetime import timedelta
import json

AMOUNT_OF_CHARACTERS = 40

def print_summary(overall_stats, overall_execution_time):
    """Print a comprehensive summary of the extraction process.
    
    Args:
        overall_stats: Dictionary containing overall statistics
        overall_execution_time: Total execution time in seconds
    """
    overall_time_str = str(timedelta(seconds=round(overall_execution_time)))
    
    print("\n\n")
    print("=" * AMOUNT_OF_CHARACTERS)
    print("===       OVERALL PROCESSING SUMMARY      ===")
    print("=" * AMOUNT_OF_CHARACTERS)
    print(f"Total files processed: {overall_stats['total_files']}")
    
    success_percentage = 0
    failed_percentage = 0
    if overall_stats['total_files'] > 0:
        success_percentage = overall_stats['success_count']/overall_stats['total_files']*100
        failed_percentage = overall_stats['failed_count']/overall_stats['total_files']*100

    print(f"Successfully processed: {overall_stats['success_count']} ({success_percentage:.1f}%)")
    print(f"Failed: {overall_stats['failed_count']} ({failed_percentage:.1f}%)")
    
    print(
        f"Input/Output token count: {overall_stats['input_token_count']}/{overall_stats['output_token_count']} "
        f"(cost ${overall_stats['input_cost']:.3f}/${overall_stats['output_cost']:.3f})"
    )

    print(f"Total execution time: {overall_time_str}")
    print("=" * AMOUNT_OF_CHARACTERS)


def export_failed_scripts(all_failed_scripts, filename="failed_scripts.json"):
    """Export failed scripts to a JSON file for later analysis.
    
    Args:
        all_failed_scripts: List of failed scripts
        filename: Name of the file to export to
    """
    with open(filename, "w") as f:
        json.dump(all_failed_scripts, f, indent=2)