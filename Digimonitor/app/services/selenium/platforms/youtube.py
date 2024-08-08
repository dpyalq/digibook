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
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from app.services.files.actions import LogMessage


def ScrollDownPageYouTube(driver: webdriver.Firefox) -> None:
    """
    Scrolls down the loaded YouTube page to load more content.

    This function uses JavaScript to determine the total height of the page and scrolls down
    incrementally to load more comments or dynamically loaded elements. It checks if the DOM has
    changed after each scroll to adjust the scrolling accordingly.

    Args:
        driver (webdriver.Firefox): The Firefox WebDriver instance used to interact with the page.
    """
    script = """
    return {
        pageHeight: Math.max(document.body.scrollHeight, document.body.offsetHeight, 
                            document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight)
    };
    """
    dimensions = driver.execute_script(script)
    page_init_height = dimensions['pageHeight']
    LogMessage("INFO", f"Initial total page height: {page_init_height}")
    max_attempts = 3  # Maximum number of verification attempts
    current_attempt = 0
    while current_attempt < max_attempts:
        # Scroll down incrementally
        for _ in range(5):  # Perform 5 small scrolls down
            driver.execute_script("window.scrollBy(0, 449);")  # Scroll down 449 pixels
            time.sleep(0.5)  # Small pause between scrolls
        # Scroll up slightly to adjust
        driver.execute_script("window.scrollBy(0, -169);")
        time.sleep(0.5)
        # Get the new page dimensions after scroll
        dimensions = driver.execute_script(script)
        page_last_height = dimensions['pageHeight']
        LogMessage("INFO", f"New total page height: {page_last_height}")
        # Check if the page height has stopped updating
        if page_init_height == page_last_height:
            current_attempt += 1
            LogMessage('INFO', f"Attempt {current_attempt}: Page height has not changed.")
            driver.execute_script("window.scrollBy(0, 449);")  # Scroll down a bit more to test
            time.sleep(0.5)
        else:
            page_init_height = page_last_height
            current_attempt = 0  # Reset verification attempts
    LogMessage("INFO", "Scrolling complete or maximum attempts reached.")


def ExtractDataPageYouTube(driver: webdriver.Firefox) -> dict:
    """
    Extracts data from a YouTube video page using the specified WebDriver instance.

    This function retrieves various details about the video, including the URL, channel name,
    subscriber count, title, description, views, comments, likes, and more. The extracted
    data is returned as a dictionary.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        dict: A dictionary containing extracted data, including:
            - date_scraping (str): Timestamp of when the data was scraped.
            - url_post (str): The URL of the YouTube post.
            - channel_name (str): Name of the channel.
            - count_subscribers (str): Number of subscribers to the channel.
            - id_channel (str): Unique ID of the channel (URL).
            - title (str): Title of the video.
            - description (str): Description of the video.
            - views (str): Number of views for the video.
            - count_comment (str): Number of comments on the video.
            - count_likes (str): Number of likes for the video.
            - upload (str): Upload date of the video.
            - comment (dict): Dictionary containing details about comments, including:
                - username (list of str): Usernames of commenters.
                - emoji (list of list): Emojis used in comments.
                - n_like (list of str): Number of likes on each comment.
                - n_response (list of str): Number of responses to each comment.
                - date (list of str): Dates of each comment.
    """
    data = {
        "date_scraping": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url_post": _extract_url_post(driver),
        "channel_name": _extract_name_channel(driver),
        "count_subscribers": _extract_count_subscribers(driver),
        "id_channel": _extract_id_channel(driver),
        "title": _extract_title_post(driver),
        'description': _extract_description(driver),
        "views": _extract_count_views(driver),
        "count_comment": _extract_count_comments(driver),
        "count_likes": _extract_count_likes(driver),
        "upload": _extract_upload(driver),
        "comment": {
            "username": _extract_usernames(driver),
            "emoji": _extract_comments_emojis(driver),
            "n_like": _extract_n_likes(driver),
            "n_response": _extract_n_responses(driver),
            "date": _extract_dates(driver)
        }
    }
    # Print sizes of extracted data for verification
    username = len(data['comment'].get('username', []))
    emoji = len(data['comment'].get('emoji', []))
    n_like = len(data['comment'].get('n_like', []))
    n_response = len(data['comment'].get('n_response', []))
    date = len(data['comment'].get('date', []))
    LogMessage("INFO", f'Size of "username": {username}')
    LogMessage("INFO", f'Size of "emoji": {emoji}')
    LogMessage("INFO", f'Size of "n_like": {n_like}')
    LogMessage("INFO", f'Size of "n_response": {n_response}')
    LogMessage("INFO", f'Size of "date": {date}')
    return data


