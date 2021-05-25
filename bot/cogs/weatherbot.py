from re import I
import discord
from discord.ext import commands
from discord.ext.commands.core import command
import requests
import json
import datetime
import typing as t
class NoCityName(commands.CommandError):
    pass
class NoCityFound(commands.CommandError):
    pass


class WeatherBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def build_url(self, base_url, city, api_key):
        return base_url+"q="+city+"&appid="+api_key

    @commands.command()
    async def weather(self,ctx,*, city_name):
        if not len(city_name):
            raise NoCityName
        
        print(len(city_name))
        url = self.build_url("http://api.openweathermap.org/data/2.5/weather?",
                             city_name, "2888fecacf9ba5007679e4fd079a7388")
        res = requests.get(url)
        x = res.json()
        if x["cod"] == "401" or x["cod"] == "404":
            raise NoCityFound
        else:
            info = x["main"]
            curr_temp = info["temp"] - 273.15
            curr_humidity = info["humidity"]
            z = x["weather"]
            curr_temp
            weather_description = z[0]["description"]

            await ctx.send(f"`` Temperature = {int(curr_temp)} C\n humidity (in percentage) = {str(curr_humidity)} \n description = {str(weather_description)}``")
    @commands.command()
    async def forecast(self, ctx, city_name, days = 3):
        url = self.build_url("http://api.openweathermap.org/data/2.5/forecast?",
                             city_name, "2888fecacf9ba5007679e4fd079a7388")
        forecast = []
        lista = []
        res = requests.get(url)
        x = res.json()
        if days > 30 or days < 1:
            await ctx.send("aight mate, cant be over 30 neither lower than one, so imma jus say 'you dumb, dumb'")
            pass
        if x["cod"] == "401" or x["cod"] == "404":
            raise NoCityFound
        else:
            for i in range(days):
                info = x["list"][i]["main"]
                lista.append(int(info["temp_min"] - 273.15))
                lista.append(int(info["temp_max"] - 273.15))
                lista.append(int(info["humidity"]))
                
                z = x["list"][i]["weather"]
                
                lista.append(z[0]["description"])
                forecast.append(list(lista))
                
                lista.clear()
        a = datetime.datetime.today()

        date_list = [a + datetime.timedelta(days=x) for x in range(days)]
        msg = ""
        for i in range(days):
            msg +=f'``Forecast for {str(date_list[i].day)} - {str(date_list[i].strftime("%B"))} - {str(date_list[i].year)}``\n'
            msg += f'``` Max Temperature = {forecast[i][0]} C\n Min Temperature = {forecast[i][1]} C\n humidity (in percentage) = {forecast[i][2]} \n description = {forecast[i][3]}```\n'
        await ctx.send(msg)
    @weather.error
    async def weather_exc(self, ctx, exc):
        if isinstance(exc, NoCityName):
            await ctx.send("You must enter a city name after the command")
        elif isinstance(exc, NoCityFound):
            await ctx.send("I couldn't find a city with this name")
    
def setup(bot):
    bot.add_cog(WeatherBot(bot))
