from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from tqdm import tqdm
import csv
import time
# Create a dataframe:

match_list = []

# Read the match_links.csv file:
match_links = pd.read_csv('Matches_links2020_copy.csv', header=None).values.tolist()
# Create a Service object using the path to the chromedriver executable
service = Service(executable_path='./chromedriver')

# Set the options for the Chrome browser
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # this option extends execution time
driver = webdriver.Chrome(service=service, options=options)

for year, url in tqdm(match_links[0:3]):

    driver.get(url)

    # Fetch match information:
    try:
        Date = driver.find_element(By.XPATH, "//div[@class='row text-center gridtable games']//div[@class="
                                             "'date khanded']").text
    except NoSuchElementException:
        Date = None
    try:
        Phase = driver.find_element(By.XPATH,
                                    "//div[@class='row text-center']//*[text()='Faza:']/following-sibling::node()"
                                    "[1]").text
    except NoSuchElementException:
        Phase = None
    try:
        Round = driver.find_element(By.XPATH,
                                    "//div[@class='row text-center']//*[text()='Termin:']/following-sibling::node()"
                                    "[1]").text
    except NoSuchElementException:
        Round = None
    try:
        Spectators = driver.find_element(By.XPATH,
                                         "//div[@class='row text-center']//*[text()='Liczba widzów:']/following-"
                                         "sibling::node()[1]").text
    except NoSuchElementException:
        Spectators = None
    try:
        Capacity = driver.find_element(By.XPATH, "//table[@class='right-left spacced']//*[text()='Liczba miejsc "
                                                 "siedzących w hali:']/following-sibling::node()[1]").text
    except NoSuchElementException:
        Capacity = None


    try:
        href_elements = driver.find_element(By.XPATH, "//div[@class='row text-center gridtable games']"). \
            find_elements(By.XPATH, ".//a[@href]")
        href_list = [elem.get_attribute('href') for elem in href_elements]
        unique_href_list = href_list[1:3]

    except NoSuchElementException:
        unique_href_list = None

    # Unused list of players - required for future purposes of counting single players stats
    """
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
    """
    time2 = time.time()
    # Iterate over points:
    if year == 2020:
        driver.switch_to.frame(0)
    else:
        driver.switch_to.frame(2)

    # Wait for the element to be visible on the page
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='play-by-play-container']")))

    sets = driver.find_element(By.XPATH, "//div[@class='play-by-play-container']").find_elements(By.XPATH,
                                                                                                 ".//div[@class='events-container']")

    # Creating match variables:
    set_count = 0
    host_serves = 0
    host_serve_errors = 0
    host_serve_aces = 0
    host_receive_perfect = 0
    host_receive_positive = 0
    host_receive_near_10_feet_line = 0
    host_receive_negative = 0
    host_receive_ball_returned = 0
    host_receive_errors = 0
    host_attacks = 0
    host_attack_errors = 0
    host_attacks_blocked = 0
    host_attacks_scored = 0
    host_block_scored = 0
    host_block_convertible = 0

    guest_serves = 0
    guest_serve_errors = 0
    guest_serve_aces = 0
    guest_receive_perfect = 0
    guest_receive_positive = 0
    guest_receive_near_10_feet_line = 0
    guest_receive_negative = 0
    guest_receive_ball_returned = 0
    guest_receive_errors = 0
    guest_attacks = 0
    guest_attack_errors = 0
    guest_attacks_blocked = 0
    guest_attacks_scored = 0
    guest_block_scored = 0
    guest_block_convertible = 0

    for set in reversed(sets):
        # Store local variables:
        set_count += 1
        Timeouts_host = 0
        Timeouts_guest = 0
        Challenges_host = 0
        Challenges_guest = 0

        # Fetch set information:
        set_info = set.find_element(By.XPATH, ".//vsw-end-set-play-by-play[@class='w100']")
        set_score = set_info.find_elements(By.XPATH, ".//div[@class='result match-result']")
        point_score = set_info.find_elements(By.XPATH, ".//div[@class='result set-result']")
        set_score_host = int(set_score[0].text)
        set_score_guest = int(set_score[1].text)
        point_score_host = int(point_score[0].text)
        point_score_guest = int(point_score[1].text)
        if point_score_host > point_score_guest:
            set_score_host_before = set_score_host - 1
            set_score_guest_before = set_score_guest
        else:
            set_score_host_before = set_score_host
            set_score_guest_before = set_score_guest - 1
        # Unused table of squads - required for future purposes of counting single players stats
        """
        # Fetch list of players for each team:
        squads = set.find_element(By.XPATH, ".//vsw-lineup-play-by-play[@class='w100']")
        host_team = squads.find_element(By.XPATH, ".//div[@class='team']"). \
            find_elements(By.XPATH, ".//span[@class='player-nr']")
        guest_team = squads.find_element(By.XPATH, ".//div[@class='team right']"). \
            find_elements(By.XPATH, ".//span[@class='player-nr']")
        """

        # Fetch points:
        play_by_play = set.find_elements(By.XPATH, ".//div[@class='w100']")
        for point in reversed(play_by_play):
            try:
                host_score = point.find_element(By.XPATH, ".//span[contains(@class, 'left')]").text
                guest_score = point.find_element(By.XPATH, ".//span[contains(@class, 'right')]").text
                serve_result = point.find_element(By.XPATH, ".//span[@class='skill']").text
                serve_effect = point.find_element(By.XPATH, ".//span[@class='effect']").text

                # Check which team scored the point
                try:
                    point_winner = point.find_element(By.XPATH,
                                                      ".//div[@class = 'rally-play-by-play event-play-by-play right']")
                    point_winner = "Guest"
                except NoSuchElementException:
                    point_winner = "Host"

                try:  # If first element of the point contains character "right" in class name (i.e. guest is serving):
                    serving = point.find_element(By.XPATH, ".//div[contains(@class, 'plays-play-by-play')]/*[1]"). \
                        find_element(By.XPATH, ".//div[@class='rally-playrow-play-by-play right']").text
                    serving = "Guest"
                except NoSuchElementException:
                    serving = "Host"

                try:  # Check the serve receive information:
                    receive_skill = point.find_element(By.XPATH,
                                                       ".//div[contains(@class, 'plays-play-by-play')]/*[2]"). \
                        find_element(By.XPATH, ".//span[@class='skill']").text
                    receive_effect = point.find_element(By.XPATH,
                                                        ".//div[contains(@class, 'plays-play-by-play')]/*[2]"). \
                        find_element(By.XPATH, ".//span[@class='effect']").text.strip()
                    # Classify the serve receive effect:
                    if receive_effect == "perfect":
                        if serving == "Host":
                            host_receive_perfect += 1
                        else:
                            guest_receive_perfect += 1
                    elif receive_effect == "positive":
                        if serving == "Host":
                            host_receive_positive += 1
                        else:
                            guest_receive_positive += 1
                    elif receive_effect == "near 10ft line":
                        if serving == "Host":
                            host_receive_near_10_feet_line += 1
                        else:
                            guest_receive_near_10_feet_line += 1
                    elif receive_effect == "negative":
                        if serving == "Host":
                            host_receive_negative += 1
                        else:
                            guest_receive_negative += 1
                    elif receive_effect == "ball returns":
                        if serving == "Host":
                            host_receive_ball_returned += 1
                        else:
                            guest_receive_ball_returned += 1
                    elif receive_effect == "error":
                        if serving == "Host":
                            host_receive_errors += 1
                        else:
                            guest_receive_errors += 1

                except NoSuchElementException:
                    receiver = None
                    receive_skill = None
                    receive_effect = None

                # Calculate net crossing and attack/block stats looping through the touches:
                try:
                    touches = point.find_elements(By.XPATH,
                                                  './/div[contains(@class, "rally-playrow-play-by-play") or contains('
                                                  '@class, "rally-playrow-play-by-play right")]')
                    net_crossings = 0
                    current_side = serving
                    last_touch_side = serving
                    last_touch = None

                    for touch in touches:
                        class_name = touch.get_attribute("class")
                        skill_element = touch.find_element(By.XPATH, ".//span[@class='skill']")
                        skill_text = skill_element.text.strip()
                        effect_element = touch.find_element(By.XPATH, ".//span[@class='effect']")
                        effect_text = effect_element.text.strip()

                        if "right" in class_name:
                            current_side = "Guest"
                            if skill_text == "Attack":
                                guest_attacks += 1
                                if effect_text == "error":
                                    guest_attack_errors += 1
                            elif skill_text == "Serve":
                                guest_serves += 1
                                if effect_text == "error":
                                    guest_serve_errors += 1
                        else:
                            current_side = "Host"
                            if skill_text == "Attack":
                                host_attacks += 1
                                if effect_text == "error":
                                    host_attack_errors += 1
                            elif skill_text == "Serve":
                                host_serves += 1
                                if effect_text == "error":
                                    host_serve_errors += 1

                        if current_side == last_touch_side and last_touch == "Block":
                            if current_side == "Host":
                                host_block_convertible += 1
                            else:
                                guest_block_convertible += 1
                        if skill_text == "Block":
                            last_touch = "Block"
                        else:
                            last_touch = "Other"
                        if current_side != last_touch_side:
                            net_crossings += 1
                        last_touch_side = current_side

                    if skill_text in ["Attack", "Block"] and effect_text != "error":
                        net_crossings += 1

                except NoSuchElementException:
                    print("No right class for game ", url, " set ", set_count, " points ", host_score, ":", guest_score)
                    net_crossings = None

                # Checking final effect of the point:
                try:
                    final_effect = point.find_element(By.XPATH,
                                                      ".//div[contains(@class, 'rally-final-playrow-play-by-play')]")
                    description = final_effect.find_element(By.XPATH, ".//span[@class='description']").text.strip()
                    play_type = final_effect.find_element(By.XPATH, ".//span[@class='play-type']").text.strip()
                    if "right" in final_effect.get_attribute("class"):
                        scored = "Guest"
                    else:
                        scored = "Host"
                    if description == "PLAYER SCORED" and play_type == "- ATTACK":
                        if scored == "Host":
                            host_attacks_scored += 1
                        else:
                            guest_attacks_scored += 1
                    elif description == "PLAYER SCORED" and play_type == "- BLOCK":
                        if scored == "Host":
                            host_block_scored += 1
                            guest_attacks_blocked += 1
                        else:
                            guest_block_scored += 1
                            host_attacks_blocked += 1
                    elif description == "PLAYER SCORED" and play_type == "- SERVE":
                        if scored == "Host":
                            host_serve_aces += 1
                        else:
                            guest_serve_aces += 1
                    else:
                        print("difference for", description, play_type, "in set", set_count, 'of match', url)

                except NoSuchElementException:
                    final_effect = None

                # create a dictionary with the point information to append to set dataframe
                single_point_info = {'MatchID': url,  # Match url
                                     'Date': Date,  # Date of the match
                                     'Year': year,  # Year of the match
                                     'Phase': Phase,  # Phase of the match
                                     'Round': Round,  # Round of the match
                                     'Spectators': Spectators,  # Number of spectators
                                     'Capacity': Capacity,  # Capacity of the hall
                                     'Team1_href': unique_href_list[0],  # Team 1
                                     'Team2_href': unique_href_list[1],
                                     'Set_number': set_count,
                                     'Current_set_score_host': set_score_host,
                                     'Current_set_score_guest': set_score_guest,
                                     'Final_point_score_host': point_score_host,
                                     'Final_point_score_guest': point_score_guest,
                                     'Before_set_score_host': set_score_host_before,
                                     'Before_set_score_guest': set_score_guest_before,
                                     'Current_point_score_host': host_score,
                                     'Current_point_score_guest': guest_score,
                                     'Serving_team': serving,
                                     'Serve_result': serve_result,
                                     'Serve_effect': serve_effect,
                                     'Receive_skill': receive_skill,
                                     'Receive_effect': receive_effect,
                                     'Net_crossings_number': net_crossings,
                                     'Point_winner_team': point_winner,
                                     'Current_timeouts_host': Timeouts_host,
                                     'Current_timeouts_guest': Timeouts_guest,
                                     'Current_challenges_host': Challenges_host,
                                     'Current_challenges_guest': Challenges_guest,
                                     'Current_host_serves': host_serves,
                                     'Current_host_serve_aces': host_serve_aces,
                                     'Current_host_serve_errors': host_serve_errors,
                                     'Current_host_receive_perfect': host_receive_perfect,
                                     'Current_host_receive_positive': host_receive_positive,
                                     'Current_host_receive_near_10_feet_line': host_receive_near_10_feet_line,
                                     'Current_host_receive_negative': host_receive_negative,
                                     'Current_host_receive_ball_returned': host_receive_ball_returned,
                                     'Current_host_receive_errors': host_receive_errors,
                                     'Current_host_attacks': host_attacks,
                                     'Current_host_attack_errors': host_attack_errors,
                                     'Current_host_attacks_blocked': host_attacks_blocked,
                                     'Current_host_attacks_scored': host_attacks_scored,
                                     'Current_host_block_scored': host_block_scored,
                                     'Current_host_block_convertible': host_block_convertible,
                                     'Current_guest_serves': guest_serves,
                                     'Current_guest_serve_aces': guest_serve_aces,
                                     'Current_guest_serve_errors': guest_serve_errors,
                                     'Current_guest_receive_perfect': guest_receive_perfect,
                                     'Current_guest_receive_positive': guest_receive_positive,
                                     'Current_guest_receive_near_10_feet_line': guest_receive_near_10_feet_line,
                                     'Current_guest_receive_negative': guest_receive_negative,
                                     'Current_guest_receive_ball_returned': guest_receive_ball_returned,
                                     'Current_guest_receive_errors': guest_receive_errors,
                                     'Current_guest_attacks': guest_attacks,
                                     'Current_guest_attack_errors': guest_attack_errors,
                                     'Current_guest_attacks_blocked': guest_attacks_blocked,
                                     'Current_guest_attacks_scored': guest_attacks_scored,
                                     'Current_guest_block_points': guest_block_scored,
                                     'Current_guest_block_convertible': guest_block_convertible
                                     }

                match_list.append(single_point_info)



            except NoSuchElementException:
                try:
                    challenge = point.find_element(By.XPATH,
                                                   ".//div[contains(@class, 'video-challenge-play-by-play')]")
                    try:
                        challenge = point.find_element(By.XPATH,
                                                       ".//div[@class='video-challenge-play-by-play event-play-by-play "
                                                       "right']")
                        Challenges_guest += 1
                    except NoSuchElementException:
                        Challenges_host += 1

                except NoSuchElementException:
                    try:
                        timeout = point.find_element(By.XPATH, ".//div[contains(@class, 'timeout-play-by-play')]")
                        try:
                            timeout = point.find_element(By.XPATH,
                                                         ".//div[@class='timeout-play-by-play event-play-by-play "
                                                         "right']")
                            Timeouts_guest += 1
                        except NoSuchElementException:
                            Timeouts_host += 1
                    except NoSuchElementException:
                        pass

