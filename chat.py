import json
import random
from datetime import datetime
from review_handler import get_review_sentiment
from comparison_handler import compare_products
from data_handler import load_product_data, save_product_data
from amazon_scraper import AmazonScraper
from utils import query_llm, find_product, normalize_text
from config import load_prompts
import re
from fuzzywuzzy import fuzz

# Load prompts from JSON
prompts = load_prompts()
print("✅ Loaded prompts from prompts.json")

# Load chat history from JSON
def load_chat_history():
    try:
        with open("chatlog.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"chat_history": []}

# Save chat history to JSON
def save_chat_history(user_input, bot_response):
    chat_data = load_chat_history()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_entry = {
        "timestamp": timestamp,
        "user": user_input,
        "bot": bot_response
    }
    
    chat_data["chat_history"].append(new_entry)
    
    with open("chatlog.json", "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=4, ensure_ascii=False)

# Function to get a random greeting from prompts.json
def get_greeting():
    return random.choice(prompts.get("greetings", ["Hello! How can I assist you?"]))

# Function to trigger scraper when a product is missing
def scrape_product(product_name):
    print(f"🔍 Scraping data for {product_name}...")
    try:
        scraper = AmazonScraper()
        product_url = scraper.get_product_url(product_name)
        if product_url:
            print(f"✅ Found product URL: {product_url}")
            product_data = scraper.scrape_amazon(product_url)
            if product_data:
                print(f"✅ Scraped product data: {product_data}")
                save_product_data(product_data)
                return product_data
            else:
                print("❌ No product data found after scraping.")
        else:
            print("❌ No product URL found.")
        return None
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return None

# Function to get product recommendations
def get_product_recommendations(product_name):
    product = find_product(product_name)
    
    if not product:
        print("❌ Product not found in existing data. Triggering scraper...")
        product_data = scrape_product(product_name)
        if product_data:
            print("✅ Scraping successful. Reloading product data...")
            product_data = load_product_data()
            product = find_product(product_name)
    
    if product:
        return f"📌 **Product:** {product.get('Title')}\n💰 **Price:** {product.get('Price', 'Price Not Available')}\n🌐 **Website:** {product.get('Website', 'Unknown')}"
    else:
        return "I couldn't find any product recommendations for that. Let me know if you need something else."

# Function to extract product name from a user query
def extract_product_name(text):
    stopwords = ["buy", "price", "details", "tell", "me", "about", "recommendation", "give", "show", "what", "is", "the", "can", "you"]
    words = [word for word in text.split() if word.lower() not in stopwords]
    product_name = " ".join(words)
    print(f"Extracted product name: {product_name}")
    return product_name.strip()

# Main function to handle user queries
def get_response(user_input):
    if not user_input.strip():
        return random.choice(prompts["fallback_responses"])
        
    product_name = extract_product_name(user_input)
    response = ""

    if any(greeting in user_input.lower() for greeting in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        response = get_greeting()
    elif any(keyword in user_input.lower() for keyword in ["recommendation", "suggest", "tell me about", "what is", "details", "price", "buy"]):
        response = get_product_recommendations(product_name)
    elif any(keyword in user_input.lower() for keyword in ["review", "feedback", "what do people think", "opinion"]):
        response = get_review_sentiment(product_name)
    elif any(keyword in user_input.lower() for keyword in ["compare", "comparison"]):
        response = compare_products(user_input)
    else:
        product = find_product(product_name)
        if product:
            prompt = f"The user asked: {user_input}. Respond based on the available product information."
            response = query_llm(prompt, product)
        else:
            response = "I couldn't find any product recommendations for that. Let me know if you need something else."
    
    save_chat_history(user_input, response)
    
    return response

# Example Usage
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye!")
            break
        response = get_response(user_input)
        print(f"Chatbot: {response}")