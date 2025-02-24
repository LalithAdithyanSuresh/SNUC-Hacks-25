import google.generativeai as genai
import json
import re
import numpy as np

# Set up Gemini API
API_KEY = "AIzaSyCyFi55AE8nKFwQakb2MzMkCLx6d1774uE"
genai.configure(api_key=API_KEY)

def remove_outliers(data_dict, threshold=3):
    """Removes outliers from the object frequency dictionary using Z-score."""
    values = np.array(list(data_dict.values()))
    mean = np.mean(values)
    std_dev = np.std(values)

    filtered_data = {
        key: value
        for key, value in data_dict.items()
        if abs((value - mean) / std_dev) <= threshold
    }
    return filtered_data

def prompt_gemini(filtered_objects):
    """Generates 3 fun, safe, and creative DIY experiments using available household items."""
    object_list = ", ".join(filtered_objects.keys())
    model = genai.GenerativeModel("gemini-pro")

    # Step 1: Ask Gemini for 3 structured experiment ideas
    project_prompt = f"""
    Suggest three different fun, safe, and educational DIY experiments using some of these objects: {object_list}.
    - The experiments should be engaging and suitable for all ages.
    - They must be harmless and easy to conduct at home.
    - They should make good use of common household materials.
    - You DO NOT need to use all the objects listed; pick the best ones for exciting experiments.

    Provide the response in valid JSON format:
    {{
        "experiments": [
            {{
                "title": "Experiment 1 Title",
                "description": "Short description of Experiment 1.",
                "steps": [
                    "Step 1...",
                    "Step 2...",
                    "Step 3..."
                ]
            }},
            {{
                "title": "Experiment 2 Title",
                "description": "Short description of Experiment 2.",
                "steps": [
                    "Step 1...",
                    "Step 2...",
                    "Step 3..."
                ]
            }},
            {{
                "title": "Experiment 3 Title",
                "description": "Short description of Experiment 3.",
                "steps": [
                    "Step 1...",
                    "Step 2...",
                    "Step 3..."
                ]
            }}
        ]
    }}
    Ensure the output is valid JSON.
    """
    
    details_prompt = f"""
    You are given the following objects detected in an environment: {object_list}.  
    Your task is to **ONLY describe these exact objects** in relation to the experiment.  
    - Do NOT introduce any new objects.  
    - The description must be relevant to how the object can be used in a fun DIY experiment.  

    Provide the response in valid JSON format:
    {{
        "object_1": "Specific use of the object in an experiment.",
        "object_2": "Specific use of the object in an experiment."
    }}
    Only describe the given objects and ensure the output is valid JSON.
    """

    # Generate responses
    project_response = model.generate_content(project_prompt)
    details_response = model.generate_content(details_prompt)

    # Debugging: Print raw responses
    print("Raw Project Response:", project_response.text)
    print("Raw Details Response:", details_response.text)

    # Function to clean out the Markdown code block
    def clean_json_response(response_text):
        return re.sub(r'```json\n|```', '', response_text).strip()

    # Clean and parse JSON
    try:
        experiments_data = json.loads(clean_json_response(project_response.text))
    except json.JSONDecodeError:
        print("Error: Gemini response is not valid JSON for the experiments.")
        experiments_data = {
            "error": "Invalid response from Gemini API",
            "raw_response": project_response.text
        }

    try:
        object_details = json.loads(clean_json_response(details_response.text))
    except json.JSONDecodeError:
        print("Error: Gemini response is not valid JSON for object details.")
        object_details = {
            "error": "Invalid response from Gemini API",
            "raw_response": details_response.text
        }

    return experiments_data, object_details


filtered_objects = remove_outliers(input_objects)

# Get 3 DIY experiment ideas and object details
if filtered_objects:
    diy_experiments, object_details = prompt_gemini(filtered_objects)
else:
    diy_experiments = {"error": "No valid objects left after filtering outliers."}
    object_details = {}

# Format output as JSON
output_json = {
    "filtered_objects": filtered_objects,
    "diy_experiments": diy_experiments,
    "object_details": object_details
}

# Print formatted JSON output
print(json.dumps(output_json, indent=4))
