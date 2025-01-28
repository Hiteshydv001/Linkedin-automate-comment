import csv
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from dotenv import load_dotenv
from fpdf import FPDF
import re

# Load environment variables from .env file (if available)
load_dotenv()

# Get credentials from environment variables (or hardcode if needed)
EMAIL = os.getenv("EMAIL")  # e.g. "your-email@example.com"
PASSWORD = os.getenv("PASSWORD")  # e.g. "your-password"

def scrape_latest_feed(email, password):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    )
    driver = uc.Chrome(options=options)

    try:
        # Login to LinkedIn
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Wait until the feed page loads
        WebDriverWait(driver, 10).until(EC.url_contains("feed"))
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)

        # Scroll down to load more posts
        for _ in range(3):  # Adjust range for more scrolling
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))  # Mimic human behavior with random delays

        # Scrape the first post only
        posts = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")
        latest_feed = []

        if posts:
            post = posts[0]  # Fetch the first post
            try:
                # Click "See more" if it exists to expand content
                try:
                    see_more_button = post.find_element(By.XPATH, './/button[contains(text(), "See more")]')
                    driver.execute_script("arguments[0].click();", see_more_button)
                    time.sleep(2)
                except:
                    pass  # If no "See more" button, proceed

                # Extract post content
                content = post.find_element(By.XPATH, './/span[contains(@class, "break-words")]').text

                # Extract likes and comments (if available)
                try:
                    likes = post.find_element(By.XPATH, './/span[contains(@class, "social-details-social-counts__reactions")]').text
                except:
                    likes = "0"

                try:
                    comments = post.find_element(By.XPATH, './/span[contains(@class, "social-details-social-counts__comments")]').text
                except:
                    comments = "0"

                # Append post details to the list
                latest_feed.append({
                    "content": content,
                    "likes": likes,
                    "comments": comments
                })

            except Exception as e:
                print(f"Error scraping a post: {e}")
        
        return latest_feed

    finally:
        # Quit the driver and clean up resources
        if driver:
            driver.quit()
            driver = None

def remove_non_latin_characters(text):
    """Remove non-latin characters (e.g., emojis) from the text."""
    return re.sub(r'[^\x00-\x7F]+', '', text)

def generate_pdf(posts, filename="linkedin_posts_report.pdf"):
    """Generate a PDF report with the scraped posts as simple text."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="LinkedIn Post Scraping Report", ln=True, align='C')
    pdf.ln(10)

    # Add post data to the PDF
    pdf.set_font('Arial', '', 12)
    for post in posts:
        # Remove non-latin characters from the content
        clean_content = remove_non_latin_characters(post["content"])

        # Add content, likes, and comments as plain text (no table)
        pdf.multi_cell(0, 10, f"Content: {clean_content}\nLikes: {post['likes']}\nComments: {post['comments']}\n\n")
    
    # Save the PDF
    pdf.output(filename)
    print(f"PDF report generated: {filename}")

if __name__ == "__main__":
    print("Scraping the latest LinkedIn feed...")
    feed_posts = scrape_latest_feed(EMAIL, PASSWORD)

    if feed_posts:
        # Save the scraped posts to a PDF file
        generate_pdf(feed_posts)

        print("Scraped posts saved to linkedin_posts_report.pdf")
    else:
        print("No posts found.")
