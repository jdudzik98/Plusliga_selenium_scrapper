from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import csv
from tqdm import tqdm

driver = webdriver.Chrome('./chromedriver')
match_links = []

for year in tqdm(range(2020, 2023)):
    url = 'https://www.plusliga.pl/games/tour/' + str(year) + '.html'
    driver.get(url)

    # Click the cookies button:
    try:
        wait = WebDriverWait(driver, 10)
        element = wait.until(
            ec.element_to_be_clickable((By.XPATH, "/html/body/footer/div[6]/div/div[4]/div/button[4]")))
        element.click()

        print('clicked cookies')
    except NoSuchElementException:
        print('not clicked cookies')
        pass
    except TimeoutException:
        pass

    # Click the phase button:
    try:
        wait = WebDriverWait(driver, 10)
        element = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                         "//*[@style='display: block;']//div[@class='col-md-12 bar sort filtr fazy']//*[contains(text(), 'Faza zasadnicza')]")))
        element.click()
        print('clicked phase')
    except NoSuchElementException:
        print('not clicked phase')
        pass
    except TimeoutException:
        print('not clicked phase')
        pass

    # Get the matches links and add to match_links list
    matches = driver.find_elements(By.XPATH,
                                   ".//div[contains(@class, 'gameData team-')]//a[@class='btn btn-default btm-margins']")
    for match in matches:
        match_links.append((year, match.get_attribute('href')))

# Write match_links to a CSV file
with open('Matches_links.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(match_links)
