from data_handler import load_product_data
from utils import query_llm, find_product
import json

def compare_products(user_input):
    """
    Compare two or more products based on user input.
    """
    product_names = [name.strip() for name in user_input.lower().replace("compare", "").split("and")]
    
    products = []
    for name in product_names:
        product = find_product(name)
        if product:
            products.append(product)
    
    if len(products) < 2:
        return "I need at least two products to compare. Please provide the names of the products you want to compare."

    prompt = (
        f"Here are the details of the products to compare:\n\n"
        f"{json.dumps(products, indent=2)}\n\n"
        "Please compare these products in a user-friendly way. Highlight the key differences, "
        "mention the pros and cons of each, and provide a recommendation if possible. "
        "Make it sound like a helpful chatbot response."
    )

    response = query_llm(prompt)
    return response