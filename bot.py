import hikari, lightbulb, json, logging

import northstar

config = json.load(open("./config.json"))
token = config["token"]

bot = lightbulb.BotApp(token=token,prefix=None,help_class=None)
try:
    northstarAPI = northstar.northstar()
except:
    logging.warn("FAILED TO INIT NORTHSTAR API: CONTINUING WITH NONE")
    northstarAPI = None

@bot.command
@lightbulb.command("ping", "how dead am i", ephemeral=True,guilds=[925509769958162462])
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency * 1_000:.0f}ms")

@bot.command
@lightbulb.command("help", "what the hell do i do",guilds=[925509769958162462])
@lightbulb.implements(lightbulb.SlashCommand)
async def help(ctx) -> None:
    embed = hikari.Embed(title = "Help")
    embed.add_field("/ping",   "Sends you my latency.")
    embed.add_field("/search", "Searches for servers.\nOptions:\n`keyword`- Required, what to search for.\n`field`, Optional, tells you what you want to search for. Defaults to `name`.")
    embed.add_field("/info",   "Gives some more info on a server.\nOptions:\n    `name`- Required, the exact name of the server.")
    embed.add_field("/status", "Tells you about the masterserver and some other general stats.")
    await ctx.respond(embed)

@bot.command
@lightbulb.option("keyword", "keyword to search for",required=True)
@lightbulb.option("field", "what exactly to search for",required=False,default="name")
@lightbulb.command("search", "where the hell are those servers",guilds=[925509769958162462])
@lightbulb.implements(lightbulb.SlashCommand)
async def search(ctx) -> None:
    if northstarAPI == None:
        await ohshit(ctx)
        return
    embed = hikari.Embed(title = "Servers")
    northstarAPI.updateServers()
    servers = northstarAPI.searchServers(ctx.options.keyword.lower(), northstarAPI.getServers(), field=ctx.options.field)
    for server in servers:
        embed.add_field(server["name"], server["description"])
    await ctx.respond(embed)

@bot.command
@lightbulb.option("name", "the name of the server you want info for",required=True)
@lightbulb.command("info", "what the fuck is that server",guilds=[925509769958162462])
@lightbulb.implements(lightbulb.SlashCommand)
async def info(ctx) -> None:
    if northstarAPI == None:
        await ohshit(ctx)
        return
    northstarAPI.updateServers()
    servers = northstarAPI.getServers()
    realServer = None
    for server in servers:
        if server["name"] == ctx.options.name:
            realServer = server
            break
    if realServer == None:
        await ctx.respond("Server not found!", flags=hikari.MessageFlags.EPHEMERAL)
    else:
        server = realServer
        embed = hikari.Embed(title=server["name"], description=server["description"])
        embed.set_footer(server["id"])
        embed.add_field("Map", server["map"]) #TODO: convert between raw map names and normal map names
        embed.add_field("Players", f"{server['playerCount']}/{server['maxPlayers']}")
        await ctx.respond(embed)

@bot.command
@lightbulb.command("status", "check out the masterserver info and general stats",guilds=[925509769958162462])
@lightbulb.implements(lightbulb.SlashCommand)
async def status(ctx) -> None:
    if northstarAPI == None:
        embed = hikari.Embed(title="status", description="Oh no! The masterserver is/was down. Attempting reconnect...")
        await ctx.respond(embed)
        await ohshit(ctx)
    else:
        northstarAPI.updateServers()

        serverCount = 0
        playerCount = 0 
        maxPlayers  = 0 
        for server in northstarAPI.servers:
            serverCount += 1
            playerCount += server["playerCount"]
            maxPlayers  += server["maxPlayers"]

        embed = hikari.Embed(title="Status", description="Masterserver is running properly!")
        embed.add_field("Servers online", str(serverCount))
        embed.add_field("Players online", f"{playerCount}/{maxPlayers}")
        await ctx.respond(embed)

async def ohshit(ctx):
    try:
        northstarAPI.__init__()
        logging.info("ABLE TO RE-INIT NORTHSTAR API")
        await ctx.respond("We were able to re-init the API! Try your command again.", flags=hikari.MessageFlags.EPHEMERAL)
    except:
        logging.warn("STILL CANNOT ACCESS NORTHSTAR API")
        await ctx.respond("Oh shit, the API is still down. Try again later!", flags=hikari.MessageFlags.EPHEMERAL)
bot.run()
