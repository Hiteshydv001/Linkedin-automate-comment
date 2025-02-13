import os
import time
import random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from llm import generate_comment  # Import AI comment generator

# Load environment variables
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def automate_linkedin_comments(email, password):
    options = Options()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    try:
        # **🔹 Login**
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(5)

        # **🔹 Navigate to feed**
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)

        for i in range(5):  # Process 5 posts
            try:
                # **🔹 Find all posts**
                posts = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")
                if len(posts) <= i:
                    print("⚠️ No more posts available.")
                    break
                
                post = posts[i]  # Take the i-th post
                
                # **🔹 Scroll post into view**
                driver.execute_script("arguments[0].scrollIntoView();", post)
                time.sleep(2)

                # **🔹 Extract Post Content**
                post_content = post.text[:300]  # First 300 characters
                print(f"\n📌 Processing Post {i+1}:\n{post_content[:100]}...")  # Show a preview

                # **🔹 Generate AI comment**
                print("⏳ Sending post content to LLM API...")
                comment_text = generate_comment(post_content)
                time.sleep(random.uniform(5, 10))  # Simulate LLM processing time

                if not comment_text or comment_text.strip() in ["👍", "Nice!", "Great post!"]:
                    print("⚠️ Skipping post (no meaningful comment generated).")
                    continue

                print(f"✅ AI Generated Comment: {comment_text}")

                # **🔹 Open Comment Section**
                try:
                    comment_button = post.find_element(By.XPATH, './/button[contains(@aria-label, "Comment")]')
                    driver.execute_script("arguments[0].click();", comment_button)
                    time.sleep(3)
                except:
                    print("⚠️ No comment button found. Skipping...")
                    continue

                # **🔹 Enter Comment**
                comment_box = post.find_element(By.XPATH, './/div[contains(@role, "textbox")]')
                driver.execute_script("arguments[0].innerText = arguments[1];", comment_box, comment_text)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", comment_box)
                time.sleep(2)

                # **🔹 Click Post Button**
                try:
                    post_button = WebDriverWait(post, 10).until(
                        EC.element_to_be_clickable((By.XPATH, './/button[contains(@class, "comments-comment-box__submit-button--cr")]'))
                    )
                    driver.execute_script("arguments[0].click();", post_button)
                    time.sleep(random.uniform(2, 4))
                    print("✅ Comment Posted Successfully!")
                except:
                    print("⚠️ Failed to post comment.")

                # **🔹 Scroll to Next Post Properly**
                print("🔽 Scrolling to next post...")
                ActionChains(driver).move_to_element(posts[i]).perform()  # Move to next post
                driver.execute_script("window.scrollBy(0, 700);")  # Scroll smoothly down
                time.sleep(3)

            except Exception as e:
                print(f"❌ Error processing post: {e}")

    finally:
        driver.quit()
        print("✅ Automation Completed.")

if __name__ == "__main__":
    print("🚀 Starting LinkedIn automation...")
    automate_linkedin_comments(EMAIL, PASSWORD)
