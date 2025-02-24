import pandas as pd
import numpy as np
import requests
import json

def generate_diy_project(detected_objects_str, gemini_api_key):
    """
    Process detected objects, remove outliers, and generate a DIY project idea.

    Parameters:
    - detected_objects_str (str): JSON string of detected objects and their frequencies.
    - gemini_api_key (str): Your Gemini API key.

    Returns:
    - dict: A dictionary containing the DIY project idea or an error message.
    """
    # Convert string to dictionary
    detected_objects = json.loads(detected_objects_str)

    # Convert to DataFrame
    df = pd.DataFrame(list(detected_objects.items()), columns=["Object", "Frequency"])

    # Remove outliers using IQR
    Q1 = df["Frequency"].quantile(0.25)
    Q3 = df["Frequency"].quantile(0.75)
    IQR = Q3 - Q1
    df_filtered = df[(df["Frequency"] >= (Q1 - 1.5 * IQR)) & (df["Frequency"] <= (Q3 + 1.5 * IQR))]

    # Convert back to dictionary (without outliers)
    cleaned_data = dict(zip(df_filtered["Object"], df_filtered["Frequency"]))

    # Generate DIY project using Gemini API
    prompt = (
        f"""
    Suggest a creative DIY project idea using these objects: {cleaned_data}. 
    Provide the response in the following JSON format:
    {{
        "title": "DIY Project Title",
        "description": "Short description of the project.",
        "steps": [
            "Step 1...",
            "Step 2...",
            "Step 3..."
        ]
    }}
    """
    )

    gemini_endpoint = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={gemini_api_key}"
    response = requests.post(gemini_endpoint, json={"contents": [{"parts": [{"text": prompt}]}]})

    if response.status_code == 200:
        diy_project = response.json()
        return diy_project
    else:
        return {"error": response.text}

# Example usage
detected_objects_str = '{"scissors": 5, "glue": 12, "paper": 100, "pencil": 3, "eraser": 2, "ruler": 25, "tape": 7}'
gemini_api_key = "AIzaSyCyFi55AE8nKFwQakb2MzMkCLx6d1774uE"  # Replace with your actual Gemini API key
result = generate_diy_project(detected_objects_str, gemini_api_key)
print(json.dumps(result, indent=2))
