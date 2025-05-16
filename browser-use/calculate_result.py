import json

def calculate_ratios(json_file_path):
    """
    Calculate the ratio of 'Attempted: Yes' and 'Completed: Yes' in final_results from the given JSON file.
    """
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    total_logs = 0
    attempted_yes_count = 0
    completed_yes_count = 0

    # Iterate through each test case
    for test_case in data:
        log_results = test_case.get("log_results", {})
        for log_file, log_data in log_results.items():
            final_result = log_data.get("final_result", {})
            if final_result.get("Attempted") == "Yes":
                attempted_yes_count += 1
            if final_result.get("Completed") == "Yes":
                completed_yes_count += 1
            total_logs += 1

    # Calculate ratios
    attempted_ratio = (attempted_yes_count / total_logs) * 100 if total_logs > 0 else 0
    completed_ratio = (completed_yes_count / total_logs) * 100 if total_logs > 0 else 0

    return {
        "attempted_ratio": attempted_ratio,
        "completed_ratio": completed_ratio,
        "total_logs": total_logs
    }

# Example usage
if __name__ == "__main__":
    json_file_path = "./judgement/judgements_test_cases_email_logs_gemini-2.5-pro.json"


    ratios = calculate_ratios(json_file_path)
    print(json_file_path)
    print(f"Total Logs: {ratios['total_logs']}")
    print(f"Attempted: Yes Ratio: {ratios['attempted_ratio']:.2f}%")
    print(f"Completed: Yes Ratio: {ratios['completed_ratio']:.2f}%")
    print(f"{ratios['attempted_ratio']:.2f}/{ratios['completed_ratio']:.2f}")