from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
from tqdm import tqdm

driver = webdriver.Chrome('./chromedriver')

# Create the dataframe to store the data:
df = pd.DataFrame({'year': [],
                   'round_number': [],
                   'position': [],
                   'team': [],
                   'points': [],
                   'played_matches': [],
                   'won_matches': [],
                   'lost_matches': [],
                   'sets_won': [],
                   'sets_lost': [],
                   'points_won': [],
                   'points_lost': [],
                   'sets_ratio': [],
                   'points_ratio': []}
                  )

# create loop to create urls for each season
for year in tqdm(range(2019, 2022)):
    url = 'https://www.plusliga.pl/table/tour/' + str(year) + '.html'
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
        element = wait.until(ec.element_to_be_clickable((By.XPATH, "//*[@id='filterContent']/div[1]/div/div/a[1]")))
        element.click()

        print('clicked phase')
    except NoSuchElementException:
        print('not clicked phase')
        pass
    except TimeoutException:
        pass

    # Get the round buttons:
    round_buttons = driver.find_element(By.XPATH,
                                        "//div[@class='col-xs-12 bar sort filtr fazy rundy kolejki grupa-1 faza-1']"). \
        find_elements(By.XPATH, ".//a")
    for round_button in tqdm(round_buttons[1:len(round_buttons)]):
        # Click the round button:
        try:
            round_button.click()
            # print('clicked round')

            # Get the table:
            table = driver.find_element(By.XPATH,
                                        "//table[@class='rs-standings-table table table-bordered table-hover table-condensed']")
            # Get the table rows:
            rows = table.find_elements(By.XPATH, ".//tbody/tr[not(contains(@class, 'hidden'))]")

            for row in rows:
                # get the rows attributes:
                round_number = row.get_attribute('data-termin')[4:]
                team = row.find_element(By.XPATH, ".//td[2]/a").get_attribute('href')
                point_info = row.find_elements(By.XPATH, ".//td")

                # Create a dictionary:
                data = {'year': year,
                        'round_number': round_number,
                        'position': point_info[0].text,
                        'team': team,
                        'points': point_info[2].text,
                        'played_matches': point_info[3].text,
                        'won_matches': point_info[4].text,
                        'lost_matches': point_info[5].text,
                        'sets_won': point_info[6].text,
                        'sets_lost': point_info[7].text,
                        'points_won': point_info[8].text,
                        'points_lost': point_info[9].text,
                        'sets_ratio': point_info[10].text,
                        'points_ratio': point_info[11].text}
                # Append the dictionary to the dataframe:
                df.loc[len(df)] = data
        except NoSuchElementException:
            print('not clicked round')
            pass

# Save the dataframe to a csv file:
df.to_csv('table_standings.csv', index=False)
# Close browser:
driver.quit()
