import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def start_hepsiemlak_test():
    print("Hepsiemlak test botu başlatılıyor (Gelişmiş JS Seçicileri ile)...")
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=options, version_main=147) 

    try:
        target_url = "https://www.hepsiemlak.com/satilik"
        driver.get(target_url)
        time.sleep(5)

        try:
            cookie_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Tümünü Kabul Et') or contains(text(), 'Kabul Et')]"))
            )
            cookie_btn.click()
            time.sleep(2)
        except:
            pass

        print("İlanların yüklenmesi için sayfa aşağı kaydırılıyor...")
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(3)
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

        ilan_linkleri = []
        tum_linkler = driver.find_elements(By.CSS_SELECTOR, "a")
        
        for a in tum_linkler:
            try:
                href = a.get_attribute("href")
                if href and "satilik" in href and any(char.isdigit() for char in href):
                    if len(href) > 40 and href not in ilan_linkleri:
                        ilan_linkleri.append(href)
            except:
                continue

        if len(ilan_linkleri) == 0:
            print("Hiç ilan linki bulunamadı. Seçicileri veya sayfa yüklenmesini kontrol edin.")
            return

        print(f"Toplam {len(ilan_linkleri)} link bulundu. SADECE İLK 3 İLANIN detayına giriliyor...\n")

        for url in ilan_linkleri[:3]:
            try:
                driver.get(url)
                time.sleep(2) 
                driver.execute_script("window.scrollBy(0, 500);") 
                time.sleep(random.uniform(3, 5)) 
                
                try:
                    title = driver.find_element(By.CSS_SELECTOR, "h1").get_attribute("textContent").strip()
                except:
                    title = "Başlık Bulunamadı"

                try:
                    price = driver.find_element(By.CSS_SELECTOR, ".font-title-1, .price, .fz24-bold").get_attribute("textContent").strip()
                except:
                    price = "Fiyat Bulunamadı"
                
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
                    return "-"

                oda_sayisi = fuzzy_get(["Oda Sayısı", "Oda + Salon"])
                metrekare = fuzzy_get(["Brüt / Net", "Brüt M2", "Metrekare", "m2", "m²"])
                kat = fuzzy_get(["Bulunduğu Kat", "Kat"])
                yas = fuzzy_get(["Bina Yaşı", "Yaş"])
                isinma = fuzzy_get(["Isınma Tipi", "Isıtma"])
                esya = fuzzy_get(["Eşya Durumu", "Eşyalı"])

                print("=" * 50)
                print(f"BAŞLIK    : {title}")
                print(f"FİYAT     : {price}")
                print(f"LOKASYON  : {city} / {district} / {neighborhood}")
                print("-" * 50)
                print(f"Oda Sayısı     : {oda_sayisi}")
                print(f"Brüt / Net M2  : {metrekare}")
                print(f"Bulunduğu Kat  : {kat}")
                print(f"Bina Yaşı      : {yas}")
                print(f"Isınma Tipi    : {isinma}")
                print(f"Eşya Durumu    : {esya}")
                print("=" * 50 + "\n")

            except Exception as e:
                print(f"Hata: {url} çekilirken sorun oldu.\nDetay: {e}\n")

    finally:
        driver.quit()
        print("Test tamamlandı.")

if __name__ == "__main__":
    start_hepsiemlak_test()
    