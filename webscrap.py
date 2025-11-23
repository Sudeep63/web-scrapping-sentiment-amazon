import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import time
import sqlite3

# Connect to database (creates file if not exists)
conn = sqlite3.connect("user_data.db")
cursor = conn.cursor()

# Create a table for storing product data
cursor.execute("""
CREATE TABLE IF NOT EXISTS product_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_query TEXT,
    product_name TEXT,
    rating TEXT,
    price TEXT,
    link TEXT,
    reviews TEXT,
    overall_sentiment TEXT,
    positive_perc REAL,
    negative_perc REAL,
    neutral_perc REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.title("Web Scrapping System")
st.write("Search any product on Amazon.in and analyze customer review sentiment faster!")

query = st.text_input("Enter product to search:", "laptop")

if st.button("🔍 Search"):
    st.info(f"Fetching products for: {query}")

    # --------------------------------------------------
    # Optimized Chrome setup
    # --------------------------------------------------
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Disable images, CSS, and fonts (to speed up loading)
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.fonts": 2,
        "profile.managed_default_content_settings.cookies": 2,
        "profile.default_content_setting_values.notifications": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Reduce automation detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/120.0.0.0 Safari/537.36")

    # --------------------------------------------------
    # Start Browser
    # --------------------------------------------------
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 8)

    # --------------------------------------------------
    # Search on Amazon
    # --------------------------------------------------
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    driver.get(url)

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
    except:
        st.error("❌ Timeout: No products found.")
        driver.quit()
        st.stop()

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = soup.find_all("div", {"data-component-type": "s-search-result"})

    if not products:
        st.error("❌ No products found.")
        driver.quit()
    else:
        st.write(f"Found {len(products)} results. Extracting top 20 for sentiment analysis...")
        data = []
        analyzer = SentimentIntensityAnalyzer()

        for item in products[:20]:  # fewer products for speed
            # Product title
            title_tag = item.h2
            title = title_tag.text.strip() if title_tag else "N/A"

            # Product link
            link_tag = item.find("a", class_="a-link-normal s-no-outline")
            link = "https://www.amazon.in" + link_tag["href"] if link_tag else "N/A"

            # Product rating
            rating_tag = item.find("span", class_="a-icon-alt")
            rating = rating_tag.text if rating_tag else "No rating"

            # Product price
            price_tag = item.find("span", class_="a-price-whole")
            price = price_tag.text if price_tag else "N/A"

            # ---------------------------------------------
            # Extract Reviews (fast mode)
            # ---------------------------------------------
            review_texts = []
            try:
                driver.get(link)
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span[data-hook='review-body']")))
                product_soup = BeautifulSoup(driver.page_source, "html.parser")
                reviews = product_soup.find_all("span", {"data-hook": "review-body"}, limit=3)

                for r in reviews:
                    review_texts.append(r.text.strip())

                if not review_texts:
                    review_texts.append("No reviews found.")
            except:
                review_texts.append("Error fetching reviews.")

            # Sentiment Analysis
            sentiments = []
            for review in review_texts:
                score = analyzer.polarity_scores(review)['compound']
                if score >= 0.05:
                    sentiments.append("Positive")
                elif score <= -0.05:
                    sentiments.append("Negative")
                else:
                    sentiments.append("Neutral")

            # Calculate percentages
            pos = sentiments.count("Positive")
            neg = sentiments.count("Negative")
            neu = sentiments.count("Neutral")
            total = len(sentiments)
            pos_perc = round((pos / total) * 100, 2)
            neg_perc = round((neg / total) * 100, 2)
            neu_perc = round((neu / total) * 100, 2)

            # Determine overall
            if pos > neg and pos > neu:
                overall_sentiment = "Positive"
            elif neg > pos and neg > neu:
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Neutral"

            combined_reviews = " | ".join(review_texts)

            data.append([
                title, rating, price, link, combined_reviews,
                overall_sentiment, pos_perc, neg_perc, neu_perc
            ])

        driver.quit()

        # --------------------------------------------------
        # Display Data in Streamlit
        # --------------------------------------------------
        df = pd.DataFrame(data, columns=[
            "Product Name", "Rating", "Price", "Link", "Reviews",
            "Overall Sentiment", "Positive %", "Negative %", "Neutral %"
        ])

        st.success("✅ Data fetched successfully in optimized mode!")
        st.dataframe(df)

        # Download CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Download CSV",
            data=csv,
            file_name=f"{query}_amazon_sentiment_fast.csv",
            mime="text/csv"
        )

        # Visualization
        st.subheader("📊 Sentiment Comparison")
        st.bar_chart(df.set_index("Product Name")[["Positive %", "Negative %", "Neutral %"]])

        st.subheader("🌟 Top Products by Positive Sentiment")
        st.dataframe(df.sort_values(by="Positive %", ascending=False).head(5))
