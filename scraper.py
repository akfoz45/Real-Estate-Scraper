import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import time
import random
import re
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'host' : 'localhost',
    'user' : 'root',         
    'password' : os.getenv("DB_PASSWORD"), 
    'database' : 'house_price_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def get_or_create_location(cursor, city, district, neighborhood):
    cursor.execute("SELECT city_id FROM cities WHERE city_name = %s", (city,))
    result = cursor.fetchone()
    if result:
        city_id = result[0]
    else:
        cursor.execute("INSERT INTO cities (city_name) VALUES (%s)", (city,))
        city_id = cursor.lastrowid

    cursor.execute("SELECT district_id FROM districts WHERE district_name = %s AND city_id = %s", (district, city_id))
    result = cursor.fetchone()
    if result:
        district_id = result[0]
    else:
        cursor.execute("INSERT INTO districts (district_name, city_id) VALUES (%s, %s)", (district, city_id))
        district_id = cursor.lastrowid

    cursor.execute("SELECT neighborhood_id FROM neighborhoods WHERE neighborhood_name = %s AND district_id = %s", (neighborhood, district_id))
    result = cursor.fetchone()
    if result:
        neighborhood_id = result[0]
    else:
        cursor.execute("INSERT INTO neighborhoods (neighborhood_name, district_id) VALUES (%s, %s)", (neighborhood, district_id))
        neighborhood_id = cursor.lastrowid

    return neighborhood_id

