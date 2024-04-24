# python packages: mysql-connector-python git+https://github.com/Rapptz/discord.py

import discord, re
from discord import app_commands
from wm_engine import *
import urllib.request
import urllib.parse
from discord.ext import tasks

topgg_auth = "topgg token goes here"
intents = discord.Intents.default()

class Wordity(discord.AutoShardedClient):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def on_ready(self):
        # broadcast the slash commands
        await tree.sync() #live

        activity = discord.Game(name="word puzzles /help", type=3)
        await self.change_presence(status=discord.Status.online, activity=activity)

        update_topgg.start()

        print('Logged on as', self.user)


    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        # respond on private channel or if mentioned
        if message.channel.type == discord.ChannelType.private or self.user in message.mentions:
            if message.channel.type == discord.ChannelType.private:
                id = message.author.id
            else:
                id = message.channel.id
            utterance = re.sub(r'<@.*>', '', message.content).strip()
            if utterance == "":
                return

            if re.search(r"^\/\s*progress", utterance, flags=re.IGNORECASE):
                mydb = connect()
                if mydb:
                    response = get_report(id, mydb)
                else:
                    response = "Database error! Please try later."
            elif re.search(r"^\/\s*share", utterance, flags=re.IGNORECASE):
                mydb = connect()
                if mydb:
                    response = get_sharable_report(id, mydb)
                else:
                    response = "Database error! Please try later."
            elif re.search(r"^\/\s*new", utterance, flags=re.IGNORECASE):
                numbers = re.findall(r"([0-9]+)", utterance)
                size = 5
                puzzle = -1
                if len(numbers) > 0:
                    size = int(numbers[0])
                if len(numbers) > 1:
                    puzzle = int(numbers[1])
                if size < 4 or size > 7:
                    response = "Sorry, puzzle size must be from 4 to 7."
                else:
                    mydb = connect()
                    if mydb:
                        response = get_new_state(id, mydb, size, puzzle)
                        if type(response) != str:
                            response = make_report(response)
                    else:
                        response = "Database error! Please try later."
            elif re.search(r"^\/\s*help", utterance, flags=re.IGNORECASE):
                response = wordity_help()
            elif re.search(r"^\/\s*support", utterance, flags=re.IGNORECASE):
                response = support()
            elif re.search(r"^\/\s*stats", utterance, flags=re.IGNORECASE):
                mydb = connect()
                response = stats(mydb)
            elif re.search(r"^\/\s*rating", utterance, flags=re.IGNORECASE):
                mydb = connect()
                response = history(message.author.id, mydb, re.search(r"full", utterance, flags=re.IGNORECASE))
            else:
                mydb = connect()
                if mydb:
                    response = one_move(id, utterance.lower().strip(), mydb, message.author.id)
                else:
                    response = "Database error! Please try later."
            await message.channel.send(response)

## create the bot
wm = Wordity()

## Add the SLASH Commands
from typing import Literal

tree = app_commands.CommandTree(wm)

# @tree.command(description="Get some help!")
# @app_commands.describe(topic="Choose a help topic")
# async def help(ctx: discord.Interaction, topic: Literal["basic", "tags", "modifiers", "quickrolls", "success", "multirolls", "shortcuts", "pbta", "ars magica", "bling", "server", "get", "support", "contact", "other"] = "basic"):
#     is_dm, server_owner = flags(ctx)
#     command = "help "+topic
#     await handle_message(ctx.client, ctx, command, ctx.user, ctx.guild,  command, ctx.user, ctx.guild, server_owner, is_dm, ephemeral = True)
#
@tree.command(description="Start a new puzzle.")
@app_commands.describe(size="Word length.")
@app_commands.describe(puzzle="Puzzle id (random if not specified).")
@app_commands.describe(language="Language of the puzzle word.")
@app_commands.describe(rarity="Rarity of the puzzle word.")
async def new(ctx: discord.Interaction,
    size: app_commands.Range[int,4,7] = 5,
    puzzle: app_commands.Range[int,0,2000] = -1,
    language: Literal["English", "Spanish"] = "English",
    rarity: Literal["common", "uncommon"] = "common"
):
    mydb = connect()
    if mydb:
        response = get_new_state(get_id(ctx), mydb, size, puzzle, language=language, rarity=rarity)
        if type(response) != str:
            response = make_report(response)
    else:
        response = "Database error! Please try later."
    await ctx.response.send_message(response)

