import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def scrape_linkedin_posts(email, password):
    """
    Logs into LinkedIn, scrapes the latest feed posts, and returns their text.

    Args:
        email (str): LinkedIn email/username.
        password (str): LinkedIn password.

    Returns:
        list: A list containing scraped LinkedIn post texts.
    """

    options = Options()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    posts_data = []  # Store extracted post content

    try:
        print("Logging into LinkedIn...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        
        # Enter login credentials
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(5)

        print("Navigating to LinkedIn feed...")
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)

        # Scroll to load more posts
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        # Find all posts
        posts = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")
        if not posts:
            print("No posts found.")
            return []

        print(f"Found {len(posts)} posts. Extracting content...")

        for idx, post in enumerate(posts[:5]):  # Limit to 5 posts
            try:
                post_content = post.text.strip()[:500]  # Extract and limit to 500 characters
                if not post_content:
                    continue  # Skip empty posts
                
                print(f"Post {idx + 1} Extracted: {post_content[:100]}...")  # Show first 100 chars
                posts_data.append(post_content)  # Store post text
                
            except NoSuchElementException:
                print(f"Error processing Post {idx + 1}: Element not found")
            except Exception as e:
                print(f"Error processing Post {idx + 1}: {e}")

    finally:
        driver.quit()

    return posts_data  # Return extracted LinkedIn posts

# For standalone testing
if __name__ == "__main__":
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")

    if not EMAIL or not PASSWORD:
        print("Error: EMAIL and PASSWORD environment variables are not set.")
    else:
        posts = scrape_linkedin_posts(EMAIL, PASSWORD)
        print("\nExtracted Posts:")
        for idx, post in enumerate(posts):
            print(f"Post {idx + 1}: {post}\n")
