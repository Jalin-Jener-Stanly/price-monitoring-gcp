# Price Collection Project

## Description

This project is an automated **price monitoring and ranking system** that collects product prices from multiple online sources, calculates daily price rankings, detects ranking changes, and triggers automated email alerts.

The system was developed as a **academic group assignment**, where individual modules were implemented separately for clarity and then integrated into a final end-to-end pipeline.

---

## System Functionality

### Task 1 & Task 2 — Data Collection (Web Scraping)

* Collect product price data from multiple online sources (Amazon, eBay, Idealo)
* Extract and structure product, seller, and price information
* Final implementation is included in:

  ```
  ebay_amazon_idealo_collection (task 1 and 2).py
  ```
* Integrated into final pipeline via `main.py`

---

### Task 3 — Price Ranking and Visualization

* Computes daily average prices
* Ranks sellers based on lowest price
* Uses structured CSV dataset for stable evaluation
* Generates plots with change in ranks

---

### Task 4 — Email Alert System

* Detects ranking changes between time periods
* Sends automated email notifications when changes occur

> For demonstration purposes, Tasks 3 and 4 use a static dataset (`PRICE.csv`) to ensure reproducible and consistent results.

---

### Task 5 — Deployment (Cloud Integration)

* System deployed using Google Cloud Platform
* Uses Cloud Run and Cloud Scheduler
* Automates execution of price tracking pipeline
* Detects market shifts and triggers alerts based on ranking changes

---

## Data Handling

The project uses **CSV-based storage** instead of a database for simplicity and reproducibility.

### Included Files:

* `PRICE.csv` → Stable dataset for Tasks 3 & 4
* `products.csv` → Product configuration input
* `final_clean.csv` → Output of integrated pipeline
* `settings.txt` → Configuration file (API keys, email settings, seller metadata)

---

## Technologies Used

* Python 3.x
* Pandas, NumPy
* Requests, BeautifulSoup (Web Scraping)
* SQLAlchemy (data handling)
* Matplotlib (visualization)
* SMTP (email automation)
* Google Cloud Platform (Cloud Run, Cloud Scheduler)

---

## Installation

Install dependencies:

```bash
pip install pandas matplotlib requests beautifulsoup4 sqlalchemy numpy
```

---

## Cloud Requirements

To run the deployed version:

* Google Cloud Project
* Cloud Run enabled
* Cloud Scheduler enabled
* Artifact Registry access

---

## Authors

* **Task 1:** Jayakrishnan Unnikrishnan
* **Task 2:** Aswin S
* **Task 3 & 4:** Ronal Thomas
* **Task 5 & Final Integration:** Jalin Jener Stanly

---

## Project Structure

```
Price-collection-app/
│── main.py                 # Core ETL + analytics pipeline
│── Dockerfile              # Container configuration
│── requirements.txt        # Python dependencies
│── settings.txt            # API keys (excluded from GitHub)
│── products.xlsx           # Product input data
│── urls.csv                # Amazon scraping input
│── ebay.csv                # eBay URLs
│── idealo_prices_extracted.csv
│── final_clean.db          # SQLite database
│── prices.pdf              # Generated reports
│── .gitignore
```

---

## Security Note

Sensitive files such as API keys and credentials are excluded using `.gitignore`:

* settings.txt
* .env
* database files
* generated outputs

---

## Final Remark

This project demonstrates a complete **data pipeline system including web scraping, ranking analytics, automation, and cloud deployment**, simulating a real-world pricing intelligence system.