@tree.command(description="Start a custom puzzle.")
@app_commands.describe(word="The word to guess. Must be 4 to 7 letters long.")
@app_commands.describe(language="Language of the puzzle word.")
async def custom(ctx: discord.Interaction, word: str, language: Literal["English", "Spanish"] = "English"):
    word = word.lower()
    if re.match(r"^[a-z]{4,7}$", word):
        check = check_word(word, language)
        if check == True:
            mydb = connect()
            if mydb:
                response = get_new_state(get_id(ctx), mydb, word=word, language=language)
                if type(response) != str:
                    response = make_report(response)
                await ctx.response.send_message("Custom puzzle started: '"+word+"'.", ephemeral=True)
                await ctx.channel.send(response)
            else:
                await ctx.response.send_message("Database error! Please try later.")
        elif check == None:
            await ctx.response.send_message("Sorry, I do not have a list of "+language+" words of length "+str(len(word))+".")
        else:
            await ctx.response.send_message("Sorry, '"+word+"' is not in my "+language+" word list.", ephemeral=True)
    else:
        await ctx.response.send_message("Sorry, word must consist of 4 to 7 letters only.", ephemeral = True)

@tree.command(description="Show your progress on the current puzzle.")
async def progress(ctx: discord.Interaction):
    mydb = connect()
    if mydb:
        response = get_report(get_id(ctx), mydb)
    else:
        response = "Database error! Please try later."
    await ctx.response.send_message(response)

@tree.command(description="Get your overall rating.")
@app_commands.describe(counts="Include more stats")
@app_commands.describe(language="Language of the puzzle word.")
@app_commands.describe(rarity="Rarity of the puzzle word.")
async def rating(ctx: discord.Interaction, counts: Literal["yes", "no"] = "yes", language: Literal["English", "Spanish"] = "English", rarity: Literal["common", "uncommon"] = "common"):
    mydb = connect()
    if mydb:
        response = history(ctx.user.id, mydb, counts=="yes", language, rarity)
    else:
        response = "Database error! Please try later."
    await ctx.response.send_message(response)

@tree.command(description="Show sharable progress on the current puzzle.")
async def share(ctx: discord.Interaction):
    mydb = connect()
    if mydb:
        response = get_sharable_report(get_id(ctx), mydb)
    else:
        response = "Database error! Please try later."
    await ctx.response.send_message(response)

@tree.command(description="What is Wordity?")
async def help(ctx: discord.Interaction):
    response = wordity_help()
    await ctx.response.send_message(response)

@tree.command(description="Take a guess at the current puzzle.")
@app_commands.describe(word="Your guess")
async def guess(ctx: discord.Interaction, word: str):
    mydb = connect()
    if mydb:
        response = one_move(get_id(ctx), word.lower().strip(), mydb, ctx.user.id)
    else:
        response = "Database error! Please try later."
    await ctx.response.send_message(response)

@tree.command(description="Give back to the bot.")
async def support(ctx: discord.Interaction):
    await ctx.response.send_message(support_message())

def get_id(ctx):
    if ctx.channel.type == discord.ChannelType.private:
        return ctx.user.id
    return ctx.channel.id

def setup(bot):
    bot.add_cog(WordityCog(bot))

@tasks.loop(minutes=30)
async def update_topgg():
    global topgg_auth
    global wm
    if topgg_auth != "":
        data = {
            "server_count": str(len(wm.guilds)),
            "shard_count": str(wm.shard_count)
        }
        data = urllib.parse.urlencode(data).encode()
        req =  urllib.request.Request('https://top.gg/api/bots/topgg id goes here/stats', data=data)
        req.add_header('Authorization', topgg_auth)
        r=urllib.request.urlopen(req)

wm.run("token goes here")
