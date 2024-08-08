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
import time
import json
import random
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from app.services.files.actions import LogMessage


def ExtractDataPageTiktok(driver: webdriver.Firefox, name_folder: str, name_file: str):
    """
    Scroll through the webpage, handle captcha, and extract data.

    Args:
        driver: The Selenium WebDriver instance used to interact with the webpage.

    Returns:
        dict: The extracted data or an empty dictionary if an error occurs.
    """
    iteration_count = 0
    data = {}
    previous_wait_time = None
    previous_scroll_wait_time = None
    tolerance = 0.01

    try:
        while True:
            try:
                for _ in range(3):
                    if _check_captcha_exists(driver):
                        print('Captcha detected. Please close the captcha window manually.')
                        input('Press Enter after you have closed the captcha window to continue...')
                        while _check_captcha_exists(driver):
                            print('Captcha still present. Please close it.')
                            input('Press Enter after you have closed the captcha window to continue...')

                    if _check_login(driver):
                        input('Press Enter after you have closed the login window to continue...')
                        while _check_login(driver):
                            print('Login still present. Please close it.')
                            input('Press Enter after you have closed the login window to continue...')
                        if _check_main_page(driver):
                            driver.back()
                            time.sleep(10)
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(1)

                    if _check_main_page(driver):
                        driver.back()
                        time.sleep(4)
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)

                    if _check_without_login(driver):
                        time.sleep(1)
                        try:
                            xpath = '//div[@data-e2e="channel-item"]'
                            driver.find_element(By.XPATH, xpath).click()
                        except:
                            pass
                        
                    # Generate a random wait time for scrolling
                    new_scroll_wait_time = random.uniform(0.8, 1)
                    while previous_scroll_wait_time is not None and abs(new_scroll_wait_time - previous_scroll_wait_time) < tolerance:
                        new_scroll_wait_time = random.uniform(0.8, 2)
                    
                    driver.execute_script("window.scrollBy(0, 420);")
                    time.sleep(new_scroll_wait_time)
                    previous_scroll_wait_time = new_scroll_wait_time

                # Change wait time in each iteration of the while loop
                new_wait_time = random.uniform(1.5, 2)
                while previous_wait_time is not None and abs(new_wait_time - previous_wait_time) < tolerance:
                    new_wait_time = random.uniform(2, 3)
                
                print(f'Waiting for {new_wait_time:.2f} seconds before the next iteration.')
                time.sleep(new_wait_time)
                
                previous_wait_time = new_wait_time
                iteration_count += 1
                
                if iteration_count >= 1:
                    print('Data extraction in progress, please wait...')
                    data = extract_all_data(driver)

                    # Display a message about data extraction status
                    if all(
                        data.get('url_post') and
                        data.get('comment', {}).get('username') and
                        data.get('comment', {}).get('n_like') and
                        data.get('comment', {}).get('n_response') and
                        data.get('comment', {}).get('date')
                    ):
                        print(f"Usernames count: {len(data.get('comment', {}).get('username', []))}")
                        print(f"Comments count: {len(data.get('comment', {}).get('username', []))}")  # Assuming comments and usernames are related
                        print(f"Likes count: {len(data.get('comment', {}).get('n_like', []))}")
                        print(f"Dates count: {len(data.get('comment', {}).get('date', []))}")
                        print(f"Responses count: {len(data.get('comment', {}).get('n_response', []))}")
                        
                        # Ask user for input to continue or exit
                        user_input = input("Type 'exit' to stop or 'c' to keep going: ").strip().lower()
                        if user_input == 'exit':
                            if data:
                                print("Saving data...")
                                LogMessage("INFO", f'Size of "username": {len(data.get("comment", {}).get("username", []))}')
                                LogMessage("INFO", f'Size of "likes": {len(data.get("comment", {}).get("n_like", []))}')
                                LogMessage("INFO", f'Size of "dates": {len(data.get("comment", {}).get("date", []))}')
                                LogMessage("INFO", f'Size of "responses": {len(data.get("comment", {}).get("n_response", []))}')
                                _save_to_json(data, 'out', 'tiktok.json')
                                print("Data saved successfully.")
                            else:
                                print("Data extraction failed or returned no data.")
                            break
                        elif user_input == 'c':
                            continue
                    else:
                        print("Some data was not extracted correctly.")

            except Exception as e:
                print(f'An error occurred: {e}')
                return data
            finally:
                print('Scroll operation reset.')
    finally:
        print('Scroll operation finished.')
        LogMessage("INFO", f'Size of "username": {len(data.get("comment", {}).get("username", []))}')
        LogMessage("INFO", f'Size of "likes": {len(data.get("comment", {}).get("n_like", []))}')
        LogMessage("INFO", f'Size of "dates": {len(data.get("comment", {}).get("date", []))}')
        LogMessage("INFO", f'Size of "responses": {len(data.get("comment", {}).get("n_response", []))}')
        _save_to_json(data, name_folder, name_file)


