from discord.ext import commands,tasks
from dotenv import load_dotenv
import discord
import asyncio
import os
import youtube_dl

# TOKEN debe ser una variable de entorno, para eso usamos dotenv
load_dotenv()
# Esto va a leer la variable de entorno TOKEN
TOKEN = os.getenv("TU TOKEN")

# Variables de uso general
intents = discord.Intents().all() # Para esto aun no tengo explicacion, pero si no lo pones no sirve.
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents) 


# Bloque para el formato de videos/audio de YT que bajaran a Discord
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_option = {
    'format': 'bestaudio/best',
    'restrictfilenames': True ,
    'noplaylist': True ,
    'nocheckcertificate': True ,
    'ignoreerrors': False , 
    'logtostderr': False ,
    'quiet': True ,
    'no_warnings': True ,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# FFMPEG es un modulo de modulos para el encode, decode y todo el procesamiento de audio
# -vn en las opciones es para quitar el video de la repro.
ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_option)


# Vamos a crear la clase acceder, tomar, bajar y colocar
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume = 0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""
        
    @classmethod
    async def from_url(ctx, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download= not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
    

# Este es el metodo para que el bot entre al canal de voz.
@bot.command(name = 'join')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send('{} is not connected to a voice channel'.format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()
        
# Este sera el comando para poner play a una cancion.
@bot.command(name='play')
async def p(ctx,url):
    server = ctx.message.guild
    voice_channel = server.voice_client
    async with ctx.typing():
        filename = await YTDLSource.from_url(url, loop = bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(executable = "C:\\Users\\iscda\\Documents\\bragi\\ffmpeg-2023-04-17-git-65e537b833-full_build\\bin", source=filename))
    await ctx.send('**Bragi esta reproduciendo: ** {}'.format(filename))
    
    
 # Comando para pausar la cancion. 
@bot.command(name= 'pausa')
async def ps(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("Bragi ha pausado la musica o no estas reproduciendo nada")
        
        
# Comando para continua o quitar pausa.
@bot.command(name= 'resume')
async def r(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("Bragi no esta reproduciendo nada")

      
# Comando para abandonar el bot
@bot.command(name='leave')
async def l(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Bragi esta desconectado")
        

# Comando para detener la musica.
@bot.command(name='stop')
async def s(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("Bragi no esta reproduciendo nada")
        
# Para que corra el bot
if __name__ == "__main__" :
    bot.run("TU TOKEN")
