import requests

# Sample post content for testing
post_content = """I found this crazy report called the India Salary Guide 2023.

86% of all respondents across every industry, age group, market and seniority level are planning to switch jobs.

38% of all current employees have not worked in their current role for more than 2 years.

This report issued by Michael Page has the full range of minimum, average and maximum salaries across functions and types of companies in:

Finance, Engineering, Manufacturing, Accounting, Healthcare, HR, Legal, Compliance, Procurement, Construction, Sales & Marketing - all across various industries and positions varying by seniority.

If you’re looking to switch, this is a phenomenal guide for you to get a sense of where the employee market is at.

Though one disclaimer - this report was published in the beginning of the year. A lot has changed with the startups of the country in layoffs since then. So take that into account, but this is great data to have.

hashtag#casarthakahuja hashtag#salaries hashtag#employees hashtag#hr hashtag#business"""

# Base URL of the FastAPI application
base_url = "http://127.0.0.1:8000"

# Test /summarize endpoint
def test_summarize():
    response = requests.post(f"{base_url}/summarize", json={"text": post_content})
    print("Summarize Endpoint Response:")
    print(response.json())

# Test /write_post endpoint
def test_write_post():
    response = requests.post(f"{base_url}/write_post", json={"topic": "Android Dvelopment for beginners", "outline": "This is a beginner-friendly guide to Android development."})
    print("Write Post Endpoint Response:")
    print(response.json())

# Test /sanitize_data endpoint
def test_sanitize_data():
    response = requests.post(f"{base_url}/sanitize_data", json={"data": post_content})
    print("Sanitize Data Endpoint Response:")
    print(response.json())

# Test /refine_post endpoint
def test_refine_post():
    response = requests.post(f"{base_url}/refine_post", json={"draft": post_content})
    print("Refine Post Endpoint Response:")
    print(response.json())

# Test /validate_post endpoint
def test_validate_post():
    response = requests.post(f"{base_url}/validate_post", json={"topic": "Your topic", "article": post_content})
    print("Validate Post Endpoint Response:")
    print(response.json())

# Test /generate_comment endpoint
def test_generate_comment():
    response = requests.post(f"{base_url}/generate_comment", json={"post_content": post_content})
    print("Generate Comment Endpoint Response:")
    print(response.json())

# Test /sentiment_analysis endpoint
def test_sentiment_analysis():
    response = requests.post(f"{base_url}/sentiment_analysis", json={"text": post_content})
    print("Sentiment Analysis Endpoint Response:")
    print(response.json())

# Run all tests
if __name__ == "__main__":
    test_summarize()
    test_write_post()
    test_sanitize_data()
    test_refine_post()
    test_validate_post()
    test_generate_comment()
    test_sentiment_analysis()