def extract_all_data(driver) -> dict:
    """
    Extracts all required data from the webpage using concurrent futures.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        dict: A dictionary containing all extracted data.
    """
    with ThreadPoolExecutor() as executor:
        # Create futures for each data extraction function
        futures = {
            executor.submit(_extract_url_post, driver): 'url_post',
            executor.submit(_extract_usernames_comments, driver): 'usernames',
            executor.submit(_extract_comments, driver): 'comments',
            executor.submit(_extract_n_likes, driver): 'likes',
            executor.submit(_extract_dates, driver): 'dates',
            executor.submit(_extract_n_responses, driver): 'responses'
        }
        
        # Initialize results dictionary
        results = {}
        
        # Collect results from futures
        for future in as_completed(futures):
            key = futures[future]
            try:
                result = future.result()
                if key in ['usernames', 'comments', 'likes', 'responses', 'dates']:
                    if key not in results:
                        results[key] = result
                else:
                    results[key] = result
            except Exception as e:
                print(f'Error executing {key}: {e}')
        
        # Assemble the final structure
        data = {
            "date_scraping": "2024-07-30 03:18:56",  # Replace with dynamic timestamp if needed
            "url_post": results.get('url_post', ''),
            "comment": {
                "username": results.get('usernames', []),
                "n_like": results.get('likes', []),
                "n_response": results.get('responses', []),
                "date": results.get('dates', [])
            }
        }
        
        # Verify if all results are complete
        all_data_present = all(key in results and results[key] for key in ['url_post', 'usernames', 'comments', 'likes', 'responses', 'dates',])
        if all_data_present:
            print("Data extraction completed successfully.")
        else:
            print("Some data was not extracted correctly.")
        
        return data


def _save_to_json(data: dict, name_folder: str, name_file: str) -> None:
    """
    Saves the extracted data to a JSON file.

    Args:
        data (dict): The data to save.
        name_folder (str): The folder name where data will be saved.
        name_file (str): The file name for saving the extracted data.

    Returns:
        None
    """
    try:
        output_path = os.path.join(name_folder, name_file)
        os.makedirs(name_folder, exist_ok=True)  # Create the folder if it does not exist
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        print('OK', f"Data saved successfully in {output_path}.")
    except Exception as error:
        print('ERROR', f"An error occurred while saving the dictionary: {error}")


def _extract_url_post(driver: webdriver.Firefox) -> str:
    """
    Extracts the current URL of the post.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        str: The current URL of the post.
    """
    try:
        return driver.current_url
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_usernames_comments(driver: webdriver.Firefox) -> list:
    """
    Extracts usernames from comments on the webpage.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        list: A list of usernames.
    """
    try:
        elements = []
        xpath = '//div[contains(@class, "css-1i7ohvi-DivCommentItemContainer")]'
        header_elements = driver.find_elements(By.XPATH, xpath)
        for element in header_elements:
            user_xpath = './/a'
            user_element = element.find_element(By.XPATH, user_xpath)
            user_link = user_element.get_attribute('href')
            elements.append(user_link)
        return elements
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return elements
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return elements


