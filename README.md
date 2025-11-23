# web-scrapping-sentiment-amazon
Web Scraping System – Amazon Product Sentiment Analyzer

This project is a web scraping system that extracts product information from Amazon.in and performs sentiment analysis on customer reviews. The application uses Selenium for scraping dynamic content, BeautifulSoup for parsing HTML, VADER for sentiment analysis, SQLite for local data storage, and Streamlit for the user interface.

Features
Search for any product on Amazon.in.
Scrape product details including title, price, rating, and product link.
Extract the top three customer reviews from each product.
Perform sentiment analysis using the VADER sentiment analyzer.
Display sentiment percentages for each product.
Store all extracted data in a SQLite database.
Download results as a CSV file.
View sentiment comparison through visual charts in the Streamlit interface.

Technologies Used
Python
Streamlit
Selenium WebDriver
WebDriver Manager
BeautifulSoup
VADER Sentiment Analysis
Pandas
SQLite Database

How It Works
The user enters a product keyword in the Streamlit application.
Selenium loads the Amazon search results page.
The scraper extracts product titles, ratings, prices, and product links.
For each product, Selenium navigates to the product page and extracts up to three customer reviews.
The VADER sentiment analyzer processes each review and classifies it as positive, negative, or neutral.
The application calculates sentiment percentages and determines an overall sentiment classification.
The results are displayed in a table, saved to a database, and optionally downloaded as a CSV file.

Installation and Setup
Clone the repository:
git clone https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git
cd REPOSITORY_NAME

Install required Python packages:
pip install -r requirements.txt

Run the Streamlit application:
streamlit run app.py

File Structure
project/
│── app.py
│── requirements.txt
│── README.md
│── user_data.db (automatically created)
│── screenshots/ (optional)

Database

The SQLite database user_data.db stores:
User query
Product name
Rating
Price
Product link
Extracted reviews
Overall sentiment
Positive, negative, and neutral percentage scores
Timestamp
The database is automatically created when the application runs.

Limitations
Amazon frequently changes its HTML structure and may trigger CAPTCHA, which can affect scraping.
Selenium increases load time compared to API-based scraping.
Only the first three reviews per product are extracted for faster performance.

Future Enhancements
Multi-website scraping (Flipkart, Walmart, Google Shopping).
Integration of advanced sentiment models such as BERT or RoBERTa.
Price comparison across platforms.
Automatic CAPTCHA solving methods.
Deployment on cloud platforms.