def _extract_url_post(driver: webdriver.Firefox) -> str:
    """
    Extracts the URL of the YouTube post.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        str: The URL of the YouTube post.
    """
    try:
        return driver.current_url
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_name_channel(driver: webdriver.Firefox) -> str:
    """
    Extracts the name of the channel from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        str: The name of the channel.
    """
    try:
        xpath = '//yt-formatted-string[@class="style-scope ytd-channel-name complex-string"]/a'
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return 'None'
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_id_channel(driver: webdriver.Firefox) -> str:
    """
    Extracts the ID of the channel from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        str: The ID of the channel.
    """
    try:
        xpath = '//yt-formatted-string[@class="style-scope ytd-channel-name complex-string"]/a'
        return driver.find_element(By.XPATH, xpath).get_attribute('href')
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return 'None'
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_count_subscribers(driver: webdriver.Firefox) -> str:
    """
    Extracts the number of subscribers for the channel from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        str: The number of subscribers.
    """
    try:
        xpath = '//yt-formatted-string[@class="style-scope ytd-video-owner-renderer"]'
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return 'None'
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_title_post(driver: webdriver.Firefox) -> str:
    """
    Extracts the title of the YouTube video from the page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        str: The title of the video.
    """
    try:
        xpath = '//h1/yt-formatted-string[@class="style-scope ytd-watch-metadata"]'
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return 'None'
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_count_views(driver: webdriver.Firefox) -> str:
    """
    Extracts the number of views for the video from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        str: The number of views.
    """
    xpath1 = '//span[@class="style-scope yt-formatted-string bold"]'
    xpath2 = '//div[@id="info-container"]'
    try:
        # Attempt to extract the view count using the primary XPath
        return driver.find_element(By.XPATH, xpath1).text
    except NoSuchElementException:
        # If primary XPath fails, attempt to extract from the alternative XPath
        try:
            get_item = driver.find_element(By.XPATH, xpath2)
            text = get_item.text.replace('\n', '').strip()
            return text
        except NoSuchElementException:
            # Handle the case where neither XPath finds the element
            func_name = inspect.currentframe().f_code.co_name
            docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
            LogMessage("WARNING", f"Element with XPath '{xpath1}' and '{xpath2}' not found in function '{func_name}'. Docstring: {docstring}")
            return 'None'
    except Exception as e:
        # Handle any other unexpected errors
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_count_comments(driver: webdriver.Firefox) -> str:
    """
    Extracts the number of comments on the video from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        str: The number of comments.
    """
    try:
        xpath = '//yt-formatted-string[@class="count-text style-scope ytd-comments-header-renderer"]//span[@class="style-scope yt-formatted-string"]'
        elements = [item.text for item in driver.find_elements(By.XPATH, xpath)]
        return ' '.join(elements)
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return 'None'
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_count_likes(driver: webdriver.Firefox) -> str:
    """
    Extracts the number of likes for the video from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        str: The number of likes.
    """
    try:
        xpath = '//button[@class="yt-spec-button-shape-next yt-spec-button-shape-next--tonal yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m yt-spec-button-shape-next--icon-leading yt-spec-button-shape-next--segmented-start"]//div[@class="yt-spec-button-shape-next__button-text-content"]'
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return 'None'
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_upload(driver: webdriver.Firefox) -> str:
    """
    Extracts the upload date of the video from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        str: The upload date, or 'None' if unable to extract.
    """
    xpath1 = '//span[@class="style-scope yt-formatted-string bold"]'
    xpath2 = '//div[@id="info-container"]'
    try:
        return driver.find_elements(By.XPATH, xpath1)[2].text
    except NoSuchElementException:
        try:
            get_item = driver.find_element(By.XPATH, xpath2)
            text = get_item.text.replace('\n', '').strip()
            return text
        except NoSuchElementException:
            func_name = inspect.currentframe().f_code.co_name
            docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
            LogMessage("WARNING", f"Element with XPath '{xpath1}' and '{xpath2}' not found in function '{func_name}'. Docstring: {docstring}")
            return 'None'
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_description(driver: webdriver.Firefox) -> str:
    """
    Extracts the description of the video from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        str: The description of the video.
    """
    xpath1 = '//tp-yt-paper-button[@id="expand"]'
    xpath2 = '//yt-attributed-string[@class="style-scope ytd-text-inline-expander"]'
    xpath3 = '//ytd-text-inline-expander[@id="description-inline-expander"]'
    try:
        driver.find_element(By.XPATH, xpath1).click()        
        try:
            return driver.find_element(By.XPATH, xpath2).text
        except NoSuchElementException:
            func_name = inspect.currentframe().f_code.co_name
            docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
            LogMessage("WARNING", f"Element with XPath '{xpath2}' not found in function '{func_name}'. Docstring: {docstring}")
            return 'None'
    except NoSuchElementException:
        try:
            return driver.find_element(By.XPATH, xpath3).text
        except NoSuchElementException:
            func_name = inspect.currentframe().f_code.co_name
            docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
            LogMessage("WARNING", f"Element with XPath '{xpath1}' and '{xpath3}' not found in function '{func_name}'. Docstring: {docstring}")
            return 'None'
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return 'None'


