# linkedin-automate-comment

Welcome to the **LinkedIn Automate Comment** project! This tool combines web scraping, sentiment analysis, and natural language processing to automate meaningful LinkedIn interactions by generating and posting thoughtful comments.

---

## Table of Contents
- [Project Overview](#project-overview)
- [How It Works](#how-it-works)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview
The **LinkedIn Automate Comment** project simplifies professional networking by:
- Scraping LinkedIn posts from your feed.
- Performing sentiment analysis on posts and their comments.
- Generating short, context-aware, and meaningful comments using AI.
- Automating the posting of comments on LinkedIn.

This tool is ideal for professionals aiming to maintain an active LinkedIn presence with minimal manual effort.

---

## How It Works
1. **Scrape Posts:**
   - The `web_scrapper.py` script logs into LinkedIn, collects the latest posts, and saves them for analysis.

2. **Analyze Sentiment:**
   - The `anlyze.py` script uses the TextBlob library to assess the sentiment of posts and their associated comments.

3. **Generate Comments:**
   - The `llm.py` script uses Google Generative AI and FAISS to create concise, context-sensitive comments tailored to the tone of the post.

4. **Post Comments:**
   - The `test.py` script automates posting comments on LinkedIn using Selenium.

---

## Features
- **Web Scraping:** Efficiently scrape LinkedIn posts and metadata.
- **Sentiment Analysis:** Analyze the tone and sentiment of posts and their comments.
- **AI-Powered Commenting:** Generate short, impactful comments using state-of-the-art AI models.
- **Automation:** Automatically post comments with a headless browser.
- **PDF Reports:** Export reports of scraped posts and analysis as PDFs.

---

## Directory Structure
```
linkedin-automate-comment/
├── README.md                # Project documentation
├── web_scrapper.py          # Script to scrape LinkedIn posts
├── anlyze.py                # Sentiment analysis script
├── llm.py                   # AI-powered comment generation
├── test.py                  # Script to automate LinkedIn commenting
├── linkedin_posts.csv       # Sample CSV file for post data
```

---

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- Google API Key (for Generative AI integration)
- Chrome and ChromeDriver (compatible versions)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/hiteshydv001/linkedin-automate-comment.git
   cd linkedin-automate-comment
   ```

2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in a `.env` file:
   ```env
   EMAIL=your_email@example.com
   PASSWORD=your_password
   GOOGLE_API_KEY=your_google_api_key
   ```

4. Ensure Chrome and the appropriate version of ChromeDriver are installed.

---

## Usage

### Step 1: Scrape LinkedIn Posts
Run the scraper to collect posts from your LinkedIn feed:
```bash
python web_scrapper.py
```

### Step 2: Perform Sentiment Analysis
Analyze the sentiment of scraped posts and their comments:
```bash
python anlyze.py
```

### Step 3: Generate Comments
Create automated comments using the LLM:
```bash
python llm.py
```

### Step 4: Post Comments
Automate the commenting process on LinkedIn:
```bash
python test.py
```

---

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature description"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Enjoy automating your LinkedIn interactions with **LinkedIn Automate Comment**!
