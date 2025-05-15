import requests
import json
from bs4 import BeautifulSoup
import csv
import random
import time
import pandas as pd
from random import uniform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from selenium.webdriver.support.ui import Select


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
]


def setup_browser():
    """setup browser and User-Agent randomly"""
    chrome_options = Options()

    user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"user-agent={user_agent}")

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-extensions")

    browser = webdriver.Chrome(options=chrome_options)
    browser.maximize_window()

    browser = Driver(uc=True)
    url = "https://mesowest.utah.edu"
    browser.uc_open_with_reconnect(url, 1)
    browser.uc_gui_click_captcha()
    browser.maximize_window()

    browser.refresh()
    time.sleep(2)

    return browser

def open_to_website(browser):
    url = "https://mesowest.utah.edu/cgi-bin/droman/mesomap.cgi?state=AKCC&rawsflag=3"
    browser.get(url)
    time.sleep(5)

    # Ambil source HTML halaman
    soup = BeautifulSoup(browser.page_source, "html.parser")

    # Temukan form yang benar
    form = soup.find("form", attrs={"onsubmit": "return submitit(this)"})

    # Temukan select id=state di dalam form
    select_state = form.find("select", attrs={"id": "state"})

    # Ambil semua opsi dari select
    state_options = [
        (opt.get("value"), opt.text.strip()) 
        for opt in select_state.find_all("option") 
        if opt.get("value")
    ]

    print(f"✅ Total state unik dalam form: {len(state_options)}")

    wait = WebDriverWait(browser, 2)

    for index, (state_val, state_text) in enumerate(state_options):
        print(f"\n➡️ [{index + 1}] Memilih state: {state_text}")

        browser.get(url)
        wait.until(EC.presence_of_element_located((By.ID, "state")))
        time.sleep(1)

        # Pilih state via JavaScript
        browser.execute_script(f"""
            let select = document.getElementById('state');
            select.value = '{state_val}';
            select.dispatchEvent(new Event('change'));
        """)
        print(f"✅ State '{state_text}' dipilih.")

        time.sleep(1)

        # Pilih product tetap
        browser.execute_script("""
            let select = document.getElementById('product');
            select.value = 'summary';
            select.dispatchEvent(new Event('change'));
        """)
        print("✅ Product 'Current Weather Summary' dipilih.")

        time.sleep(1)

        # Klik tombol Go
        go_button = wait.until(EC.element_to_be_clickable((By.ID, "navgo")))
        go_button.click()
        print("✅ Tombol 'Go' diklik.")

        soup = BeautifulSoup(browser.page_source, "html.parser")
        
        tables = soup.find_all("table", attrs={"width": "800", "border": "1"})

        for idx, table in enumerate(tables, 1):
            print(f"\n📄 Tabel #{idx}")

            rows = table.find_all("tr")
            for row in rows:
                cols = row.find(["td"])      
                print(cols)          
                # col_texts = [col.get_text(strip=True) for col in cols]
                # print(" | ".join(col_texts))
                print("-" * 50)
        print(f"✅ Tabel #{idx} selesai diproses.")



        



        time.sleep(5)




def main():
    browser = setup_browser()
    open_to_website(browser)
    time.sleep(5)
    browser.quit()

if __name__ == "__main__":
    main()
