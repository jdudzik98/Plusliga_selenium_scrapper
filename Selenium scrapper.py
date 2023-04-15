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

# Fetch match information:
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

try:
    players_tables = driver.find_element(By.XPATH, "//table[@class='rs-standings-table stats-table table "
                                                   "table-bordered table-hover table-condensed table-striped "
                                                   "responsive double-responsive']")
    numbers = players_tables.find_elements(By.XPATH, "//th[@class='min-responsive']//span")
    names = players_tables.find_elements(By.XPATH, "//th[@class='min-responsive']//a")
    hrefs = players_tables.find_elements(By.XPATH, "//th[@class='min-responsive']//a")

    # Create an empty players dataframe
    players = pd.DataFrame({'nameAndSurname': [], 'number': [], 'href': []}, index=[])

    # Iterate over players to append them to the dataframe:
    for player in range(len(numbers)):
        players.loc[len(players)] = [names[player].text, numbers[player].text, hrefs[player].get_attribute('href')]

    # Assign team names to the players dataframe:
    players['number'] = pd.to_numeric(players['number'])
    players['team'] = unique_href_list[1]
    first_change_idx = (players['number'].diff() < 0).idxmax() - 1
    players.loc[0:first_change_idx, 'team'] = unique_href_list[0]

except NoSuchElementException:
    players = None
    print("Couldn't find players")

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
sets = driver.find_element(By.XPATH, "//div[@class='play-by-play-container']")\
    .find_elements(By.XPATH, ".//div[@class='events-container']")

for set in sets[0:1]:

    # Fetch set information:
    set_info = set.find_element(By.XPATH, ".//vsw-end-set-play-by-play[@class='w100']")
    set_score = set_info.find_elements(By.XPATH, ".//div[@class='result match-result']")
    point_score = set_info.find_elements(By.XPATH, ".//div[@class='result set-result']")
    set_score_host = int(set_score[0].text)
    set_score_guest = int(set_score[1].text)
    point_score_host = int(point_score[0].text)
    point_score_guest = int(point_score[1].text)
    if point_score_host > point_score_guest:
        set_score_host_before = set_score_host-1
        set_score_guest_before = set_score_guest
    else:
        set_score_host_before = set_score_host
        set_score_guest_before = set_score_guest-1
    print(set_score_host, set_score_guest, point_score_host, point_score_guest, set_score_host_before,
          set_score_guest_before)

    # Fetch list of players for each team:
    squads = set.find_element(By.XPATH, ".//vsw-lineup-play-by-play[@class='w100']")
    host_team = squads.find_element(By.XPATH, ".//div[@class='team']").\
        find_elements(By.XPATH, ".//span[@class='player-nr']")
    print("host team: ", [player.text for player in host_team])
    guest_team = squads.find_element(By.XPATH, ".//div[@class='team right']").\
        find_elements(By.XPATH, ".//span[@class='player-nr']")
    print("guest team: ", [player.text for player in guest_team])

    # Fetch points:
    play_by_play = set.find_elements(By.XPATH, ".//div[@class='w100']")
    for point in reversed(play_by_play):
        try:
            host_score = point.find_element(By.XPATH, ".//span[contains(@class, 'left')]").text
            guest_score = point.find_element(By.XPATH, ".//span[contains(@class, 'right')]").text
            serving_player = point.find_element(By.XPATH, ".//p[@class='shirt-number']").text
            serve_result = point.find_element(By.XPATH, ".//span[@class='skill']").text
            serve_effect = point.find_element(By.XPATH, ".//span[@class='effect']").text
            try:  # If first element of the point contains character "right" in class name (i.e. guest is serving):
                serving = point.find_element(By.XPATH, ".//div[contains(@class, 'plays-play-by-play')]/*[1]").\
                    find_element(By.XPATH, ".//div[@class='rally-playrow-play-by-play right']").text
                serving = "Guest"
            except NoSuchElementException:
                serving = "Host"
            try:  # If the point is an ace:
                ace = point.find_element(By.XPATH, ".//span[@class='play-type']").text
                if ace == "- SERVE":
                    serve_effect = "ace"
            except NoSuchElementException:
                pass
            try:  # Check the receiver of the serve:
                receiver = point.find_element(By.XPATH, ".//div[contains(@class, 'plays-play-by-play')]/*[2]").\
                    find_element(By.XPATH, ".//p[@class='shirt-number']").text
                receive_skill = point.find_element(By.XPATH, ".//div[contains(@class, 'plays-play-by-play')]/*[2]").\
                    find_element(By.XPATH, ".//span[@class='skill']").text
                receive_effect = point.find_element(By.XPATH, ".//div[contains(@class, 'plays-play-by-play')]/*[2]").\
                    find_element(By.XPATH, ".//span[@class='effect']").text
            except NoSuchElementException:
                receiver = None
                receive_skill = None
                receive_effect = None

            print(host_score, ":", guest_score, " serving player: ", serving_player, " from team ", serving,
                  " with effect", serve_result,  serve_effect, "\n"
                  "receiver: ", receiver, " with effect", receive_skill, receive_effect, "\n")

        except NoSuchElementException:
            print("No score")
            continue
    print("\n\n\n")


df.to_csv('Matches.csv', index=False)

# Close browser:
driver.quit()
