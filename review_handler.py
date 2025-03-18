from utils import query_llm, find_product

def get_review_sentiment(product_name):
    """
    Generate a comprehensive review summary using the LLM based on reviews in the JSON file.
    """
    product = find_product(product_name)
    if not product:
        return "I couldn't find any reviews for this product. Let me know if you need help with something else!"

    if "Reviews" in product:
        all_reviews = product["Reviews"].get("Best Reviews", []) + product["Reviews"].get("Worst Reviews", [])
        if not all_reviews:
            return "There are no reviews available for this product yet. Check back later!"

        review_texts = [review["Review"] for review in all_reviews]
        combined_reviews = "\n".join(review_texts)

        prompt = (
            f"Here are some reviews for the product '{product_name}':\n\n{combined_reviews}\n\n"
            "Please summarize the reviews in a user-friendly way. Highlight the key points, "
            "mention what users liked and disliked, and provide an overall impression. "
            "Make it sound like a helpful chatbot response."
        )

        response = query_llm(prompt)
        return response
    else:
        return "There are no reviews available for this product yet. Check back later!"