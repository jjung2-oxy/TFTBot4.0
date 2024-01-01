import os

import dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

dotenv.load_dotenv()

PATH_TO_CHROMEDRIVER = os.getenv("PATH_TO_CHROMEDRIVER")

def clear_terminal():
    # Clears the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

def scrape_webpage(url):
    try:
        clear_terminal()
        print("Loading the webpage...")

        options = Options()
        options.headless = True
        options.add_argument("--disable-images")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        service = Service(executable_path=PATH_TO_CHROMEDRIVER)
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'CompRow'))
        )
        print("Webpage loaded.")

        page_source = driver.page_source
        driver.quit()
        print("Page source retrieved.")

        soup = BeautifulSoup(page_source, 'html.parser')

        team_containers = soup.find_all('div', class_='CompRow')
        print(f"Found {len(team_containers)} team containers.")

        for container in team_containers:
            team_name = container.find('div', class_='Comp_Title').get_text(strip=True) if container.find('div', class_='Comp_Title') else "No team name"
            print(f"Team Name: {team_name}")

            # Extract units and their items
            units = container.find_all('div', class_='Unit_Wrapper')
            for unit in units:
                unit_name_element = unit.find('div', class_='UnitNames')
                if unit_name_element:
                    unit_name = unit_name_element.get_text(strip=True)
                    item_elements = unit.find_all('img', class_='Item_img')
                    items = [item['alt'] for item in item_elements if 'alt' in item.attrs]
                    print(f"Unit: {unit_name}, Items: {items}")

            print("-" * 40)  # Separator for each team

    except Exception as e:
        print(f"An error occurred: {e}")

url = "https://www.metatft.com/comps"
scrape_webpage(url)
