# Digimonitor is part of the DIGIBOOK collection.
# DIGIBOOK Copyright (C) 2024 Daniel Alcalá.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import inspect
import datetime
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
from app.services.files.actions import LogMessage


def ExtractDataPageTwitch(driver: webdriver.Firefox,  name_folder: str, name_file: str) -> dict:
    """
    Extracts data from a Twitch chat page.

    This function continuously scrapes chat data from a Twitch page, collecting usernames and comments.
    It handles duplicate comments, saves data to a CSV file when a threshold is reached, and provides
    mechanisms to clear chat messages when they exceed a certain length.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance used to interact with the web page.

    Returns:
        dict: A dictionary containing the extracted chat data, with keys 'date_scraping', 'Username', and 'Comment'.
    """
    db = {'date_scraping': [], 'time_live': [], 'views': [],  'username': [], 'comment': []}
    seen_comments = set()  # Set to track unique comments
    while True:
        try:
            if _check_offline(driver):
                try:
                    for username, comment in zip(usernames, comments):
                        if comment not in seen_comments:
                            seen_comments.add(comment)
                            db['date_scraping'].append(now)
                            db['time_live'].append(time_live)
                            db['views'].append(views)
                            db['username'].append(username)
                            db['comment'].append(comment)
                    _create_csv(db,  name_folder, name_file)
                except:
                    break
            if _check_element_comments_presence(driver):
                time.sleep(0.1)
                # Get current HTML content
                html_content = driver.page_source
                # Extract usernames and comments
                time_live = _extract_time_live(driver)
                views = _extract_views(driver)
                usernames = _extract_usernames_comments(html_content)
                comments = _extract_texts_comments(html_content)
                # Get current timestamp
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if len(usernames) == len(comments) and len(usernames) <= 140:
                    # Filter unique comments
                    for username, comment in zip(usernames, comments):
                        if comment not in seen_comments:
                            seen_comments.add(comment)
                            db['date_scraping'].append(now)
                            db['time_live'].append(time_live)
                            db['views'].append(views)
                            db['username'].append(username)
                            db['comment'].append(comment)
                    # Check if the dictionary exceeds 1000 elements
                    if len(db['date_scraping']) > 1000:
                        LogMessage("OK", "Number of elements in the dictionary has exceeded 1000. Saving data...")
                        _create_csv(db,  name_folder, name_file)
                        db = {'date_scraping': [], 'time_live': [], 'views': [],  'username': [], 'comment': []}  # Reset the dictionary
                    time.sleep(0.3)
                    # Print the size of each list for verification
                    print(len(db['date_scraping']))
                    print(len(db['time_live']))
                    print(len(db['views']))
                    print(len(db['username']))
                    print(len(db['comment']))
                elif len(usernames) > 140 or len(comments) > 140:
                    print("Either usernames or comments exceed 140 characters.")
                    script = """
                    var elements = document.querySelectorAll('.chat-line__message');
                    elements.forEach(function(element) {
                        element.parentNode.removeChild(element);
                    });
                    """
                    driver.execute_script(script)
            else:
                driver.refresh()
        except KeyboardInterrupt:
            LogMessage("WARNING", "Keyboard interruption detected. Ending scraping.")
            for username, comment in zip(usernames, comments):
                if comment not in seen_comments:
                    seen_comments.add(comment)
                    db['date_scraping'].append(now)
                    db['time_live'].append(time_live)
                    db['views'].append(views)
                    db['username'].append(username)
                    db['comment'].append(comment)
            _create_csv(db,  name_folder, name_file)
            break
        except Exception as e:
            for username, comment in zip(usernames, comments):
                if comment not in seen_comments:
                    seen_comments.add(comment)
                    db['date_scraping'].append(now)
                    db['time_live'].append(time_live)
                    db['views'].append(views)
                    db['username'].append(username)
                    db['comment'].append(comment)
            _create_csv(db,  name_folder, name_file)
            break
    return db


def _extract_usernames_comments(html_content: str) -> list:
    """
    Extracts usernames from the provided HTML content.

    This function parses the HTML content to extract usernames from Twitch chat messages.

    Args:
        html_content (str): The HTML content of the Twitch chat page.

    Returns:
        list: A list of usernames extracted from the HTML content.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        usernames = [span.get_text() for span in soup.find_all('span', class_='chat-author__display-name')]
        return usernames
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element not found in function '{func_name}'. Docstring: {docstring}")
        return []
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return []


def _extract_texts_comments(html_content: str) -> list:
    """
    Extracts chat messages from the provided HTML content.

    This function parses the HTML content to extract chat messages from Twitch.

    Args:
        html_content (str): The HTML content of the Twitch chat page.

    Returns:
        list: A list of chat messages extracted from the HTML content.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        comments = [span.get_text() for span in soup.find_all('span', attrs={'data-a-target': 'chat-line-message-body'})]
        return comments
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element not found in function '{func_name}'. Docstring: {docstring}")
        return []
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return []


def _extract_views(driver: webdriver.Firefox) -> str:
    try:
        xpath = '//p[@data-a-target="animated-channel-viewers-count"]'
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element not found in function '{func_name}'. Docstring: {docstring}")
        return 'None'
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_time_live(driver: webdriver.Firefox):
    try:
        xpath = '//span[@class="live-time"]'
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element not found in function '{func_name}'. Docstring: {docstring}")
        return []
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return []


def _check_element_comments_presence(driver: webdriver.Firefox) -> bool:
    """
    Checks if a specific element is present on the page.

    This function uses XPath to locate a specific element on the page.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance used to interact with the web page.

    Returns:
        bool: True if the element is found, False otherwise.
    """
    try:
        xpath = "//div[@class='Layout-sc-1xcs6mc-0 InjectLayout-sc-1i43xsx-0 chat-list--default font-scale--default iClcoJ']"
        driver.find_element(By.XPATH, xpath)
        print('Element of comments found.')
        return True
    except Exception as e:
        print(f'Element of comments not found: {e}')
        return False


def _check_offline(driver: webdriver.Firefox) -> bool:
    try:
        xpath = '//div[@class="Layout-sc-1xcs6mc-0 exGAHk channel-status-info channel-status-info--offline"]'
        driver.find_element(By.XPATH, xpath)
        LogMessage("WARNING", "Offline channel.")
        return True
    except Exception as e:
        return False


def _create_csv(data: list, name_folder: str, name_file: str) -> None:
    """
    Creates or appends data to a CSV file.

    This function saves the provided data to a CSV file. If the CSV file does not exist, it will be created. 
    If the file already exists, the new data will be appended to the existing content.

    Args:
        data (list of dict): The data to be saved in the CSV file.
        name_folder (str): The folder where the CSV file will be saved.
        name_file (str): The name of the CSV file.
    """
    df_data = pd.DataFrame(data)
    os.makedirs(name_folder, exist_ok=True)
    csv_file_path = os.path.join(name_folder, name_file)
    if not os.path.isfile(csv_file_path):
        # File does not exist, create and save it
        df_data.to_csv(csv_file_path, index=False)
        LogMessage('OK', f"CSV file created and data saved to {csv_file_path}.")
    else:
        # File exists, append data
        df_existing = pd.read_csv(csv_file_path)
        df_concat = pd.concat([df_existing, df_data], ignore_index=True)
        df_concat.to_csv(csv_file_path, index=False)
        LogMessage('OK', f"Data appended to existing CSV file {csv_file_path}.")
