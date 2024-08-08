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


import json
import datetime
import os


LOG_FILE_PATH = 'logs/log.txt'


def DictionarySaveJSON(dictionary: dict, name_folder: str, name_file: str):
    """
    Saves a dictionary to a JSON file.

    Args:
        dictionary (dict): The dictionary to be saved.
        name_folder (str): The folder where the JSON file will be saved.
        name_file (str): The name of the JSON file to be saved.

    Example:
        >>> DictionarySaveJSON({'name': 'I', 'age': 29}, 'my_folder', 'my_dictionary.json')
    """
    try:
        output_path = os.path.join(name_folder, name_file)
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(dictionary, file, ensure_ascii=False, indent=4)
        LogMessage('OK', f"Data saved successfully in {output_path}.")
    except Exception as error:
        LogMessage('ERROR', f"An error occurred while saving the dictionary: {error}")


def LogMessage(level: str, message: str):
    """
    Logs a message with a specified level and timestamps it.

    This function prints the log message to the console and appends it to a log file.
    The log entry includes the timestamp, log level, and the message.

    Args:
        level (str): The severity level of the log (e.g., 'INFO', 'WARNING', 'ERROR', 'OK').
        message (str): The message to be logged.

    Example:
        >>> LogMessage("OK", "Processing complete.")
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"    
    print(log_entry)
    with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry + '\n')