def _extract_usernames(driver: webdriver.Firefox) -> list:
    """
    Extracts the usernames of commenters from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        list of str: List of usernames.
    """
    xpath = '//div[@id="header-author"]'
    elements = []
    try:
        # Get the list of header-author elements
        header_elements = driver.find_elements(By.XPATH, xpath)
        for element in header_elements:
            # Extract class names using JavaScript
            class_names = driver.execute_script(
                "return arguments[0].getAttribute('class');", element
            )
            class_names = class_names.strip().split()  # Split into a list of class names
            # Build dynamic XPath for a and span elements
            xpath1 = f'.//a[contains(@class, "{class_names[0]}")]' if class_names else './/a'
            xpath2 = f'.//span[contains(@class, "{class_names[0]}")]' if class_names else './/span'
            text = None
            try:
                # Try to find the a element and get its text
                button = element.find_element(By.XPATH, xpath1)
                text = button.text or button.get_attribute('href')
            except Exception:
                try:
                    # If not found, try to find the span element and get its text
                    button = element.find_element(By.XPATH, xpath2)
                    text = button.text
                except Exception:
                    text = None
            elements.append(text)
        return elements
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return elements
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return elements


def _extract_comments_emojis(driver: webdriver.Firefox) -> list:
    """
    Extracts comments and emojis used in comments from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        list of list: List containing comments and corresponding emojis.
    """
    elements = []
    try:
        xpath = '//yt-attributed-string[@id="content-text"] | //img[@class="yt-core-image yt-core-attributed-string__image-element yt-core-attributed-string__image-element--image-alignment-vertical-center yt-core-image--content-mode-scale-to-fill yt-core-image--loaded"]'
        comments = driver.find_elements(By.XPATH, xpath)
        for comment in comments:
            com = comment.text
            emojis_items = comment.find_elements(By.XPATH, './/img[@class="yt-core-image yt-core-attributed-string__image-element yt-core-attributed-string__image-element--image-alignment-vertical-center yt-core-image--content-mode-scale-to-fill yt-core-image--loaded"]')
            emoji_element = [element.get_attribute('src') for element in emojis_items]
            comentario = [com, emoji_element]
            elements.append(comentario)
        for i in range(len(elements)):
            for item in elements:
                if len(item[0]) == 0 and len(item[1]) == 0:
                    elements.remove(item)
        return elements
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return elements
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return elements


def _extract_n_likes(driver: webdriver.Firefox) -> list:
    """
    Extracts the number of likes on each comment from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        list of str: List of likes count for each comment.
    """
    try:
        xpath = '//span[@id="vote-count-middle"]'
        return [item.text for item in driver.find_elements(By.XPATH, xpath)]
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return []
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return []


def _extract_n_responses(driver: webdriver.Firefox) -> list:
    """
    Extracts the number of responses to each comment from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        list of str: List of responses count for each comment.
    """
    elements = []
    try:
        xpath = '//div[@class=" style-scope ytd-item-section-renderer style-scope ytd-item-section-renderer"]//ytd-comment-thread-renderer[@class="style-scope ytd-item-section-renderer"]'
        get_items = driver.find_elements(By.XPATH, xpath)    
        for comment_thread in get_items:
            xpath1 = './/button[@class="yt-spec-button-shape-next yt-spec-button-shape-next--text yt-spec-button-shape-next--call-to-action yt-spec-button-shape-next--size-m yt-spec-button-shape-next--icon-leading yt-spec-button-shape-next--align-by-text"]'
            try:
                button = comment_thread.find_element(By.XPATH, xpath1)
                element = button.get_attribute('aria-label')
            except Exception:
                element = None
            elements.append(element)
        return elements
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return elements
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return elements


def _extract_dates(driver: webdriver.Firefox) -> list:
    """
    Extracts the dates of comments from the YouTube page.

    Args:
        driver (webdriver.Firefox): The WebDriver instance used to interact with the YouTube page.

    Returns:
        list of str: List of dates for each comment.
    """
    try:
        xpath = '//span[@id="published-time-text"]/a'
        return [i.text for i in driver.find_elements(By.XPATH, xpath)]
    except NoSuchElementException:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"Element with XPath '{xpath}' not found in function '{func_name}'. Docstring: {docstring}")
        return []
    except Exception as e:
        func_name = inspect.currentframe().f_code.co_name
        docstring = inspect.getdoc(inspect.currentframe().f_back.f_locals[func_name])
        LogMessage("WARNING", f"An error occurred in function '{func_name}'. Docstring: {docstring}. Error: {str(e)}")
        return []
