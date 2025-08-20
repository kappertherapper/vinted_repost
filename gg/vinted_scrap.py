def scrape_current_listing(driver):
    listing_data = {}
    
    # Titel/overskrift
    # virker ikke hver gang, nogle gange tom
    try:
        title_element = driver.find_element(By.CSS_SELECTOR, "h1[class*='title']")
        listing_data['title'] = title_element.text
        print(f"✅ Titel (alt class): {listing_data['title']}")

    except:
        listing_data['title'] = ""
        print("❌ Kunne ikke finde titel")

    # Pris
    try:
        price_element = driver.find_element(By.CSS_SELECTOR, "[data-testid='item-price']")
        listing_data['price'] = price_element.text
        print(f"✅ Pris: {listing_data['price']}")
   
    except:
        listing_data['price'] = ""
        print("❌ Kunne ikke finde pris")    

    # Details
    details_labels = ["Varemærke", "Størrelse", "Artiklens stand", "Farve"]
    details_data = {}

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

    listing_data["url"] = driver.current_url
    listing_data["details"] = details_data

    print("✅ Fandt ønskede detaljer:")
    for k, v in details_data.items():
        print(f"- {k}: {v}")  


    # Brød tekst
    try:
        description_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format"))
        )
        description_text = description_element.text
        print(f"✅ Description found: {description_text}")
        
    except TimeoutException:
        print("❌ Could not find description")

    except Exception as e:
        print(f"❌ Error extracting description: {e}")

    
    # Create images directory if it doesn't exist
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"📁 Oprettede mappe: {images_dir}")
    
    try:
        # Find all images
        image_elements = driver.find_elements(By.CSS_SELECTOR, "img.web_ui__Image__content[data-testid*='item-photo']")
        
        if image_elements:
            listing_data['images'] = []
            print(f"🔍 Fandt {len(image_elements)} billede-elementer")
            
            # Filter out duplicates
            unique_urls = []
            seen_urls = set()
            
            for img_element in image_elements:
                img_url = img_element.get_attribute('src')
                if img_url:  
                    if img_url not in seen_urls:
                        unique_urls.append(img_url)
                        seen_urls.add(img_url)
            
            print(f"✅ {len(unique_urls)} unikke billeder efter dubletter fjernet")
            
            for i, img_url in enumerate(unique_urls, 1):
                try:
                        print(f"⬇️ Downloader billede {i}: {img_url[:50]}...")
                        
                        # Download image
                        response = requests.get(img_url, stream=True)
                        if response.status_code == 200:
                            # Get file extension from URL or default to .jpg
                            parsed_url = urlparse(img_url)
                            file_extension = os.path.splitext(parsed_url.path)[1]
                            
                            # If no extension found, check URL for common formats or default to .jpg
                            if not file_extension:
                                if 'webp' in img_url.lower():
                                    file_extension = '.webp'
                                elif 'png' in img_url.lower():
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
                                'url': img_url,
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