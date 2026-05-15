import os
import discord
from discord.ext import commands
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot listo")

@bot.tree.command(name="blvjoin", description="Entrar al canal")
async def blvjoin(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Debes estar en un canal de voz.")
        return
    channel = interaction.user.voice.channel
    if interaction.guild.voice_client is None:
        await channel.connect()
        await interaction.response.send_message(f"✅ Entré a {channel.name}")
    else:
        await interaction.response.send_message("✅ Ya estoy conectado.")

@bot.tree.command(name="leave", description="Salir del canal")
async def leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        await vc.disconnect()
        await interaction.response.send_message("👋 Me desconecté.")
    else:
        await interaction.response.send_message("❌ No estoy conectado.")

@bot.tree.command(name="blvplay", description="Reproducir música")
async def blvplay(interaction: discord.Interaction, search: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Debes estar en un canal de voz.")
        return
    await interaction.response.defer()
    channel = interaction.user.voice.channel
    try:
        vc = await channel.connect() if interaction.guild.voice_client is None else interaction.guild.voice_client
    except Exception as e:
        await interaction.followup.send(f"❌ Error al conectar: `{e}`")
        return
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            if not info.get('entries'):
                await interaction.followup.send("❌ No encontré la canción.")
                return
            url = info['entries'][0]['url']
            title = info['entries'][0]['title']
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        vc.stop()
        vc.play(source)
        await interaction.followup.send(f"🎵 Reproduciendo: {title}")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: `{e}`")

token = os.getenv("TOKEN")
if not token:
    raise RuntimeError("TOKEN no configurado.")
bot.run(token)
