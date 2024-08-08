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


import argparse
import datetime

from selenium.common.exceptions import WebDriverException
from app.services.selenium.driver.actions import FirefoxWebDriver
from app.services.utils.detected import DetectPlatform
from app.services.files.actions import DictionarySaveJSON, LogMessage


def read_urls_from_file(file_path: str) -> list:
    """
    Reads URLs from a .txt file and returns a list of URLs.
    
    Parameters:
    file_path (str): Path to the .txt file containing URLs.
    
    Returns:
    list: A list of URLs read from the file.
    """
    with open(file_path, 'r') as file:
        urls = file.read().splitlines()
    return urls


def main(url: str, root_path: str = None, platform: str = 'youtube'):
    driver = None
    try:
        # Validar la plataforma
        if platform not in ['youtube', 'twitch', 'tiktok']:
            raise ValueError(f"Plataforma no soportada especificada: '{platform}'.")

        # Inicializar el driver del navegador
        driver = FirefoxWebDriver(root_path)
        driver.StartDriver()

        # Leer URLs
        if url.endswith('.txt'):
            url_list = read_urls_from_file(url)
        else:
            url_list = [url]

        # Procesar cada URL
        for current_url in url_list:
            platform_detected = DetectPlatform(current_url)
            if platform_detected == platform:
                driver.OpenPage(current_url)
                if platform == 'youtube':
                    driver.ScrollDownPageYT()
                    data = driver.ExtractDataPageYT()
                    DictionarySaveJSON(
                        data,
                        name_folder='data/youtube',
                        name_file=f'{datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}_extract_{platform}.json'
                    )
                elif platform == 'twitch':
                    driver.ExtractDataPageTW(
                        name_folder='data/twitch',
                        name_file=f'{datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}_extract_{platform}.csv'
                    )
                elif platform == 'tiktok':
                    driver.ExtractDataPageTK(
                        name_folder='data/tiktok',
                        name_file=f'{datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}_extract_{platform}.json'
                    )
            else:
                LogMessage("WARNING", f'URL: {current_url} no válida para la plataforma {platform}')

    except ValueError as error:
        LogMessage("ERROR", str(error))
    except WebDriverException as error:
        LogMessage("WARNING", "Se produjo una WebDriverException: " + str(error))
    except KeyboardInterrupt:
        LogMessage("WARNING", "Programa interrumpido por el usuario.")
    finally:
        if driver:
            driver.StopDriver()
        LogMessage("OK", 'Ciao')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web data extraction tool.')
    parser.add_argument('url', help='A single URL or a .txt file with URLs (mandatory)')
    parser.add_argument('-r', '--root', default=None, help='Path to Firefox profile (optional)')
    parser.add_argument('-p', '--platform', choices=['youtube', 'twitch', 'tiktok'], required=True, help='Platform to process (mandatory)')

    args = parser.parse_args()

    main(args.url, args.root, args.platform)