def insert_listing(cursor, listing_data):
    query = """
    INSERT IGNORE INTO listings 
    (listing_id, neighborhood_id, title, price, room_count, gross_sqm, net_sqm, building_age, floor_level, heating_type, is_furnished)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, listing_data)

def handle_cloudflare(driver):
    try:
        time.sleep(2)
        current_title = driver.title.lower()
        if "güvenlik" in current_title or "moment" in current_title or "cloudflare" in current_title or "dikkat" in current_title:
            print("🛡️ Cloudflare Algılandı! İnsan taklidi yapılıyor...")
            for _ in range(3):
                driver.execute_script(f"window.scrollBy(0, {random.randint(200, 500)});")
                time.sleep(random.uniform(2, 4))
            time.sleep(6) 
    except:
        pass

def start_scraping():
    print("Nihai Bot Başlatılıyor: Veriler doğrudan MySQL'e yazılacak...")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    options.page_load_strategy = 'normal' 

    """
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    """

    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=options, version_main=147)

    try:
        ref_links = []

        #target_url = "https://www.hepsiemlak.com/satilik"
        for page in range(1,10):
            print(f"\n{'='*20} SAYFA {page} İŞLENİYOR {'='*20}")

            if page == 1:
                target_url = "https://www.hepsiemlak.com/istanbul-satilik"
            else:
                target_url = f"https://www.hepsiemlak.com/istanbul-satilik?page={page}"

            driver.get(target_url)
            time.sleep(4)

            handle_cloudflare(driver)

            if page == 1:
                try:
                    cookie_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Tümünü Kabul Et') or contains(text(), 'Kabul Et')]"))
                    )
                    cookie_btn.click()
                    time.sleep(2)
                except:
                    pass

            print(f"Sayfa {page} kaydırılıyor...")
            for _ in range(4):
                driver.execute_script(f"window.scrollBy(0, {random.randint(800, 1200)});")
                time.sleep(random.uniform(1.5, 3.0))

            all_ref = driver.find_elements(By.CSS_SELECTOR, "a")
            for a in all_ref:
                try:
                    href = a.get_attribute("href")
                    if href and "-satilik" in href and "?" not in href and any(char.isdigit() for char in href):
                        if len(href) > 40 and href not in ref_links:
                            ref_links.append(href)
                except:
                    continue

            print(f"Sayfa {page} tamamlandı. Toplam link havuzu: {len(ref_links)}")

            time.sleep(random.uniform(3, 6))

        print(f"\nToplam {len(ref_links)} adet İstanbul ilan bulundu. Veritabanı aktarımı başlıyor...\n")
        if len(ref_links) == 0: return

        for url in ref_links:
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 4))

                handle_cloudflare(driver)

                time.sleep(random.uniform(2, 4))
                driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(random.uniform(1, 2))
                
                listing_id = url.split('/')[-1]

                try:
                    title = driver.find_element(By.CSS_SELECTOR, "h1").get_attribute("textContent").strip()
                except:
                    continue

                try:
                    price_str = driver.find_element(By.CSS_SELECTOR, ".font-title-1, .price, .fz24-bold").get_attribute("textContent").strip()
                    price = int("".join(filter(str.isdigit, price_str)))
                except:
                    print(f"Uyarı: {listing_id} ID'li ilanın fiyatı okunamadı, atlanıyor.")
                    continue
                
                city, district, neighborhood = "Belirtilmemiş", "Belirtilmemiş", "Belirtilmemiş"
                for part in url.split("/"):
                    if "-satilik" in part:
                        clean_loc = part.replace("-satilik", "").split("-")
                        city = clean_loc[0].capitalize() if len(clean_loc) > 0 else city
                        district = clean_loc[1].capitalize() if len(clean_loc) > 1 else district
                        neighborhood = " ".join(clean_loc[2:]).capitalize() if len(clean_loc) > 2 else neighborhood
                        break

                features = driver.execute_script("""
                    let data = {};
                    let items = document.querySelectorAll('li, .spec-item, .property-item, tr'); 
                    
                    items.forEach(item => {
                        let textContent = item.innerText.split('\\n').map(x => x.trim()).filter(x => x);
                        
                        if (textContent.length === 2) {
                            data[textContent[0]] = textContent[1];
                        } 
                        else {
                            let spans = item.querySelectorAll('span, div');
                            if(spans.length >= 2) {
                                 let key = spans[0].innerText.trim();
                                 let value = spans[1].innerText.trim();
                                 if(key && value && key !== value) {
                                     data[key] = value;
                                 }
                            }
                        }
                    });
                    return data;
                """)

                def fuzzy_get(search_keys):
                    for k, v in features.items():
                        for sk in search_keys:
                            if sk.lower() in k.lower():
                                return v
                    return None 

                oda_sayisi = fuzzy_get(["Oda Sayısı", "Oda + Salon"])
                kat = fuzzy_get(["Bulunduğu Kat", "Kat"])
                yas = fuzzy_get(["Bina Yaşı", "Yaş"])
                isinma = fuzzy_get(["Isınma Tipi", "Isıtma"])
                esya = fuzzy_get(["Eşya Durumu", "Eşyalı"])

                sqm_str = fuzzy_get(["Brüt / Net", "Brüt M2", "Metrekare", "m2", "m²"])
                gross_sqm, net_sqm = None, None
                if sqm_str:
                    cleaned_str = sqm_str.lower().replace("m2", "").replace("m²", "").replace("m", "")

                    numbers = [int(s) for s in re.findall(r'\d+', cleaned_str)]
                    if len(numbers) >= 2:
                        gross_sqm, net_sqm = numbers[0], numbers[1]
                    elif len(numbers) == 1:
                        gross_sqm, net_sqm = numbers[0], numbers[0]

                neighborhood_id = get_or_create_location(cursor, city, district, neighborhood)

                listing_data = (
                    listing_id, neighborhood_id, title, price, oda_sayisi, 
                    gross_sqm, net_sqm, yas, kat, isinma, esya
                )

                insert_listing(cursor, listing_data)
                conn.commit()
                
                print(f"BAŞARILI: {listing_id} | {city}/{district} | {price} TL | Kaydedildi.")

            except Exception as e:
                #print(f"HATA: {url} işlenirken hata oluştu. Detay: {e}")
                pass

    finally:
        driver.quit()
        cursor.close()
        conn.close()
        print("\nİşlem Tamamlandı. Veritabanı bağlantısı ve Tarayıcı kapatıldı.")

if __name__ == "__main__":
    start_scraping()