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


import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from app.services.selenium.platforms.youtube import ScrollDownPageYouTube, ExtractDataPageYouTube
from app.services.selenium.platforms.twitch import ExtractDataPageTwitch
from app.services.selenium.platforms.tiktok import ExtractDataPageTiktok
from app.services.files.actions import LogMessage


class FirefoxWebDriver:
    def __init__(self, root_path: str = None):
        """
        Initializes an instance of FirefoxWebDriver.

        Args:
            root_path (str, optional): The root directory where the Firefox profile is located.
                                        If not provided, the default is None, meaning that the WebDriver
                                        will start with a default profile.
        """
        self.root_path = root_path
        self.driver = None


    def StartDriver(self) -> webdriver.Firefox:
        """
        Initializes a WebDriver instance for the Firefox browser.

        This method configures the WebDriver options, including specifying an existing Firefox profile.
        The 'headless' mode can be enabled or disabled by uncommenting or commenting the corresponding option.

        Returns:
            webdriver.Firefox: An instance of the Firefox WebDriver.
        """
        try:
            options = Options()
            if self.root_path:
                options.add_argument("-profile")
                options.add_argument(self.root_path)
            # options.add_argument('--headless')  # Uncomment to enable headless mode
            self.driver = webdriver.Firefox(options=options)
            LogMessage("OK", "Starting WebDriver.")
            return self.driver
        except Exception as e:
            LogMessage("ERROR", f"Failed to start WebDriver: {e}")
            raise


    def OpenPage(self, url: str) -> None:
        """
        Opens a web page in the Firefox WebDriver instance.

        This function receives a URL and uses the WebDriver instance to load the corresponding page. 
        A fixed wait time is included after opening the page.

        Args:
            url (str): The URL of the web page to be opened.
        """
        self.driver.get(url)
        self.driver.maximize_window()
        LogMessage('OK', f"Opened URL: {url}")
        time.sleep(9)


    def ScrollDownPageYT(self):
        """
        Scrolls down the page to load additional content, such as comments, on YouTube.

        This method initiates the scrolling process to load more content. The scrolling action is
        performed using the `ScrollDownPageYouTube` function.
        """
        LogMessage("OK", "Scrolling process to load comments has started.")
        ScrollDownPageYouTube(self.driver)
        LogMessage("OK", "End of scrolling.")


    def StopDriver(self):
        """
        Closes and terminates the Firefox WebDriver instance.

        This function ensures that the browser is properly closed and releases any resources associated
        with the WebDriver instance.
        """
        if self.driver:
            self.driver.quit()
            LogMessage('OK', "Stopping WebDriver.")
        else:
            LogMessage('WARNING', "WebDriver was not running.")


    def ExtractDataPageYT(self) -> dict:
        """
        Extracts data from a YouTube page.

        This method initiates the data extraction process using the `ExtractDataPageYouTube` function,
        and returns the extracted data.

        Returns:
            dict: A dictionary containing the extracted data from the YouTube page.
        """
        LogMessage("OK", "Data extraction process has started.")
        data = ExtractDataPageYouTube(self.driver)
        LogMessage("OK", "Data extraction process has been completed satisfactorily.")
        return data


    def ExtractDataPageTW(self, name_folder: str, name_file: str):
        """
        Extracts data from a Twitch page.

        This method initiates the data extraction process using the `ExtractDataPageTwitch` function.
        """
        LogMessage("OK", "Data extraction process for Twitch has started.")
        ExtractDataPageTwitch(self.driver, name_folder, name_file)
        LogMessage("OK", "Data extraction process for Twitch has been completed.")


    def ExtractDataPageTK(self, name_folder: str, name_file: str):
        """
        Extracts data from a TikTok page.

        This method initiates the data extraction process using the `ExtractDataPageTiktok` function.

        Parameters:
        name_folder (str): The folder path where the extracted data will be saved.
        name_file (str): The filename for the JSON file where data will be stored.
        """
        LogMessage("OK", "Data extraction process for TikTok has started.")
        ExtractDataPageTiktok(self.driver, name_folder, name_file)
        LogMessage("OK", "Data extraction process for TikTok has been completed.")