# TODO list:
# 1. create frames for each point               Done
# 2. create frames for each set                 Done
# 3. create frames for each match               Done
# 4. Handle "No score" exception -> subs        no subs
# 5. Handle timeouts                            Done
# 6. Create touches dict                        no dict
# 7. Create table position                      Done
# 8. Maybe create recent form?                  different file
# 9. Games crawler                              Done
# 10. Create historical matches comparison      TODO
# 11. Add serve errors and serves to dataframes Done

# Close browser:
driver.quit()
fieldnames = ['MatchID', 'Set_number', 'Date', 'Year', "Phase", "Round", "Spectators", "Capacity", "Team1_href", "Team2_href",
              "Current_set_score_host", "Current_set_score_guest", "Final_point_score_host", "Final_point_score_guest",
                "Before_set_score_host", "Before_set_score_guest", "Current_point_score_host", "Current_point_score_guest",
                "Serving_team", "Serve_result", "Serve_effect", "Receive_skill", "Receive_effect", 'Current_host_serves',
                'Current_host_serve_aces', 'Current_host_serve_errors', 'Current_host_receive_perfect', 'Current_host_receive_positive',
                'Current_host_receive_near_10_feet_line', 'Current_host_receive_negative', 'Current_host_receive_ball_returned',
                'Current_host_receive_errors', 'Current_host_attacks', 'Current_host_attack_errors', 'Current_host_attacks_blocked',
                'Current_host_attacks_scored', 'Current_host_block_scored', 'Current_host_block_convertible', 'Current_guest_serves',
                'Current_guest_serve_aces', 'Current_guest_serve_errors', 'Current_guest_receive_perfect', 'Current_guest_receive_positive',
                'Current_guest_receive_near_10_feet_line', 'Current_guest_receive_negative', 'Current_guest_receive_ball_returned',
                'Current_guest_receive_errors', 'Current_guest_attacks', 'Current_guest_attack_errors', 'Current_guest_attacks_blocked',
                'Current_guest_attacks_scored', 'Current_guest_block_points', 'Current_guest_block_convertible', 'Net_crossings_number',
                'Point_winner_team', 'Current_timeouts_host', 'Current_timeouts_guest', 'Current_challenges_host', 'Current_challenges_guest']

# Write data to CSV
with open("Matches.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(match_list)
