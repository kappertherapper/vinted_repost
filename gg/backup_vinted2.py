from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import os
import json

profile = "282551394"

def simple_vinted_login():
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Start Chrome
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Åbner Vinted...")
        driver.get("https://www.vinted.dk/")
        
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
        
        print("Log ind på Vinted i browseren...")
        input("Tryk Enter når du er færdig med at logge ind...")
        
        # Gå til din profil
        driver.get("https://www.vinted.dk/member/282551394")
        time.sleep(5)

        # Find og klik på "Active" knappen
        click_active_button(driver)

        # Find og klik på sidste annonce
        success = click_last_item(driver)
        
        if success:
            # SCRAPE DATA FRA ANNONCEN
            print("\n🔄 Scraper data fra annoncen...")
            listing_data = scrape_current_listing(driver)
            
            if listing_data:
                # Gem data til JSON
                filename = f"listing_{int(time.time())}.json"
                save_to_json(listing_data, filename)
                
                # Download billeder
                if listing_data.get('images'):
                    folder_name = f"images_{int(time.time())}"
                    downloaded_files = download_images(listing_data['images'], folder_name)
                    listing_data['downloaded_images'] = downloaded_files
                
                print("\n✅ DATA SCRAPED SUCCESSFULLY!")
                print(f"📄 Titel: {listing_data.get('title', 'N/A')}")
                print(f"💰 Pris: {listing_data.get('price', 'N/A')}")
                print(f"📸 Billeder: {len(listing_data.get('images', []))}")
                print(f"📝 Beskrivelse: {listing_data.get('description', 'N/A')[:100]}...")
                
                # Print detaljer
                if listing_data.get('details'):
                    print("\n📋 Produktdetaljer:")
                    for key, value in listing_data['details'].items():
                        print(f"   {key}: {value}")
        
        print("\nBrowseren forbliver åben så du kan tjekke...")
        input("Tryk Enter for at lukke browseren...")
        
    except Exception as e:
        print(f"Fejl: {e}")
    
    finally:
        driver.quit()
        print("Browseren er lukket")

# -----------------------------------------------------------------------------------------------------------------------------------------------------------        

def click_active_button(driver):
    selector = "//span[contains(text(), 'Active') or contains(text(), 'Aktiv')]"
    try:
        element = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, selector))
        )
        
        element.click()
        print("Klikkede på 'Active' knappen!")
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"Selector virkede ikke: {e}")
    
    print("Kunne ikke finde 'Active' knappen")

# -----------------------------------------------------------------------------------------------------------------------------------------------------------

def click_last_item(driver):
    print("Leder efter annoncer...")
    
    selector = "a[href*='/items/']"
    try:
        item_links = driver.find_elements(By.CSS_SELECTOR, selector)
    except Exception as e:
        print(f"Kunne ikke finde annoncer: {e}")
        return False

    if item_links:
        print(f"✅ Fandt {len(item_links)} annoncer med selector: {selector}")

        print("Liste over annoncer:")
        for i, link in enumerate(item_links, start=1):
            try:
                url = link.get_attribute('href')
                print(f"{i}. {url}")
            except Exception as e:
                print(f"{i}. Kunne ikke hente URL: {e}")
    else:
        print("Ingen annoncer fundet")
        return False
    
    try:
        # Scroll ned
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Find sidste annonce
        last_item = item_links[-1]
        item_url = last_item.get_attribute('href')
        print(f"Åbner den sidste annonce: {item_url}")
        
        # Scroll og klik
        driver.execute_script("arguments[0].scrollIntoView(true);", last_item)
        time.sleep(1)
        last_item.click()
        time.sleep(3)
        
        print("Klikkede på den sidste annonce!")
        return True
        
    except Exception as e:
        print(f"Fejl ved at klikke på annonce: {e}")
        return False

# ========================== SCRAPING FUNKTIONER ==========================

def scrape_current_listing(driver):
    """Scraper data fra den aktuelt åbne annonce"""
    print("📊 Starter scraping...")
    
    # Vent på at siden loader
    time.sleep(3)
    
    listing_data = {}
    
    # Titel/overskrift
    try:
        title_element = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='item-title']")
        listing_data['title'] = title_element.text
        print(f"✅ Titel: {listing_data['title']}")
    except NoSuchElementException:
        # Alternativ selector
        try:
            title_element = driver.find_element(By.CSS_SELECTOR, "h1")
            listing_data['title'] = title_element.text
            print(f"✅ Titel (alt): {listing_data['title']}")
        except:
            listing_data['title'] = ""
            print("❌ Kunne ikke finde titel")
    
    # Pris
    try:
        price_element = driver.find_element(By.CSS_SELECTOR, "[data-testid='item-price']")
        listing_data['price'] = price_element.text
        print(f"✅ Pris: {listing_data['price']}")
    except NoSuchElementException:
        # Alternativ selector for pris
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, ".item-price, .price")
            listing_data['price'] = price_element.text
            print(f"✅ Pris (alt): {listing_data['price']}")
        except:
            listing_data['price'] = ""
            print("❌ Kunne ikke finde pris")
    
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
    print("Starter simpel Vinted login test med scraping...")
    simple_vinted_login()