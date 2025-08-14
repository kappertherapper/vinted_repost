def click_active_button(driver):
    print("Leder efter 'Active' knappen...")
    
    active_selectors = [
        "//button[contains(text(), 'Active')]",
        "//button[contains(text(), 'Aktiv')]", 
        "//a[contains(text(), 'Active')]",
        "//a[contains(text(), 'Aktiv')]",
        "//span[contains(text(), 'Active')]", #this works
        "//span[contains(text(), 'Aktiv')]",
        "[data-testid*='active']",
        ".tab-active, .active-tab",
        "a[href*='active']"
    ]
    
    for i, selector in enumerate(active_selectors):
        try:
            print(f"Prøver selector {i + 1}: {selector}")
            
            if selector.startswith("//"):
                element = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            else:
                element = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            
            element.click()
            print("Klikkede på 'Active' knappen!")
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"Selector {i + 1} virkede ikke: {e}")
            continue
    
    print("❌ Kunne ikke finde 'Active' knappen")

def click_last_item(driver):
    print("Leder efter annoncer...")
    
    selector = "a[href*='/items/']"
    try:
        item_links = driver.find_elements(By.CSS_SELECTOR, selector)
    except Exception as e:
        print(f"Kunne ikke finde annoncer: {e}")
        return False

    if item_links:
        print(f"Fandt {len(item_links)} links med")
    else:
        print("Ingen annoncer fundet")
        return False
    
    try:
        # Scroll ned for at sikre alle elementer er synlige
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Tag den sidste annonce
        last_item = item_links[-1]
        item_url = last_item.get_attribute('href')
        print(f"Åbner den sidste annonce: {item_url}")
        
        # Scroll til elementet og klik
        driver.execute_script("arguments[0].scrollIntoView(true);", last_item)
        time.sleep(1)
        last_item.click()
        time.sleep(3)
        
        print("✅ Klikkede på den sidste annonce!")
        return True
        
    except Exception as e:
        print(f"Fejl ved at klikke på annonce: {e}")
        return False
    
class VintedScraper:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Opsætter Chrome driver med relevante indstillinger"""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Fjern headless hvis du vil se browseren
        # options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        
    def scrape_listing(self, url):
        """Scraper alle relevante data fra en Vinted annonce"""
        if not self.driver:
            self.setup_driver()
            
        self.driver.get(url)
        
        # Vent på at siden loader
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        listing_data = {}
        
        try:
            # Overskrift/titel
            title_element = self.driver.find_element(By.CSS_SELECTOR, "h1[data-testid='item-title']")
            listing_data['title'] = title_element.text
            print(f"Titel: {listing_data['title']}")
            
        except NoSuchElementException:
            print("Kunne ikke finde titel")
            listing_data['title'] = ""
        
        try:
            # Pris
            price_element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='item-price']")
            listing_data['price'] = price_element.text
            print(f"Pris: {listing_data['price']}")
            
        except NoSuchElementException:
            print("Kunne ikke finde pris")
            listing_data['price'] = ""
        
        # Produktdetaljer (Varemærke, Størrelse, Stand, Farve osv.)
        listing_data['details'] = {}
        try:
            # Find alle detalje rækker
            detail_rows = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='item-details'] > div")
            
            for row in detail_rows:
                try:
                    # Find label og værdi
                    label = row.find_element(By.CSS_SELECTOR, "div:first-child").text
                    value = row.find_element(By.CSS_SELECTOR, "div:last-child").text
                    listing_data['details'][label] = value
                    print(f"{label}: {value}")
                except:
                    continue
                    
        except NoSuchElementException:
            print("Kunne ikke finde produktdetaljer")
        
        try:
            # Beskrivelse/annonce tekst
            description_element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='item-description']")
            listing_data['description'] = description_element.text
            print(f"Beskrivelse: {listing_data['description'][:100]}...")
            
        except NoSuchElementException:
            print("Kunne ikke finde beskrivelse")
            listing_data['description'] = ""
        
        # Billeder
        listing_data['images'] = []
        try:
            # Find alle billede elementer
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='item-photo'] img")
            
            for img in image_elements:
                img_src = img.get_attribute('src')
                if img_src and 'placeholder' not in img_src:
                    listing_data['images'].append(img_src)
            
            print(f"Fundet {len(listing_data['images'])} billeder")
            
        except NoSuchElementException:
            print("Kunne ikke finde billeder")
        
        return listing_data
    
    def download_images(self, image_urls, folder_name="downloaded_images"):
        """Download billeder til lokal mappe"""
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        downloaded_files = []
        
        for i, url in enumerate(image_urls):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    filename = f"{folder_name}/image_{i+1}.jpg"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    downloaded_files.append(filename)
                    print(f"Downloaded: {filename}")
            except Exception as e:
                print(f"Fejl ved download af billede {i+1}: {e}")
        
        return downloaded_files
    
    def save_data_to_json(self, data, filename="listing_data.json"):
        """Gem data til JSON fil"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data gemt til {filename}")
    
    def close(self):
        """Luk browser"""
        if self.driver:
            self.driver.quit()

# Eksempel på brug
if __name__ == "__main__":
    scraper = VintedScraper()
    
    try:
        # URL til annoncen
        url = "https://www.vinted.dk/items/6785474491-new-balance-2002r"
        
        # Scrape data
        data = scraper.scrape_listing(url)
        
        # Gem data til JSON
        scraper.save_data_to_json(data)
        
        # Download billeder
        if data['images']:
            downloaded_files = scraper.download_images(data['images'])
            data['downloaded_images'] = downloaded_files
        
        print("\n=== SCRAPED DATA ===")
        print(f"Titel: {data['title']}")
        print(f"Pris: {data['price']}")
        print("Detaljer:")
        for key, value in data['details'].items():
            print(f"  {key}: {value}")
        print(f"Beskrivelse: {data['description'][:200]}...")
        print(f"Antal billeder: {len(data['images'])}")
        
    except Exception as e:
        print(f"Fejl: {e}")
    
    finally:
        scraper.close()    