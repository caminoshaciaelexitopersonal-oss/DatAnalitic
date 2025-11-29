from typing import List, Dict, Any, Optional

def select_best_model(
    all_results: List[Dict[str, Any]],
    metric_to_optimize: str
) -> Optional[Dict[str, Any]]:
    """
    Selects the best model from a list of trial results based on a specified metric.

    Args:
        all_results: A list of dictionaries, where each dictionary holds the
                     results of a single model trial.
        metric_to_optimize: The key of the metric to use for comparison.
                            Assumes higher is better.

    Returns:
        The dictionary corresponding to the best performing model, or None if
        the input list is empty.
    """
    if not all_results:
        return None

    # Filter out failed runs that may not have the metric
    valid_results = [
        r for r in all_results
        if r.get("status") == "success" and metric_to_optimize in r
    ]

    if not valid_results:
        return None

    # Sort the results in descending order based on the optimization metric
    sorted_results = sorted(
        valid_results,
        key=lambda x: x[metric_to_optimize],
        reverse=True
    )

    return sorted_results[0]
