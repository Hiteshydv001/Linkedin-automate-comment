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
<<<<<<< HEAD
from fpdf import FPDF  # Import FPDF for PDF generation
from llm import generate_comment  # Import updated LLM function
=======
from llm import generate_comment  # Import AI comment generator
>>>>>>> main

# Load environment variables
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
<<<<<<< HEAD

# Load the environment variables explicitly from .env.local
env_path = "D:/JWoC 2k25/linkedin-automate-comment/.env.local"
load_dotenv(dotenv_path=env_path)




def filter_bmp_characters(text):
    """Filter out non-BMP characters to prevent Selenium errors."""
    return ''.join(char for char in text if ord(char) <= 0xFFFF)


def generate_pdf_report(results):
    """Generate a PDF report with results of LinkedIn comments."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="LinkedIn Comment Automation Report", ln=True, align='C')
    pdf.ln(10)

    # Set table headers
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, "Post Index", border=1, align='C')
    pdf.cell(100, 10, "Post Content", border=1, align='C')
    pdf.cell(50, 10, "Comment Status", border=1, align='C')
    pdf.ln()

    # Add results to PDF
    pdf.set_font('Arial', '', 12)
    for result in results:
        pdf.cell(40, 10, str(result['Post Index']), border=1, align='C')
        pdf.cell(100, 10, result['Post Content'], border=1, align='C')
        pdf.cell(50, 10, result['Comment Status'], border=1, align='C')
        pdf.ln()

    # Save the PDF
    pdf_output_path = "linkedin_comments_report.pdf"
    pdf.output(pdf_output_path)
    print(f"PDF report generated: {pdf_output_path}")


def scrape_linkedin_posts():
    """Scrape LinkedIn posts and return extracted text."""
    options = Options()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    try:
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        driver.find_element(By.ID, "username").send_keys(EMAIL)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(5)

        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)

        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        posts = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")
        extracted_texts = []

        for idx, post in enumerate(posts[:5]):  # Limit to first 5 posts
            try:
                post_content = post.text[:200]  # Extract first 200 characters
                if post_content:
                    extracted_texts.append(post_content)
            except Exception as e:
                print(f"Error extracting post {idx + 1}: {e}")
                continue

        return extracted_texts  # Returns a list of extracted LinkedIn post texts

    finally:
        driver.quit()


def automate_linkedin_comments():
=======

def automate_linkedin_comments(email, password):
>>>>>>> main
    options = Options()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    try:
        # **🔹 Login**
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)
<<<<<<< HEAD

        driver.find_element(By.ID, "username").send_keys(EMAIL)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
=======
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
>>>>>>> main
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(5)

        # **🔹 Navigate to feed**
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)

        for i in range(5):  # Process 5 posts
            try:
<<<<<<< HEAD
                # Get post content for reference
                post_content = post.text[:200]  # Extract first 200 characters for the report

                # Generate AI-based comment using RAG
                generated_comment = generate_comment(post_content)
=======
                # **🔹 Find all posts**
                posts = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")
                if len(posts) <= i:
                    print("⚠️ No more posts available.")
                    break
                
                post = posts[i]  # Take the i-th post
                
                # **🔹 Scroll post into view**
                driver.execute_script("arguments[0].scrollIntoView();", post)
                time.sleep(2)
>>>>>>> main

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
<<<<<<< HEAD

                # Filter BMP characters and inject comment using JavaScript
                filtered_comment_text = filter_bmp_characters(generated_comment)
                driver.execute_script("arguments[0].innerText = arguments[1];", comment_box, filtered_comment_text)
                driver.execute_script(
                    "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", comment_box
                )
=======
                driver.execute_script("arguments[0].innerText = arguments[1];", comment_box, comment_text)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", comment_box)
>>>>>>> main
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
<<<<<<< HEAD
    print("Starting LinkedIn automation...")
    automate_linkedin_comments()
=======
    print("🚀 Starting LinkedIn automation...")
    automate_linkedin_comments(EMAIL, PASSWORD)
>>>>>>> main
