import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Set up Selenium WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Grant websites
grant_websites = {
    "Grants.gov": "https://www.grants.gov/search-grants.html",
    "Bank of America Charitable Foundation": "https://about.bankofamerica.com/en/making-an-impact/local-grants",
    "Wells Fargo Foundation": "https://www.wellsfargo.com/about/corporate-responsibility/community-giving/",
    "Candid's Foundation Directory": "https://candid.org/find-funding"
}

# Keywords to filter grants
keywords = ["education", "youth", "mental health", "family engagement", "social-emotional learning", "basic needs", "community programs"]

# Function to scrape grants dynamically
def scrape_grants():
    driver = setup_driver()
    all_grants = []
    
    for site, url in grant_websites.items():
        driver.get(url)
        time.sleep(5)
        
        try:
            grant_elements = driver.find_elements(By.CLASS_NAME, "result-item")
            for grant in grant_elements:
                try:
                    title = grant.find_element(By.TAG_NAME, "h2").text.strip()
                    description = grant.find_element(By.TAG_NAME, "p").text.strip()
                    link = grant.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    if any(keyword in description.lower() or keyword in title.lower() for keyword in keywords):
                        all_grants.append({"Title": title, "Description": description, "Source": site, "Link": link})
                except:
                    continue
        except:
            continue
        time.sleep(3)
    
    driver.quit()
    return pd.DataFrame(all_grants)

# Streamlit Chatbot UI
st.title("💬 Nonprofit Grant Finder Chatbot")
st.write("Welcome! Ask me about available grants based on your focus area, funding type, or location.")

# User input
user_query = st.text_input("🔍 Enter your funding needs (e.g., 'education grants in New Mexico')")

# Search for grants dynamically
if user_query:
    st.subheader("🔎 Searching for grants...")
    df = scrape_grants()
    
    if not df.empty:
        st.write(df)
    else:
        st.write("❌ No active grants found matching your criteria. Try again later!")

# Email subscription
st.subheader("📩 Get Email Updates")
email = st.text_input("Enter your email to receive weekly grant alerts")
if st.button("Subscribe"):
    if email:
        st.success(f"✅ You are now subscribed for grant alerts: {email}")
    else:
        st.error("❌ Please enter a valid email address.")

