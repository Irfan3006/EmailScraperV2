# Email Scraper V2

![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?style=for-the-badge&logo=flask)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-4.1-38bdf8?style=for-the-badge&logo=tailwindcss)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

> **A lightweight, web-based OSINT reconnaissance tool designed for deep-web crawling and email address enumeration.**

## 📜 Description

**Email Scraper** is a specialized web spider developed to automate the process of email harvesting during the *Reconnaissance* phase of a penetration test. Built with **Flask** and **Server-Sent Events (SSE)**, it delivers real-time feedback directly to a cyberpunk-styled terminal interface.

Unlike standard scrapers, Email Scraper features intelligent spidering capabilities that recursively crawl internal links while respecting domain boundaries, allowing for deep discovery of contact vectors.

## ⚡ Features

* **🕵️ Real-time Enumeration:** Utilizes Server-Sent Events (SSE) to stream crawl results instantly without page reloads.
* **🕷️ Recursive Spidering:** Intelligent crawling logic that navigates through internal links up to a user-defined depth.
* **🛡️ Evasion Techniques:** Implements User-Agent rotation and random delays to mimic human behavior and avoid basic bot detection (WAFs).
* **📂 Data Exfiltration:** Auto-collects unique emails and provides an instant `.txt` dump for reporting.
* **💻 Cyberpunk UI:** A fully responsive, hacker-style interface built with Tailwind CSS, featuring terminal logs and scanline aesthetics.

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask, BeautifulSoup4, Requests
* **Frontend:** HTML5, Tailwind CSS (CDN), Vanilla JavaScript
* **Protocol:** HTTP/1.1 (Chunked Transfer Encoding for streaming)


## ⚠️ Legal Disclaimer
PLEASE READ CAREFULLY:

* This tool is developed for Educational Purposes and Authorized Ethical Hacking only. The author is not responsible for any misuse of this tool.
* Do not use this tool on websites you do not own or do not have explicit permission to test.
* Unauthorized scraping or data collection may violate the Terms of Service (ToS) of the target website and local cyber laws (such as UU ITE in Indonesia or CFAA in the USA).
* Always practice Responsible Disclosure.