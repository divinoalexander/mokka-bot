import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from googlesearch import search
from selenium.common.exceptions import WebDriverException, TimeoutException

class AmazonScraper:
    def __init__(self):
        # Setup chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("start-maximized")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

    def get_product_url(self, product_name):
        query = f"{product_name} site:amazon.com"
        print(f"🔍 Google Search Query: {query}")
        try:
            for result in search(query, num_results=5):
                if "amazon.com" in result and "/dp/" in result:
                    print(f"✅ Found Amazon URL: {result}")
                    return result
        except Exception as e:
            print(f"❌ Google Search Error: {e}")
        return None

    def scrape_amazon_reviews(self, driver, url):
        try:
            # Navigate to the reviews page
            review_url = url.split('/dp/')[0] + '/product-reviews/' + url.split('/dp/')[1].split('/')[0]
            driver.get(review_url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            review_elements = soup.find_all("span", {"data-hook": "review-body"})
            rating_elements = soup.find_all("i", {"data-hook": "review-star-rating"})

            # If no reviews found on the review page, try the main page
            if not review_elements:
                driver.get(url)
                time.sleep(3)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                review_elements = soup.find_all("span", {"data-hook": "review-body"})
                rating_elements = soup.find_all("i", {"data-hook": "review-star-rating"})

            reviews = []
            for i in range(min(len(review_elements), len(rating_elements))):
                text = review_elements[i].text.strip()
                try:
                    star_rating = float(rating_elements[i].text.strip().split(" ")[0])
                except:
                    star_rating = 0.0
                reviews.append({"Rating": star_rating, "Review": text})

            best_reviews = sorted(reviews, key=lambda x: x["Rating"], reverse=True)[:5]
            worst_reviews = sorted(reviews, key=lambda x: x["Rating"])[:5]

            return {"Best Reviews": best_reviews, "Worst Reviews": worst_reviews}

        except Exception as e:
            print(f"❌ Amazon Review Scraping Error: {e}")
            return {"Best Reviews": [], "Worst Reviews": []}

    def extract_price(self, soup):
        # Try multiple price selectors in order
        price_selectors = [
            ("span.a-price span.a-offscreen", lambda el: el.text.strip()),
            ("span.a-price-whole", lambda el: el.text.strip() + ".00"),
            ("span#priceblock_ourprice", lambda el: el.text.strip()),
            ("span#priceblock_dealprice", lambda el: el.text.strip()),
            ("span.a-color-price", lambda el: el.text.strip())
        ]

        for selector, extractor in price_selectors:
            elements = soup.select(selector)
            if elements:
                try:
                    return extractor(elements[0])
                except Exception as e:
                    print(f"Price extraction error with selector {selector}: {e}")

        # If all selectors fail, look for any element with price-like text
        price_keywords = ["price", "deal", "amount"]
        for keyword in price_keywords:
            elements = soup.find_all(lambda tag: any(keyword in attr.lower() for attr in tag.attrs.values() if isinstance(attr, str)))
            for element in elements:
                if element.text and "$" in element.text:
                    price_text = element.text.strip()
                    # Extract just the price part if there's extra text
                    import re
                    price_match = re.search(r'\$\d+(?:\.\d{1,2})?', price_text)
                    if price_match:
                        return price_match.group(0)

        return "Price Not Found"

    def scrape_amazon(self, url):
        driver = None
        try:
            # Initialize driver
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)

            # Navigate to product page
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "productTitle"))
            )
            time.sleep(2)  # Wait a bit more for dynamic content

            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extract title
            title_element = soup.find("span", id="productTitle")
            title = title_element.text.strip() if title_element else "Title Not Found"

            # Extract price
            price = self.extract_price(soup)

            # Get reviews using the current driver
            reviews = self.scrape_amazon_reviews(driver, url)

            # Create and return product data
            product_data = {
                "Website": "Amazon",
                "Title": title,
                "Price": price,
                "Reviews": reviews,
                "URL": url
            }

            # Close driver before returning
            driver.quit()

            return product_data

        except TimeoutException:
            print("❌ Amazon page took too long to load.")
            if driver:
                driver.quit()
            return {"Website": "Amazon", "Title": "N/A", "Price": "N/A", "Reviews": {"Best Reviews": [], "Worst Reviews": []}, "URL": url}

        except Exception as e:
            print(f"❌ Amazon Scraping Error: {e}")
            if driver:
                driver.quit()
            return {"Website": "Amazon", "Title": "N/A", "Price": "N/A", "Reviews": {"Best Reviews": [], "Worst Reviews": []}, "URL": url}