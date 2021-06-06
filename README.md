# MLT
**A discord bot that can do it all. It is able to play music of your choice, make you laugh by sending memes, leveling system that is going to change your role based on how often you chat and much more**
![mlt logo](https://cdn.discordapp.com/attachments/812720653818921012/851100744404172800/dc2c958e7ce72c9f.png)
DOCUMENTATION
```yaml
MUSIC:
  1play/1pl/1p <query> - play a playlist/song through this command
  
  1skip/1sk - skip to the next song in the queue
  
  1loop - make the queue and the songs never stop play(enable/disable)
  
  1mix - mix the queue so the next song is a surprise
  
  1q/1queue - view the queue
  
AUTOROLE:
  1setrole <level> <role_name> - set a role to a certain level. If the role doesnt asixt, it will be created
  
  1remrole <role_name> - removes a role by typing its name. It will delete the role completely from the server
  
  1editrole <role_name> - edit role but for now level is only changeable
  
  1display_roles - dipslays all roles that are in the database for the current server
  
WEATHER:
  1forecast <days> <City/Country> - forecast for x days ahead max is fifteen
  
  1weather <City/Country> - weather for the current day
  
MEMES:
  1memepls/1meme - send a meme by doing a get request to an API
```
MOST IMPORTNANT MODULES
```requests
discord.py
ytdl
pymongo
FFmpeg
```
