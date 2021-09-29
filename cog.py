# cog.py
import discord
import traceback
from discord.ext.commands import Bot, Cog,MessageConverter,TextChannelConverter,command
import asyncio
import pandas as pd
import time
import requests
import random
from io import BytesIO

class Slash(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.channel = None 
        self.msgconverter = MessageConverter()
        self.guild = None
        self.sched = None
    @Cog.listener()
    async def on_ready(self):
        print("Ready!")

    @command(name="init",help="Initialize the channel that has banner images")
    async def init(self, ctx, channel):
        authperms = ctx.channel.permissions_for(
            ctx.author
        )
        if not (authperms.administrator):
            return
        try:
            self.channel = await TextChannelConverter().convert(ctx,channel)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            await ctx.send("Not a valid channel")
            return
        self.guild = ctx.guild
        await ctx.send(f"Album channel to {self.channel.name}")
    @command(name="setbanner",help="Set the banner by passing an image argument")
    async def setbanner(self,ctx,img):
        authperms = ctx.channel.permissions_for(
            ctx.author
        )
        if not (authperms.administrator):
            return
        try:
            resp = requests.get(img)
            imgbytes = BytesIO(resp.content)
            #await self.bot.get_guild(ctx.guild.id).edit(banner=imgbytes.read())
            await ctx.guild.edit(banner=resp.content)
            print("banner changed sucessfully")
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            await ctx.send("Couldnt parse image argument")
    
    async def set_random_img(self):
        if self.channel is None:
            return
        messages = await self.channel.history(limit=50).flatten()
        images = [msg for msg in messages if msg.attachments]
        img = random.choice(images)
        try:
            for attachment in img.attachments:
                await self.guild.edit(banner=attachment.read())
                print('banner changed sucessfully')
                break
        except Exception as e:
            print(e)

    def cog_unload(self):
        self.bannerchanger.cancel()

    @command(name="startsched",help="Start schedule of updating images with time")
    async def startsched(self,ctx,timestr):
        authperms = ctx.channel.permissions_for(
            ctx.author
        )
        if not (authperms.administrator):
            return
        self.bannerchanger.cancel()
        try:
            timedelta = pd.to_timedelta(timestr)
        except Exception as e:
            print(e)
            await ctx.send("couldnt parse time string")
            return
        sec,minutes,hours = timedelta.seconds,timedelta.minutes,timedelta.hours
        self.sched = str(timedelta)
        self.bannerchanger.change_interval(seconds=sec,minutes=minutes,hours=hours)
        self.bannerchanger.start()
        

    @command(name="stopsched",help="Stops schedule of updating images with time")
    async def stopsched(self,ctx):
        authperms = ctx.channel.permissions_for(
            ctx.author
        )
        if not (authperms.administrator):
            return
        self.bannerchanger.cancel()

    @command(name="getsched",help="Gets schedule of updating images with time")
    async def getsched(self,ctx):
        authperms = ctx.channel.permissions_for(
            ctx.author
        )
        if not (authperms.administrator):
            return
        await ctx.send(f"The current schedule is {self.sched}")
    


    @tasks.loop(seconds=5.0)
    async def bannerchanger(self):
        await self.set_random_img()

    @bannerchanger.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()







def setup(bot: Bot):
    bot.add_cog(Slash(bot))