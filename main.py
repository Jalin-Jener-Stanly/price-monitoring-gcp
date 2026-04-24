def main():
    import re
    from datetime import date
    import csv
    import time
    from datetime import datetime
    import requests
    from bs4 import BeautifulSoup
    from sqlalchemy import create_engine
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import smtplib #email reporting
    from email.message import EmailMessage #email reporting
    from pathlib import Path #email reporting
    import pandas as pd

    # =========================
    # TASK 1 ETL (EXTRACT, TRANSFORM, LOAD) FROM IDEALO.DE
    # =========================

    # Load API key from settings.txt
    settings = {}
    with open("settings.txt") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip()

    SERPAPI_KEY = settings["SERPAPI_KEY"]

    # Price cleaning: convert German price text to float
    def extract_price(text):
        if not text:
            return None
        match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})', text)
        if not match:
            return None
        price = match.group(1)
        price = price.replace(".", "").replace(",", ".")
        return float(price)

    # Load products from Excel
    df = pd.read_excel("products.xlsx")
    products = df[["Product name", "Idealo URL", "our company Price"]].dropna()
    print(f"Loaded {len(products)} products")

    rows = []
    today = date.today()
    # Extract and transform Idealo prices
    for _, row in products.iterrows():
        product_name = row["Product name"]
        our_price = float(row["our company Price"])
        print(f"\nExtracting Idealo data for: {product_name}")

        params = {
            "engine": "google",
            "q": f"site:idealo.de {product_name}",
            "hl": "de",
            "gl": "de",
            "api_key": SERPAPI_KEY
        }
        resp = requests.get("https://serpapi.com/search", params=params, timeout=30)

        if resp.status_code != 200:
            print("HTTP error:", resp.status_code)
            continue

        data = resp.json()
        idealo_price = None

        for result in data.get("organic_results", []):
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            if "idealo.de" in link and "€" in snippet:
                idealo_price = extract_price(snippet)
                break

        # Add Idealo price row
        if idealo_price is not None:
            rows.append({
                "Product": product_name,
                "Date": today,
                "Seller": "Idealo marketplace",
                "Price": idealo_price
            })
            print(f"Idealo price: {idealo_price}")
        else:
            print("Idealo price not found")

        # Add our company price row
        rows.append({
            "Product": product_name,
            "Date": today,
            "Seller": "Our company",
            "Price": our_price
        })
        print(f"Our company price: {our_price}")
        time.sleep(1)

    # Save extracted data to CSV
    out_df = pd.DataFrame(rows)
    out_df.to_csv("idealo_prices_extracted.csv", index=False, encoding="utf-8")
    print("\nTask 1 completed: idealo_prices_extracted.csv created")

    # Replace 'your_file.csv' with the path to your CSV file
    file_extract = 'idealo_prices_extracted.csv'

    # Read CSV into a DataFrame
    idealo_df = pd.read_csv(file_extract)

    # view the first few rows
    print(idealo_df)

    # =========================
    # TASK 2 ETL FROM EBAY.DE AND AMAZON.DE
    # =========================

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,ml;q=0.7"
    }

    #Amazon
    # scraping function
    def scrape(url):
        #Send HTTP Request (Download Webpage HTML)
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
    #Extract Product Title
        product_title = soup.find("span", {"id": "productTitle"})
        product_title = product_title.get_text(strip=True) if product_title else "N/A"
    #Extract Seller Name
        seller = soup.find("a", {"id": "sellerProfileTriggerId"})
        seller = seller.get_text(strip=True) if seller else "N/A"
    #Extract Product Price
        product_price = soup.find("span", {"class": "aok-offscreen"})
        product_price = product_price.get_text(strip=True) if product_price else "Sold Out"
    #Return a Structured Record
        return {
            "Product": product_title,
            "Seller": seller,
            "Price": product_price
        }
    #Main Function (Read URLs, Scrape All, Build DataFrame)
    def main():
        #List to Store All Scraped Records
        data = []
        #Read URLs from CSV File
        with open("urls.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            #Loop Through Each URL and Scrape
            for row in reader:
                data.append(scrape(row["urls"]))
    #Convert List of Dictionaries into a Pandas DataFrame
        df = pd.DataFrame(data)
        return df

    amz_df = main()
    print(amz_df)


    #E-bay
    # Load CSV
    df = pd.read_csv("ebay.csv")
    results = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    for i, row in df.iterrows():
        url = row["Ebay URL"]
        print(f"\n Scraping {i+1}/{len(df)}")
        try:
            r = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            #Title
            title_tag = soup.find("h1", class_="x-item-title__mainTitle")
            title = title_tag.text.strip() if title_tag else "N/A"
            # Price
            price_tag = soup.select_one("div.x-price-primary span")
            price = price_tag.text.strip() if price_tag else "Sold Out"
            # Seller
            seller_tag = soup.select_one("span.ux-textspans ux-textspans--BOLD")
            seller = seller_tag.text.strip() if seller_tag else "Ebay"
            print("✔ Product:", title)
            print("✔ Price  :", price)
            print("✔ Seller :", seller)

            results.append({
                "Product": title,
                "Seller": seller,
                "Price": price,
            })
            time.sleep(2)
        except Exception as e:
            print(" Error:", e)

    # Save output
    ebay_df = pd.DataFrame(results)
    print(ebay_df)

    task2_df = pd.concat([amz_df, ebay_df], ignore_index=True)
    print(task2_df)

    # Drop existing Date column if it exists
    if 'Date' in task2_df.columns:
        task2_df = task2_df.drop(columns=['Date'])
    # Insert Date as second column
    task2_df.insert(1, 'Date', datetime.today().strftime('%Y-%m-%d'))
    print(task2_df)

    #Combining Tasks 1&2
    final_clean_df = pd.concat([task2_df, idealo_df], ignore_index=True)
    print(final_clean_df)
    # Save final_clean_df to CSV
    final_clean_df.to_csv('final_clean.csv', index=False, encoding='utf-8')

    # Step 1: Add Product ID as the first column
    final_clean_df.insert(0, 'Product_ID', range(1, len(final_clean_df) + 1))
    # Step 2: Create SQLite database file
    engine = create_engine('sqlite:///final_clean.db')
    # Step 3: Save DataFrame to SQL table
    table_name = 'products'
    final_clean_df.to_sql(table_name, con=engine, if_exists='replace', index=False)

    print(f" final_clean_df has been saved as SQL table '{table_name}' in 'final_clean.db'")

    # =========================
    # TASK 3 VISUALIZATION
    # =========================

    ##Email Reporting Logic##
    SETTINGS_PATH = "settings.txt"
    def read_settings(path: str) -> dict:
        s = {}
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            s[k.strip()] = v.strip()
        return s

    def send_email(settings: dict, subject: str, body: str) -> None:
        host = settings["smtp_host"]
        port = int(settings.get("smtp_port", "587"))
        user = settings["smtp_user"]
        pw = settings["smtp_pass"]
        recipients = [x.strip() for x in settings["recipients"].split(",") if x.strip()]
        msg = EmailMessage()
        msg["From"] = user
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, pw)
            server.send_message(msg)

    def build_rank_change_body(changes_df: pd.DataFrame) -> str:
        lines = ["Rank change detected:", ""]
        for _, r in changes_df.iterrows():
            lines.append(
                f"- {r['Product']}: {r['PreviousRank']} (on {r['PreviousDate']}) -> "
                f"{r['CurrentRank']} (on {r['CurrentDate']})"
            )
        lines.append("")
        lines.append("Automated notification (Task 4).")
        return "\n".join(lines)
    ##Email Reporting Logic##

    # Use the dataframe already in memory from Task 2
    df = final_clean_df.copy()

    # --- Clean Price column ---
    df["Price"] = (
        df["Price"]
        .astype(str)
        .str.replace("€", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )

    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    # --- Clean Date column ---
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

    # --- Drop invalid rows ---
    df = df.dropna(subset=["Price", "Date"])

    # --- Sanity checks ---
    print(df.head(28))
    print(df.dtypes)
    print(df.columns)
    print(df["Seller"].unique()) #verify the name of our firm "our company"

    # --- Simulate dates from Jan 6 to Jan 26 ---
    date_range = pd.date_range(start="2026-01-06", end="2026-01-26").date

    df = pd.concat(
        [df.assign(Date=d) for d in date_range],
        ignore_index=True
    )

    # Verify
    print("Unique dates after simulation:", df["Date"].nunique())
    print(df["Date"].drop_duplicates().head())
    print(df["Date"].drop_duplicates().tail())
    unique_dates = df["Date"].drop_duplicates().reset_index(drop=True)
    print(unique_dates)

    # Small deterministic daily variation for visualization
    df["day_index"] = (
        df["Date"] - df["Date"].min()
    ).apply(lambda x: x.days)

    df["Price"] = df["Price"] * (1 + 0.002 * df["day_index"])

    # Rounding the prices so it looks clean
    df["Price"] = df["Price"].round(2)

    # FORCE RANK CHANGE####Email Reporting##
    # ===============================
    latest_date = df["Date"].max()
    mask = (df["Date"] == latest_date) & (df["Seller"] == "Our company")
    df.loc[mask, "Price"] = (df.loc[mask, "Price"] * 0.85).round(2)
    print("DEMO: forced lower our price on latest date to trigger rank change.")
    # Email Reporting##===============================##Email Reporting

    # --- Identify our company ---
    OUR_SELLER = "Our company" # we are defining who our comapny is,  to treat our company separately from the competitiors

    #SPLIT COMPETITORS vs OUR COMPANY (splitting the data frame)
    market_df = df[df["Seller"] != OUR_SELLER] #filters the data frame, keeps all rows where the seller is not "our company"
    our_df = df[df["Seller"] == OUR_SELLER] #keeps only your company’s rows eg: date and price and drops unnecessary colums like id and product seller

    # --- Quick check ---
    print("Market sellers:", market_df["Seller"].unique())
    print("Our seller:", our_df["Seller"].unique())

    # Step 3: Minimum market price per date (competitors only)
    min_market = (
        market_df
        .groupby("Date")["Price"]
        .min()
        .reset_index(name="min_market_price")
    )

    print(min_market.head(28))

    # Step 4: Our company price per date
    our_price = (
        our_df
        .groupby("Date")["Price"]
        .mean()
        .round(2)
        .reset_index(name="our_price")
    )

    print(our_price.head(28))

    # Step 5: Merge min market price with our company price (why we do this???)
    plot1_df = (
        min_market
        .merge(our_price, on="Date", how="inner")
        .sort_values("Date")
    )

    print(plot1_df.head(10))

    #Step 6 PLOTTING THE CHARTS
    # Step 6: Plot 1 - Minimum Market Price vs Our Price
    plt.figure(figsize=(10, 5))

    plt.plot(
        plot1_df["Date"],
        plot1_df["min_market_price"],
        label="Minimum Market Price"
    )

    plt.plot(
        plot1_df["Date"],
        plot1_df["our_price"],
        label="Our Price"
    )

    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("Minimum Market Price vs Our Price Over Time")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Step 7: Average market price per date (competitors only)
    avg_market = (
        market_df
        .groupby("Date")["Price"]
        .mean()
        .round(2)
        .reset_index(name="avg_market_price")
    )

    print(avg_market.head(10))

    # Step 8: Merge avg market price with our company price
    plot2_df = (
        avg_market
        .merge(our_price, on="Date", how="inner")
        .sort_values("Date")
    )

    print(plot2_df.head(10))

    # Step 9: Plot 2 - Average Market Price vs Our Price
    plt.figure(figsize=(10, 5))

    plt.plot(
        plot2_df["Date"],
        plot2_df["avg_market_price"],
        label="Average Market Price"
    )

    plt.plot(
        plot2_df["Date"],
        plot2_df["our_price"],
        label="Our Price"
    )

    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("Average Market Price vs Our Price Over Time")
    plt.legend()
    plt.tight_layout()
    plt.show()

                            #Step 3- Plot our price rank over time
    #To create a rank table
    # Step 10 : Our rank per date (1 = cheapest)

    # 1) Ensure one price per seller per date (removes duplicates created by date simulation)
    seller_daily = (
        df.groupby(["Date", "Seller"], as_index=False)["Price"]
          .mean()
    )

    # 2) Rank sellers within each date by price (lowest price = rank 1)
    seller_daily["rank"] = (
        seller_daily.groupby("Date")["Price"]
                   .rank(method="min", ascending=True)
    )

    # 3) Keep only our company rank per date
    rank_df = (
        seller_daily[seller_daily["Seller"] == OUR_SELLER][["Date", "rank"]]
          .rename(columns={"rank": "our_rank"})
          .sort_values("Date")
    )

    # =========================
    # TASK 4 (Email) - Rank change detection (Product + Date)
    # =========================

    settings = read_settings(SETTINGS_PATH)
    OUR_SELLER = settings.get("our_seller", OUR_SELLER)  # keep your existing OUR_SELLER unless settings overrides it

    # 1) Ensure one price per Product+Date+Seller (handles duplicates)
    daily = (
        df.groupby(["Product", "Date", "Seller"], as_index=False)["Price"]
          .mean()
    )

    # 2) Rank sellers within each Product+Date by price (1 = cheapest)
    daily["rank"] = (
        daily.groupby(["Product", "Date"])["Price"]
             .rank(method="min", ascending=True)
             .astype(int)
    )

    # 3) Keep only our company's rank rows
    our_rank = daily[daily["Seller"] == OUR_SELLER][["Product", "Date", "rank"]].sort_values(["Product", "Date"])

    # 4) Detect rank changes between last two dates for each product
    changes = []
    for product, g in our_rank.groupby("Product"):
        g = g.sort_values("Date")
        if len(g) < 2:
            continue
        prev = g.iloc[-2]
        curr = g.iloc[-1]
        if int(prev["rank"]) != int(curr["rank"]):
            changes.append({
                "Product": product,
                "PreviousDate": prev["Date"],
                "PreviousRank": int(prev["rank"]),
                "CurrentDate": curr["Date"],
                "CurrentRank": int(curr["rank"]),
            })

    changes_df = pd.DataFrame(changes)

    # 5) Send email only if there are changes
    if changes_df.empty:
        print("Task 4: No rank changes detected. No email sent.")
    else:
        body = build_rank_change_body(changes_df)
        print(body)
        send_email(settings, "Rank Change Alert", body)
        print("Task 4: Email sent.")
    ##########Email Reporting Logic##########

    #make rank an int for display
    rank_df["our_rank"] = rank_df["our_rank"].astype(int)

    print(rank_df.head(10))

    # Step 11: Plot 3 - Rank over time
    plt.figure(figsize=(10, 5))
    plt.plot(rank_df["Date"], rank_df["our_rank"], label="Our rank")

    plt.xlabel("Date")
    plt.ylabel("Rank (1 = cheapest)")
    plt.title("Our Price Rank Over Time")
    plt.legend()
    plt.tight_layout()
    plt.show()

                            #Export all 3 plots into ONE PDF

    pdf_name = "prices.pdf"

    with PdfPages(pdf_name) as pdf:

        # --- Plot 1 ---
        plt.figure(figsize=(10, 5))
        plt.plot(plot1_df["Date"], plot1_df["min_market_price"], label="Min price")
        plt.plot(plot1_df["Date"], plot1_df["our_price"], label="Our price")
        plt.xlabel("Date"); plt.ylabel("Price")
        plt.title("Minimal Price vs Our Price")
        plt.legend(); plt.tight_layout()
        pdf.savefig(); plt.close()

        # --- Plot 2 ---
        plt.figure(figsize=(10, 5))
        plt.plot(plot2_df["Date"], plot2_df["avg_market_price"], label="Average price")
        plt.plot(plot2_df["Date"], plot2_df["our_price"], label="Our price")
        plt.xlabel("Date"); plt.ylabel("Price")
        plt.title("Average Price vs Our Price")
        plt.legend(); plt.tight_layout()
        pdf.savefig(); plt.close()

        # --- Plot 3 ---
        plt.figure(figsize=(10, 5))
        plt.plot(rank_df["Date"], rank_df["our_rank"], label="Our rank")
        plt.xlabel("Date"); plt.ylabel("Rank (1=cheapest)")
        plt.title("Our Rank Over Time")
        plt.legend(); plt.tight_layout()
        pdf.savefig(); plt.close()

    print("Saved:", pdf_name)
    pass

if __name__ == "__main__":
    main()