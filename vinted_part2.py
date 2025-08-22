import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    wait = WebDriverWait(driver, 10)
    
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
        #driver.get(f"https://www.vinted.dk/member/{profile}")
        time.sleep(2)
        
        # Test
        click_sell_button(driver)

        # Indlæs data
        with open('vinted_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    
        # Titel
        wait.until(EC.presence_of_element_located((By.NAME, 'title'))).send_keys(data['title'])
        print("Title filled")
        time.sleep(4)

        # Description
        description = driver.find_element(By.CSS_SELECTOR, "textarea#description")
        description.clear() #kan den uden?
        description.send_keys(data["description"])
        print("Description filled")
        time.sleep(4)

        # Category
        #category_dropdown = wait.until(EC.presence_of_element_located((By.NAME, 'category')))
        #category_dropdown.click()
        #time.sleep(2)
        #print("Category dropdown opened")

        # Price
        price_input = wait.until(EC.presence_of_element_located((By.NAME, 'price')))

        # Hent prisen
        price = data["price"]

        # Fjern "DKK" (og evt. ekstra mellemrum)
        clean_price = price.replace("DKK", "").strip()

        price_input.send_keys(clean_price)
        print("✅ Price filled")

        print("\nBrowseren forbliver åben...")
        input("Tryk Enter for at lukke...")

        # Gem resultater til JSON
        # with open("vinted_data.json", "w", encoding="utf-8") as f:
        #    json.dump(listing_data, f, indent=2, ensure_ascii=False)
        #    print("\n💾 Data gemt til vinted_data.json")
        
    except Exception as e:
        print(f"Fejl: {e}")
    
    finally:
        driver.quit()
        print("Browseren er lukket")

# -----------------------------------------------------------------------------------------------------------------------------------------------------------   

def click_sell_button(driver):
    selector = "//span[contains(text(), 'Sell now') or contains(text(), 'Sælg nu')]"
    try:
            btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, selector))
            )
            
            btn.click()
            print("Klikkede på 'Sell now' knappen!")
            time.sleep(3)
            return True
            
    except Exception as e:
        print(f"Selector virkede ikke: {e}")
    
    print("Kunne ikke finde 'Sælg nu' knappen")


if __name__ == "__main__":
    print("Starter simpel Vinted login test...")
    simple_vinted_login()