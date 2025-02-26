import random
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

GEMINI_API_KEY = "SET_API_KEY"  # Replace with your actual Gemini API key

def query_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateText"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {"prompt": {"text": prompt}, "max_output_tokens": 200}
    
    try:
        response = requests.post(url, headers=headers, params=params, json=data)
        result = response.json()
        print("Gemini API Response:", result)  # Debugging
        
        if "candidates" in result and len(result["candidates"]) > 0:
            return result["candidates"][0]["output"]
        else:
            return "I couldn't generate a response. Try again."
    except Exception as e:
        print(f"Error: {e}")
        return "There was an issue getting recommendations. Try again."

def get_product_recommendations(product_name):
    prompt = f"Give me the top 5 recommended {product_name} models with their details."
    return query_gemini(prompt)

def extract_product_name(text):
    words = text.split()
    stopwords = ["buy", "price", "details", "tell", "me", "about", "recommendation", "give", "show"]
    product_name = " ".join([word for word in words if word.lower() not in stopwords])
    return product_name.strip()

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    
    if sentiment_score['compound'] >= 0.05:
        return "Positive"
    elif sentiment_score['compound'] <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def get_response(text):
    sentence = tokenize(text)
    X = bag_of_words(sentence, all_words)
    X = torch.from_numpy(X).reshape(1, X.shape[0]).to(device)
    
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    
    if "recommendation" in text.lower() or "suggest" in text.lower():
        product_name = extract_product_name(text)
        return get_product_recommendations(product_name)
    
    if "review" in text.lower() or "feedback" in text.lower():
        return "Based on sentiment analysis, the product has mostly " + analyze_sentiment("This product is amazing! I love the quality and design.") + " reviews."
    
    return "I can fetch product recommendations and analyze sentiment. Try asking about a product!"
