import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

dataframe = pd.read_csv(
    os.path.join(
        os.getcwd(),
        "data",
        "csv",
        "routes_to_scrape.csv"
    )
)

driver = webdriver.Chrome()
driver.get("https://www.viamichelin.fr/itineraires")
driver.implicitly_wait(0.5)

accept_cookies = driver.find_element(by=By.ID, value="didomi-notice-agree-button")
accept_cookies.click()

depart_input = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "departure"))
)
depart_input.click()
depart_input.send_keys(Keys.CONTROL, "a")
depart_input.send_keys(Keys.DELETE)
depart_input.send_keys("Paris Île-de-France")

# Attendre que les résultats apparaissent
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".results li button"))
)

for attempt in range(3):
    try:
        for option in driver.find_elements(by=By.CSS_SELECTOR, value=".results li button"):
            if "Paris" in option.text and "Île-de-France" in option.text:
                option.click()
                break
        break
    except StaleElementReferenceException:
        if attempt == 2:
            raise
        continue

# Attendre que le champ d'arrivée soit prêt
time.sleep(1)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "arrival"))
)

arrival_input = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "arrival"))
)
arrival_input.click()
arrival_input.send_keys(Keys.CONTROL, "a")
arrival_input.send_keys(Keys.DELETE)
arrival_input.send_keys("Lyon Auvergne-Rhône-Alpes")

# Attendre que les résultats apparaissent
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".results li button"))
)

for attempt in range(3):
    try:
        for option in driver.find_elements(by=By.CSS_SELECTOR, value=".results li button"):
            if "Lyon" in option.text and "Auvergne-Rhône-Alpes" in option.text:
                option.click()
                break
        break
    except StaleElementReferenceException:
        if attempt == 2:
            raise
        continue

time.sleep(1)
WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(., \"Rechercher\")]"))
)

button_itineraires = driver.find_element(by=By.XPATH, value="//button[contains(., \"Rechercher\")]")
button_itineraires.click()

driver.implicitly_wait(30)

ad_popup = driver.find_elements(by=By.CSS_SELECTOR, value=".ctz-ads__md-content")
if ad_popup:
    close_ad = driver.find_element(by=By.CSS_SELECTOR, value=".ctz-ads__md-content close-button button")
    close_ad.click()
