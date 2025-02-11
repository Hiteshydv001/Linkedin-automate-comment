import os
import time
import random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from llm import generate_comment  # Import the function from llm.py

# Load environment variables
load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def automate_linkedin_comments(email, password):
    options = Options()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    try:
        # Step 1: Login to LinkedIn
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)

        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(5)

        # Step 2: Navigate to LinkedIn feed
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)

        # Scroll to load more posts
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        # Step 3: Find posts
        posts = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-shared-update')]")
        if not posts:
            print("No posts found.")
            return

        for idx, post in enumerate(posts[:5]):  # Limit to 5 posts
            try:
                post_content = post.text.strip()
                if not post_content:
                    print(f"Post {idx + 1}: Empty post. Skipping...")
                    continue

                # Generate AI-based comment
                comment_text = generate_comment(post_content)
                print(f"Generated Comment for Post {idx + 1}: {comment_text}")

            except Exception as e:
                print(f"Error processing Post {idx + 1}: {e}")
                continue

    finally:
        driver.quit()
        print("Automation complete.")

if __name__ == "__main__":
    print("Starting LinkedIn automation...")
    automate_linkedin_comments(EMAIL, PASSWORD)