def _extract_comments(driver: webdriver.Firefox) -> list:
    """
    Extracts comments from the webpage.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        list: A list of comments.
    """
    try:
        elements = []
        xpath = '//div[@class="css-1i7ohvi-DivCommentItemContainer eo72wou0"]'
        for element in driver.find_elements(By.XPATH, xpath):
            xpath1 = './/p[@class="css-xm2h10-PCommentText e1g2efjf6"]/span'
            button = element.find_element(By.XPATH, xpath1)
            text = button.text or button.get_attribute('href')
            elements.append(text)
        return elements
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return elements
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return elements


def _extract_n_likes(driver: webdriver.Firefox) -> list:
    """
    Extracts the number of likes from the webpage.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        list: A list of like counts.
    """
    try:
        elements = []
        xpath = '//div[@class="css-1i7ohvi-DivCommentItemContainer eo72wou0"]'
        for element in driver.find_elements(By.XPATH, xpath):
            xpath1 = './/span[@class="css-gb2mrc-SpanCount ezxoskx3"]'
            button = element.find_element(By.XPATH, xpath1)
            text = button.text or button.get_attribute('href')
            elements.append(text)
        return elements
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return elements
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return elements


def _extract_dates(driver: webdriver.Firefox) -> list:
    """
    Extracts dates from the comments on the webpage.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        list: A list of dates.
    """
    try:
        elements = []
        xpath = '//div[contains(@class, "css-1i7ohvi-DivCommentItemContainer")]'
        header_elements = driver.find_elements(By.XPATH, xpath)
        for element in header_elements:
            user_xpath = './/span[contains(@class, "css-1esugaz-SpanCreatedTime")]'
            user_element = element.find_element(By.XPATH, user_xpath)
            user_link = user_element.text
            elements.append(user_link)
        return elements
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return elements
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return elements


def _extract_n_responses(driver) -> list:
    """
    Extracts the number of responses from comments on the webpage.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        list: A list of response counts or zeros.
    """
    try:
        elements = []
        xpath = '//div[contains(@class, "css-1i7ohvi-DivCommentItemContainer")]'
        header_elements = driver.find_elements(By.XPATH, xpath)
        for element in header_elements:
            user_xpath = './/p[contains(@class, "css-16xv7y2-PReplyActionTex")]'
            try:
                user_element = element.find_element(By.XPATH, user_xpath)
                user_link = user_element.text
                elements.append(user_link)
            except:
                elements.append(0)
        return elements
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return elements
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        print("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return elements


def _check_captcha_exists(driver: webdriver.Firefox) -> bool:
    """
    Checks if a captcha is present on the page.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        bool: True if captcha exists, otherwise False.
    """
    try:
        xpath = '//a[@id="verify-bar-close"]'
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False


def _check_login(driver: webdriver.Firefox) -> bool:
    """
    Checks if a login form is present on the page.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        bool: True if login form exists, otherwise False.
    """
    try:
        xpath = '//a[@id="loginContainer"]'
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False


def _check_main_page(driver: webdriver.Firefox) -> bool:
    """
    Checks if the main page content is present.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        bool: True if main page content exists, otherwise False.
    """
    try:
        xpath = '//div[@id="main-content-others_homepage"]'
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False


def _check_without_login(driver: webdriver.Firefox) -> bool:
    """
    Checks if the login container is not present on the page.

    Args:
        driver (webdriver.Firefox): The Selenium WebDriver instance.

    Returns:
        bool: True if login container does not exist, otherwise False.
    """
    try:
        xpath = '//div[@id="loginContainer"]'
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False
