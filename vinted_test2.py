import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import json
import requests
from urllib.parse import urlparse


profile = "282551394"
listing_data = {}

def simple_vinted_login():

    # Start Chrome
    driver = uc.Chrome()
    
    try:
        print("Åbner Vinted...")
        driver.get("https://www.vinted.dk/")
        
        # Håndter cookies
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
        driver.get(f"https://www.vinted.dk/member/{profile}")
        time.sleep(5)

        # Find og klik på aktiv knappen
        click_active_button(driver)

        # Find og klik på sidste annonce
        click_last_item(driver)
        
        # Find info om annoncen
        listing_data['title'] = findTitle(driver)
        listing_data['price'] = findPrice(driver)
        listing_data["details"] = findDetails(driver)
        listing_data["description"] = findDecription(driver)
        findPictures(driver)
        click_delete_button(driver)


        print("\nBrowseren forbliver åben...")
        input("Tryk Enter for at lukke...")

        # Gem resultater til JSON
        with open("vinted_data.json", "w", encoding="utf-8") as f:
            json.dump(listing_data, f, indent=2, ensure_ascii=False)
            print("\n💾 Data gemt til vinted_data.json")
        
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

def click_delete_button(driver):
    delete_selector = "//span[contains(text(), 'Delete') or contains(text(), 'Slet')]"
    confirm_selector = "//span[contains(text(), 'Confirm and delete') or contains(text(), 'Bekræft og slet')]"

    try:
            delete_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, delete_selector))
            )
            
            delete_btn.click()
            print("Klikkede på 'Delete' knappen!")
            time.sleep(3)

            confirm_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, confirm_selector))
            )

            confirm_btn.click()
            print("Klikkede på 'Bekræft' knappen!")
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
        print(f"✅ Fandt {len(item_links)} annoncer")

        print("Liste over annoncer:")
        for i in range(len(item_links)-1, -1, -1):
            try:
                url = item_links[i].get_attribute('href')
                if url == "https://www.vinted.dk/member/items/favourite_list" or url == "https://www.vinted.dk/items/new":
                    del item_links[i]
                else:    
                    print(f"{i+1}. {url}")
            except Exception as e:
                print(f"{i+1}. Kunne ikke hente URL: {e}")
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
    
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

def findTitle(driver):
    try:
        title_element = driver.find_element(By.CSS_SELECTOR, "h1[class*='title']")
        title = title_element.text
        print(f"Titel: {title}")
        return title
    
    except:
        print("Kunne ikke finde titel")
        return ""

def findPrice(driver):
    try:
        price_element = driver.find_element(By.CSS_SELECTOR, "[data-testid='item-price']")
        price = price_element.text
        print(f"Pris: {price}")
        return price
   
    except:
        print("Kunne ikke finde pris")    
        return ""

def findDetails(driver):
    details_labels = ["Varemærke", "Størrelse", "Artiklens stand", "Farve"]
    details_data = {}

    try:
        item_blocks = driver.find_elements(By.CSS_SELECTOR, "div.details-list__item")

        for block in item_blocks:
            text = block.text.strip()

            # Prøv først at splitte på linjeskift
            lines = text.split("\n")

            if len(lines) >= 2:
                label = lines[0].strip()
                value = lines[1].strip()
            else:
                # Hvis kun én linje, tjek om den starter med en af vores labels
                label = None
                value = None
                for wl in details_labels:
                    if text.startswith(wl):
                        label = wl
                        value = text[len(wl):].strip()  # Fjern label fra starten
                        break

            if label in details_labels and value:
                details_data[label] = value

        print("Fandt detaljer:")
        for k, v in details_data.items():
            print(f"- {k}: {v}")      

        return details_data

    except Exception as e:
        print(f"Kunne ikke finde detaljer: {e}")
        return {}

def findDecription(driver):
    try:
        description_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format"))
        )
        description = description_element.text
        print(f"Description found: {description}")
        return description

    except Exception as e:
        print(f"Error extracting description: {e}")    
        return ""

# -----------------------------------------------------------------------------------------------------------------------------------------------------------

def findPictures(driver):
    # Create images directory if it doesn't exist
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"📁 Oprettede mappe: {images_dir}")
    
    try:
        # Find all images
        image_elements = driver.find_elements(By.CSS_SELECTOR, "img.web_ui__Image__content[data-testid*='item-photo']")
        
        if image_elements:
            print(f"🔍 Fandt {len(image_elements)} billede-elementer")

            listing_data['images'] = []
            img_urls = set()
            
            for img_element in image_elements:
                url = img_element.get_attribute('src')
                if url:  
                    if url not in img_urls:
                        img_urls.add(url)
            
            for i, url in enumerate(img_urls, 1):
                try:
                        print(f"⬇️ Downloader billede {i}: {url[:50]}...")
                        
                        # Download image
                        response = requests.get(url, stream=True)
                        if response.status_code == 200:
                            # Get file extension from URL or default to .jpg
                            parsed_url = urlparse(url)
                            file_extension = os.path.splitext(parsed_url.path)[1]
                            
                            # If no extension found, check URL for common formats or default to .jpg
                            if not file_extension:
                                if 'webp' in url.lower():
                                    file_extension = '.webp'
                                elif 'png' in url.lower():
                                    file_extension = '.png'
                                else:
                                    file_extension = '.jpg'
                            
                            filename = f"billede_{i:02d}{file_extension}"
                            filepath = os.path.join(images_dir, filename)
                            
                            # Ensure the directory exists before writing
                            os.makedirs(os.path.dirname(filepath), exist_ok=True)
                            
                            with open(filepath, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            
                            listing_data['images'].append({
                                'filename': filename,
                                'url': url,
                                'path': filepath
                            })
                            print(f"✅ Billede {i} gemt som: {filename}")
                        else:
                            print(f"❌ Kunne ikke downloade billede {i} (HTTP {response.status_code})")
                        
                except Exception as e:
                    print(f"❌ Fejl ved download af billede {i}: {e}")
                    
        else:
            print("❌ Ingen billeder fundet")
            listing_data['images'] = []
            
    except Exception as e:
        print(f"❌ Fejl ved billedudtrækning: {e}")
        listing_data['images'] = [] 


if __name__ == "__main__":
    print("Starter simpel Vinted login test...")
    simple_vinted_login()