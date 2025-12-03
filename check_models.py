import google.generativeai as genai
import os

try:
    # --- Configuration ---
    # Load the API key from the environment variable
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not found.")
    else:
        genai.configure(api_key=GEMINI_API_KEY)
        
        print("--- Finding models that support 'generateContent' ---")
        
        found_models = []
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                found_models.append(model.name)
                print(f"Found model: {model.name}")

        if not found_models:
            print("\nNo models found that support 'generateContent'.")
            print("Please check the following:")
            print("1. Your API key is correct and active.")
            print("2. The 'Generative Language API' (or similar) is enabled in your Google Cloud project.")
            print("3. Your project has a valid billing account associated with it.")
        else:
            print(f"\n--- Recommended model to use in app.py ---")
            # Heuristic: prefer 'gemini-1.5-pro-latest' or 'gemini-1.0-pro' if available
            recommended = "No specific recommendation, choose one from the list above."
            if 'models/gemini-1.5-pro-latest' in found_models:
                recommended = 'models/gemini-1.5-pro-latest'
            elif 'models/gemini-1.0-pro' in found_models:
                recommended = 'models/gemini-1.0-pro'
            elif found_models:
                recommended = found_models[0] # Default to the first one found
            
            print(f"Recommended: {recommended}")


except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print("This could be due to an invalid API key or network issues.")
