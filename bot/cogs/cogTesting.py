from bot.cogs.weatherbot import WeatherBot

from bot.cogs.weatherbot import WeatherBot

import unittest
async def search_song(self,query):
    video_output = VideosSearch(query, limit = 1)
    return video_output.result()["result"][0]["link"] if video_output is not None else None


