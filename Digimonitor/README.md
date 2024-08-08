# Digimonitor
OSINT Tool for Digital Networks


## Installation
```consol
pip install -r requirements.txt
```


## Usage
To search for only one link:
```consol
python -m digimonitor -p youtube "https://www.youtube.com/watch?v="
```

To search a list of links:
```consol
python -m digimonitor -p youtube path/folder/lista_urls.txt
```

```consol
usage: digimonitor.py [-h] [-r ROOT] -p {youtube,twitch,tiktok} url

Web data extraction tool.

positional arguments:
  url                   A single URL or a .txt file with URLs (mandatory)

options:
  -h, --help            show this help message and exit
  -r ROOT, --root ROOT  Path to Firefox profile (optional)
  -p {youtube,twitch,tiktok}, --platform {youtube,twitch,tiktok}
                        Platform to process (mandatory)
```

## License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html). See the LICENSE file for more information.


## Copyright Registration Number (INDAUTOR)

```Número de registro
03-2024-080111090400-14
```

Copyright (C) 2024 [Daniel Alcalá](https://github.com/dpyalq)
