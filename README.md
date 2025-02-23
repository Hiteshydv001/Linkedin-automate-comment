# 🚀 LinkedIn Automate Comment

Welcome to **LinkedIn Automate Comment**! This project leverages **web scraping, sentiment analysis, and AI-driven text generation** to automate meaningful LinkedIn interactions. 🎯

## Table of Contents
- [Project Overview](#project-overview)
- [Featured In](#featured-in)
- [How It Works](#how-it-works)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview
💡 **LinkedIn Automate Comment** simplifies professional networking by:
- ✅ Scraping LinkedIn posts from your feed.
- ✅ Performing sentiment analysis on posts and comments.
- ✅ Generating AI-powered, context-aware comments.
- ✅ Automating the posting of comments on LinkedIn.

Ideal for professionals who want to stay active on LinkedIn with **minimal effort!** 🚀

---

## Featured In

<div align="center">

<table>
   <tr>
      <td><img src="https://media.licdn.com/dms/image/v2/C560BAQEp7MUBpYE93g/company-logo_200_200/company-logo_200_200/0/1630672259441/jwoc_logo?e=2147483647&v=beta&t=wgkKrzLc-UxgSCnWShwkjn_zTXQnaa0_4cmbv4fN4PA" width="600" height="auto" loading="lazy" alt="jgec"/></td>
      <td>JWOC Winter of Code</td>
      <td>JWoC provides a fully immersive learning experience for students and first-time contributors by promoting the wonders of open-source software and crafting a community of new and experienced technical developers. The best projects are selected for this program. Students get acquainted with the projects from the mentors during the Community Bonding Period. Students work on these projects during the coding phase. At the end of the coding period, the winners of the programs are announced on the basis of their contribution in terms of quantity as well as quality.</td>
   </tr>
</table>

</div>

---

## How It Works 🛠️
1️⃣ **Scrape Posts:** `web_scrapper.py` logs into LinkedIn and collects posts.
2️⃣ **Analyze Sentiment:** `analyze.py` determines the tone of posts/comments.
3️⃣ **Generate Comments:** `llm.py` creates AI-powered, relevant responses.
4️⃣ **Post Comments:** `test.py` automates comment posting via Selenium.

---

## Features ✨
🎯 **Web Scraping:** Extracts LinkedIn posts efficiently.
📊 **Sentiment Analysis:** Evaluates post/comment tone.
🤖 **AI-Powered Comments:** Generates concise, relevant responses.
⚡ **Automation:** Uses a headless browser to post comments.
📄 **PDF Reports:** Exports insights as downloadable PDFs.

---

## Directory Structure 📁
```plaintext
Directory structure:
└── hiteshydv001-linkedin-automate-comment/
    ├── README.md
    ├── anlyze.py
    ├── contribution.md
    ├── linkedin_posts.csv
    ├── llm.py
    ├── main.py
    ├── requirements.txt
    ├── service.json
    ├── web_scrapper.py
    ├── .env.local
    ├── JWoC/
    │   └── Readme.md
    ├── agents/
    │   ├── __init__.py
    │   ├── agent_base.py
    │   ├── generate_comment_agent.py
    │   ├── refiner_agent.py
    │   ├── sanitize_data_tool.py
    │   ├── sanitize_data_validator_agent.py
    │   ├── sentiment_analysis_agent.py
    │   ├── summarize_tool.py
    │   ├── summarize_validator_agent.py
    │   ├── validator_agent.py
    │   ├── write_post_tool.py
    │   └── write_post_validator_agent.py
    ├── frontend/
    │   ├── README.md
    │   ├── components.json
    │   ├── eslint.config.mjs
    │   ├── next.config.ts
    │   ├── package-lock.json
    │   ├── package.json
    │   ├── postcss.config.mjs
    │   ├── tailwind.config.ts
    │   ├── tsconfig.json
    │   ├── .gitignore
    │   ├── public/
    │   │   └── linkedin-automation-icon.avif
    │   └── src/
    │       ├── app/
    │       │   ├── globals.css
    │       │   ├── layout.tsx
    │       │   ├── page.tsx
    │       │   ├── generate_comments/
    │       │   │   └── page.tsx
    │       │   ├── sentiment_analysis/
    │       │   │   └── page.tsx
    │       │   ├── summarize/
    │       │   │   └── page.tsx
    │       │   └── write_post/
    │       │       └── page.tsx
    │       ├── components/
    │       │   ├── main-nav.tsx
    │       │   ├── theme-provider.tsx
    │       │   └── ui/
    │       │       ├── button.tsx
    │       │       ├── card.tsx
    │       │       ├── dialog.tsx
    │       │       ├── dropdown-menu.tsx
    │       │       ├── form.tsx
    │       │       ├── input.tsx
    │       │       ├── label.tsx
    │       │       ├── select.tsx
    │       │       ├── tabs.tsx
    │       │       ├── textarea.tsx
    │       │       ├── toast.tsx
    │       │       └── toaster.tsx
    │       ├── hooks/
    │       │   └── use-toast.ts
    │       └── lib/
    │           └── utils.ts
    └── .github/
        ├── dependabot.yml
        └── workflows/
            └── codeql.yml

```

---

## Setup and Installation 📦

### Prerequisites
- 🐍 Python 3.8+
- 🔑 Google API Key (for Generative AI)
- 🌍 Chrome & ChromeDriver (ensure compatibility)

### Installation Steps
1️⃣ Clone the repository:
   ```bash
   git clone https://github.com/hiteshydv001/linkedin-automate-comment.git
   cd linkedin-automate-comment
   ```
2️⃣ Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3️⃣ Configure environment variables in a `.env` file:
   ```env
   EMAIL=your_email@example.com
   PASSWORD=your_password
   GOOGLE_API_KEY=your_google_api_key
   ```
4️⃣ Ensure Chrome & ChromeDriver are installed.

---

## Usage 🏁

### Step 1: Scrape LinkedIn Posts
```bash
python web_scrapper.py
```
### Step 2: Perform Sentiment Analysis
```bash
python analyze.py
```
### Step 3: Generate Comments
```bash
python llm.py
```
### Step 4: Post Comments
```bash
python test.py
```

---

## Contributing 🌟
🎯 Contributions are **welcome!** Follow these steps:
1. **Fork** the repository.
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
5. Open a **pull request**. 🚀

---

## License ⚖️
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

🎉 **Enjoy automating your LinkedIn interactions with** `LinkedIn Automate Comment`! 🚀



## 📜 **Contributing Guide for specific purposes and competitons** ⚖️
----
Please refer to our 
* [contribution.md](https://github.com/Hiteshydv001/Linkedin-automate-comment/blob/main/contribution.md) for general open source contribution
* [JWoC guide](https://github.com/Hiteshydv001/Linkedin-automate-comment/blob/main/JWoC/Readme.md) for contribution under JGEC Winter of Code
