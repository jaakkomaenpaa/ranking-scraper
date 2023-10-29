"""
A script that can be used for scraping ranking data from official BWF world 
ranking and writing it to a csv file, which can then be imported to Excel, 
for example. 


NOTES:

Only scrapes the data for men's singles

Navigating through all the links takes a long time, the whole process lasts 
at least 10 minutes.

The player_dict will have some troubles if there are multiple players with
the exact same full name, since it currently uses the player's name as the 
key. Only one of those players will be stored. 


MANUAL WORK:
(to scrape data from a different ranking week than 2023-42)

In get_players() function, the page amount should be checked manually for the
wanted ranking week. The ranking link should also be changed to the week
that the data is wanted from (currently on week 2023-42).

In get_tournaments() function, the indicated link (also currently on week 
2023-42) should be changed to the one that is corresponding to the wanted 
ranking week.

Modify the LINKS_TO_IGNORE list. At least all the team events should be 
included in it, since they might cause some trouble.

"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from Player import Player
import csv

# Fill with tournament links to be ignored, for example:
LINKS_TO_IGNORE = [
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=194880', # Africa team champs
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=194881', # Europe team champs
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=194882', # Asia team champs
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=194883', # Pan american cup
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=194884', # Oceania team champs
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=216359', # Asian team champs
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=191182', # European team qual
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=191183', # European team qual
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=191184', # European team qual
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=191185', # European team qual
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=191187', # European team qual
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=212148', # FISU University team
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=212253', # FISU University indiv
    'https://www.tournamentsoftware.com/ranking/tournament.aspx?id=36972&tournament=201693', # Sudirman cup
]


player_dict = {}
tournament_links = []

driver = webdriver.Chrome()
driver.implicitly_wait(2)


def accept_cookies():
    try:
        accept = driver.find_element(By.XPATH, '/html/body/div/div/div/main/form/div[1]/button[1]')
        if accept.is_displayed():
            accept.click()
    except NoSuchElementException:
        pass


def write_file():
    with open('player_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header = ['Country', 'Player']

        for week in range(1, 53):
            header.append(f"Week {week}")

        header.extend(['OVR', 'Tournaments', 'All points', 'Confederation'])
        writer.writerow(header)

        for player in player_dict.values():
            try:
                writer.writerow(player.get_csv_row())
            except UnicodeEncodeError:
                continue


# Finds and stores the relevant data of all the ranked players
def get_players():

    # Handling all 18 pages
    # CHECK PAGE AMOUNT MANUALLY
    for page in range(1, 19):
        # CHANGE TO WANTED WEEK
        driver.get(
            f"https://www.tournamentsoftware.com/ranking/category.aspx?id=36972&category=472&C472FOC=&p={page}&ps=100"
        )
        accept_cookies()

        # Handling one page
        table_rows = driver.find_elements(By.TAG_NAME, 'tr')
        print(len(table_rows))

        for row in range(2, len(table_rows) - 1):
            # Handling a single player
            row_cells = table_rows[row].find_elements(By.TAG_NAME, 'td')

            abbreviation = row_cells[3].text
            player_name = row_cells[4].text
            confederation = row_cells[9].text
            weeks = []
            points = []

            player_dict[player_name] = Player(player_name, abbreviation, confederation, weeks, points)


# Gets links for the tournaments that are counted on the ranking 
def get_tournaments():
    # CHANGE TO WANTED WEEK
    driver.get("https://www.tournamentsoftware.com/ranking/tournaments.aspx?id=36972")

    accept_cookies()

    table = driver.find_element(By.TAG_NAME, 'tbody')
    table_rows = table.find_elements(By.TAG_NAME, 'tr')
    for row in table_rows:
        week = row.find_elements(By.TAG_NAME, 'td')[2].text
        link_container = row.find_elements(By.TAG_NAME, 'td')[1]
        link = link_container.find_element(By.TAG_NAME, 'a')
        tournament_links.append([link.get_attribute('href'), week])


# Adds all the points from the tournaments to the players
def get_points():
    get_tournaments()
    for tournament in tournament_links:
        [link, week] = tournament

        if link in LINKS_TO_IGNORE:
            continue

        driver.get(link)
        print('Week ', week)
        accept_cookies()

        table = driver.find_element(By.TAG_NAME, 'tbody')
        table_rows = table.find_elements(By.TAG_NAME, 'tr')

        for row in table_rows:

            # Script only focuses on men's singles so stops before going onto
            # the other events
            if row.text == "Women's Singles":
                break

            try:
                cells = row.find_elements(By.TAG_NAME, 'td')
                player_name = cells[1].text
                points = cells[4].text

                player = player_dict.get(player_name)
                if player is None:
                    continue
                player.add_points(int(points))
                player.add_weeks(week)

            except (NoSuchElementException, IndexError):
                continue


def main():

    get_players()
    get_points()

    driver.quit()
    write_file()


if __name__ == "__main__":
    main()
