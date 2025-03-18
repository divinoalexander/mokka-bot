# utils.py
import json
import re
from fuzzywuzzy import fuzz
from data_handler import load_product_data  # Import the missing function
import ollama  # Ensure this is installed and configured

def query_llm(prompt, product_data=None):
    """
    Generate a response using the LLM.
    """
    try:
        system_instruction = (
            "You are a customer support chatbot. Provide concise, relevant answers "
            "using only the provided data. Do NOT make up information. If data is missing, just say 'I don't have that information'."
        )
        
        if product_data:
            prompt += f"\n\nProduct Data:\nTitle: {product_data.get('Title')}\nPrice: {product_data.get('Price')}\nReviews: {json.dumps(product_data.get('Reviews'), indent=2)}"
        
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error: {e}")
        return "I'm having trouble generating a response. Please try again later."

def find_product(product_name):
    """
    Find a product in the JSON data using flexible matching logic.
    """
    product_data = load_product_data()  # Now this function is properly imported
    normalized_query = normalize_text(product_name)
    
    best_match = None
    best_score = 0
    
    for product in product_data:
        normalized_title = normalize_text(product.get("Title", ""))
        score = fuzz.partial_ratio(normalized_query, normalized_title)
        if score > best_score:
            best_match = product
            best_score = score
    
    if best_score >= 70:
        print(f"✅ Found a match for '{product_name}' with a similarity score of {best_score}%")
        print(f"Matched Product: {best_match.get('Title')}")
        return best_match
    else:
        print(f"❌ No matches found for '{product_name}' (best score: {best_score}%)")
        return None

def normalize_text(text):
    """
    Normalize text by converting to lowercase, removing special characters, and trimming spaces.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text