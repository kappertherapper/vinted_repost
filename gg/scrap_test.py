from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import os
import json
import requests
from urllib.parse import urlparse

profile = "282551394"

def vinted_test():
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Start Chrome
    driver = webdriver.Chrome(options=chrome_options)

    time.sleep(3)

    print("Åbner Vinted...")
    driver.get("https://www.vinted.dk/items/6785474491-new-balance-2002r")

    # Håndter cookie dialog
    try:
        print("fuck them cookies...")
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Vælg nødvendige') or contains(text(), 'Afvis alle')]"))
        )
        cookie_button.click()
        print("spiste cookies")
        time.sleep(2)
    except:
        print("Ingen cookies")   

    print("📊 Starter scraping...")
    
    # Vent på at siden loader
    time.sleep(20)

    with open("page_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("📄 HTML skrevet til page_debug.html")

    listing_data = {} 

    # Gem resultater til JSON
    with open("vinted_data.json", "w", encoding="utf-8") as f:
        json.dump(listing_data, f, indent=2, ensure_ascii=False)
        print("\n💾 Data gemt til vinted_data.json")


# ========================== SCRAPING FUNKTIONER ==========================

def scrape_current_listing(driver):
    """Scraper data fra den aktuelt åbne annonce"""
    print("📊 Starter scraping...")
    
    # Vent på at siden loader
    time.sleep(3)
    
    listing_data = {}
    
    # Produktdetaljer
    listing_data['details'] = {}
    try:
        detail_rows = driver.find_elements(By.CSS_SELECTOR, "[data-testid='item-details'] > div")
        
        for row in detail_rows:
            try:
                label = row.find_element(By.CSS_SELECTOR, "div:first-child").text
                value = row.find_element(By.CSS_SELECTOR, "div:last-child").text
                listing_data['details'][label] = value
                print(f"✅ {label}: {value}")
            except:
                continue
                
        if not listing_data['details']:
            # Alternativ metode for detaljer
            detail_elements = driver.find_elements(By.CSS_SELECTOR, ".details-list li, .item-details div")
            for detail in detail_elements:
                text = detail.text
                if ':' in text:
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        listing_data['details'][parts[0].strip()] = parts[1].strip()
                        
    except Exception as e:
        print(f"❌ Fejl ved produktdetaljer: {e}")
    
    # Beskrivelse
    try:
        description_element = driver.find_element(By.CSS_SELECTOR, "[data-testid='item-description']")
        listing_data['description'] = description_element.text
        print(f"✅ Beskrivelse: {listing_data['description'][:50]}...")
    except NoSuchElementException:
        try:
            description_element = driver.find_element(By.CSS_SELECTOR, ".item-description, .description")
            listing_data['description'] = description_element.text
            print(f"✅ Beskrivelse (alt): {listing_data['description'][:50]}...")
        except:
            listing_data['description'] = ""
            print("❌ Kunne ikke finde beskrivelse")
    
    # Billeder
    listing_data['images'] = []
    try:
        # Flere forskellige selectors for billeder
        selectors = [
            "[data-testid='item-photo'] img",
            ".item-photo img",
            ".photos img",
            ".carousel-item img"
        ]
        
        for selector in selectors:
            image_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if image_elements:
                break
        
        for img in image_elements:
            img_src = img.get_attribute('src')
            if img_src and 'placeholder' not in img_src and 'data:image' not in img_src:
                listing_data['images'].append(img_src)
        
        print(f"✅ Fundet {len(listing_data['images'])} billeder")
        
    except Exception as e:
        print(f"❌ Fejl ved billeder: {e}")
    
    return listing_data

def download_images(image_urls, folder_name="downloaded_images"):
    """Download billeder til lokal mappe"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    downloaded_files = []
    
    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                filename = f"{folder_name}/image_{i+1}.jpg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                downloaded_files.append(filename)
                print(f"📥 Downloaded: {filename}")
        except Exception as e:
            print(f"❌ Fejl ved download af billede {i+1}: {e}")
    
    return downloaded_files

def save_to_json(data, filename="listing_data.json"):
    """Gem data til JSON fil"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Data gemt til {filename}")

if __name__ == "__main__":
    print("test med scraping...")
    vinted_test()