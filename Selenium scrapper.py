from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome('./chromedriver')
url = 'https://www.plusliga.pl/games/id/1101129/tour/2020.html'
driver.get(url)

# Click the cookies button:
try:
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/footer/div[6]/div/div[4]/div/button[4]")))
    element.click()

    print('clicked')
except:
    print('not clicked')
    pass

# Fetch match date:
time.sleep(1)
nameAndSurname = driver.find_element(By.XPATH, "//div[@class='row text-center gridtable games']//div[@class='date khanded']").text

print(nameAndSurname)

# Close browser:
driver.quit()