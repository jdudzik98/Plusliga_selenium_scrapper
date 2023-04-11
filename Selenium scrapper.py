from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from tqdm import tqdm

driver = webdriver.Chrome('./chromedriver')
url = 'https://www.plusliga.pl/games/id/1101129/tour/2020.html'
driver.get(url)

# Click the cookies button:
try:
    wait = WebDriverWait(driver, 10)
    element = wait.until(ec.element_to_be_clickable((By.XPATH, "/html/body/footer/div[6]/div/div[4]/div/button[4]")))
    element.click()

    print('clicked')
except NoSuchElementException:
    print('not clicked')
    pass
time.sleep(10)

# Fetch match date:
try:
    Date = driver.find_element(By.XPATH, "//div[@class='row text-center gridtable games']//div[@class="
                                         "'date khanded']").text
except NoSuchElementException:
    Date = None
try:
    Phase = driver.find_element(By.XPATH, "//div[@class='row text-center']//*[text()='Faza:']/following-sibling::node()"
                                          "[1]").text
except NoSuchElementException:
    Phase = None
try:
    Spectators = driver.find_element(By.XPATH, "//div[@class='row text-center']//*[text()='Liczba widzów:']/following-"
                                               "sibling::node()[1]").text
except NoSuchElementException:
    Spectators = None
try:
    Capacity = driver.find_element(By.XPATH, "//table[@class='right-left spaccedsss']//*[text()='Liczba miejsc "
                                             "siedzących w hali:']/following-sibling::node()[1]").text
except NoSuchElementException:
    Capacity = None

try:
    href_elements = driver.find_elements(By.XPATH, "//div[@class='row text-center gridtable games'][1]//a["
                                                   "starts-with(@href, '/teams/id')]")
    href_list = [elem.get_attribute('href') for elem in href_elements]
    unique_href_list = list(set(href_list))
except NoSuchElementException:
    unique_href_list = None

try:
    elements = driver.find_elements(By.XPATH,
                                    "//div[@class='row text-center gridtable games']//span[contains(concat(' ', "
                                    "normalize-space(@class), ' '), 'green') or contains(concat(' ', normalize-space("
                                    "@class), ' '), 'red')]")
    result = [elem.text for elem in elements]
except NoSuchElementException:
    result = None

# Create a dataframe:
df = pd.DataFrame({'Date': Date,  # Date of the match
                   'Phase': Phase,  # Phase of the match
                   'Spectators': Spectators,  # Number of spectators
                   'Capacity': Capacity,  # Capacity of the hall
                   'Team1': unique_href_list[0],  # Team 1
                   'Team2': unique_href_list[1],  # Team 2
                   'Result_1': result[0],  # Result of the match
                   'Result_2': result[1]},  # Result of the match
                  index=[0])

# Iterate over points:
driver.switch_to.frame(0)
elements = driver.find_element(By.XPATH, "//div[@class='play-by-play-container']")\
    .find_elements(By.XPATH, "//div[@class='events-container']")
for element in tqdm(elements):
    sub_elements = element.find_elements(By.XPATH, "//div[@class='w100']")
    print(sub_elements[1].text)

df.to_csv('Matches.csv', index=False)

# Close browser:
driver.quit()
