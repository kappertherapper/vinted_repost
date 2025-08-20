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

if __name__ == "__main__":
    print("Starter simpel Vinted login test...")
    simple_vinted_login()