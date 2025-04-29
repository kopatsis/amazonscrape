from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import time
import csv
import random

driver = webdriver.Chrome()

def is_valid_url(url):
    print(url)
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def safe_get_element_text(driver, by, value):
    try:
        return driver.find_element(by, value).text
    except Exception:
        return ""

def safe_get_element_attribute(driver, by, value, attribute):
    try:
        return driver.find_element(by, value).get_attribute(attribute)
    except Exception:
        return ""

def load_existing_links(output_file):
    existing_links = set()
    try:
        with open(output_file, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                existing_links.add(row[0].strip())
    except FileNotFoundError:
        pass
    return existing_links

output_file = 'output_second.csv'
existing_links = load_existing_links(output_file)

with open('links.csv', 'r') as infile, open(output_file, 'a', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    if outfile.tell() == 0:
        writer.writerow(['Amazon Link', 'Price', 'Offer Text', 'Link URL', 'Reviews', 'Star Rating', 'Delivery Text'])

    first_valid_link_processed = False

    for row in reader:
        link = row[0].strip()

        if not is_valid_url(link):
            print("invalid")
            continue

        if link in existing_links:
            continue

        driver.get(link)
        
        if not first_valid_link_processed:
            first_valid_link_processed = True
            input("Press Enter once you've solved the captcha, if required.")

        time.sleep(random.uniform(4.5, 7.5))

        price_whole = safe_get_element_text(driver, By.CSS_SELECTOR, '.a-price-whole')
        price_fraction = safe_get_element_text(driver, By.CSS_SELECTOR, '.a-price-fraction')
        price = f"{price_whole}.{price_fraction}" if price_whole else ""

        offer_text = safe_get_element_text(driver, By.CSS_SELECTOR, '.a-size-small.offer-display-feature-text-message')
        href = safe_get_element_attribute(driver, By.CSS_SELECTOR, 'span.a-size-small.offer-display-feature-text-message a', 'href')

        reviews = safe_get_element_text(driver, By.ID, 'acrCustomerReviewText')
        raw_rating = safe_get_element_attribute(driver, By.ID, 'acrPopover', 'textContent')
        star_rating = raw_rating.strip().split(' ')[0] if raw_rating else ""
        delivery_text = safe_get_element_text(driver, By.CSS_SELECTOR, '[data-csa-c-type="element"][data-csa-c-content-id="DEXUnifiedCXPDM"]')

        print(f"Link: {link}")
        print(f"Price: {price}")
        print(f"Offer Text: {offer_text}")
        print(f"Link URL: {href}")
        print(f"Reviews: {reviews}")
        print(f"Star Rating: {star_rating}")
        print(f"Delivery Text: {delivery_text}")
        print("-------------------------------")

        writer.writerow([link, price, offer_text, href, reviews, star_rating, delivery_text])
        existing_links.add(link)

driver.quit()
