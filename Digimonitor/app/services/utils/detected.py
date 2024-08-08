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


import re

def DetectPlatform(url: str) -> str:
    """
    Detects whether the provided URL belongs to YouTube, Twitch, TikTok, or is invalid.

    This function uses regular expressions to identify if the given URL matches
    the patterns for YouTube, Twitch, or TikTok. If the URL matches none of these patterns, it is
    considered invalid.

    Args:
        url (str): The URL to analyze.

    Returns:
        str: The detected platform. It returns 'youtube' if the URL matches YouTube,
             'twitch' if it matches Twitch, 'tiktok' if it matches TikTok, and 'INVALIDURL' if it matches neither.
    """
    youtube_pattern = re.compile(r'https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+')
    twitch_pattern = re.compile(r'https?://(www\.)?twitch\.tv/[\w-]+')
    tiktok_pattern = re.compile(r'https?://(www\.)?tiktok\.com/@[\w.]+/video/\d+')

    if youtube_pattern.match(url):
        return 'youtube'
    elif twitch_pattern.match(url):
        return 'twitch'
    elif tiktok_pattern.match(url):
        return 'tiktok'
    else:
        return 'INVALIDURL'
