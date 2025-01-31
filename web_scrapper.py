import os
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select  # Import Select class for handling <select> elements

def generate_username(first_name, last_name):
    """Generate a valid username by combining first name, last name, and a random number."""
    # Combine first and last names, make lowercase, and remove any spaces
    base_username = f"{first_name.lower()}{last_name.lower()}"
    
    # Add a random number at the end to ensure uniqueness
    random_number = random.randint(100000, 999999)
    username = f"{base_username}{random_number}"
    
    return username

def generate_password(length=12):
    """Generate a random password of a given length."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def create_google_account():
    """Automates the creation of a Google account."""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
    
    # Use undetected_chromedriver to bypass simple bot detection
    driver = webdriver.Chrome(options=options)

    try:
        # Open Google page
        driver.get("https://accounts.google.com/")

        # Wait for the "Create account" button and click it
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Create account')]"))).click()
        print("Navigating to the Create Account page...")

        time.sleep(2)  # Give time for the next page to load

        # Click on the "For my personal use" button
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'For my personal use')]"))).click()
        print("Clicked on 'For my personal use'")

        time.sleep(2)  # Give time for the next page to load

        # Automate entering account details (First and Last name)
        first_name = "John"
        last_name = "Doe"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "firstName"))).send_keys(first_name)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "lastName"))).send_keys(last_name)
        
        # Click next after entering name
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]"))).click()

        time.sleep(2)  # Wait for the next page

        # Fill in the birthday, gender, and other details

        # Select month
        month_select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "month")))
        select_month = Select(month_select)
        select_month.select_by_value("1")  # Select "January" (value "1")
        
        # Fill in the day
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "day"))).send_keys("1")

        # Fill in the year
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "year"))).send_keys("1990")

        # Select gender
        gender_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gender")))
        gender_dropdown.click()  # Click dropdown
        time.sleep(1)
        gender_dropdown.find_element(By.XPATH, "//option[contains(text(),'Male')]").click()  # Select "Male" from dropdown
        
        # Click Next to proceed to the next step
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]"))).click()
        print("Clicked 'Next' after filling birthday, gender, and other details")

        time.sleep(5)  # Give time for the next page to load (where you will enter username)

        # Generate a valid username
        username = generate_username(first_name, last_name)
        print(f"Generated username: {username}")

        # Now fill in the username
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Username")))
        username_input.send_keys(username)  # Enter the generated username

        # Click Next to proceed to the next step
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]"))).click()
        print("Entered username and clicked 'Next'.")

        time.sleep(5)  # Give time for the next page to load (where you will enter the password)

        # Generate a strong password
        password = generate_password()
        print(f"Generated password: {password}")

        # Enter the password
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Passwd")))
        password_input.send_keys(password)
        print("Entered password.",password)
        time.sleep(10)

        # Enter the confirmed password
        
        confirm_password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "PasswdAgain")))  # Correct field name for confirm password
        print("Found confirm password input field.", confirm_password_input)
        confirm_password_input.send_keys(password)

        # Click Next to proceed to the next step
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]"))).click()
        print("Entered password and confirmed it, then clicked 'Next'.")

        time.sleep(5)  # Wait for the next page (where recovery information is entered)

    finally:
        driver.quit()

if __name__ == "__main__":
    create_google_account()
