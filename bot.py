from typing import final
import asyncio
import math
import time

import discord
from requests.utils import from_key_val_list
from serpapi import GoogleSearch
from discord import Intents,Client,Message
from discord.ext import commands
import trip as t
import os
from dotenv import load_dotenv


load_dotenv()
token: final(str) = os.getenv('BOTKEY')
serpKey: final(str) = os.getenv('SERPAPIKEY')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

bot.repeat: bool = False
bot.tripDictionary:dict = {}


@bot.event
async def on_ready()->None:
    print(f'{bot.user} is now running!')


@bot.command()
async def test(ctx):
    print("test")
    await ctx.send("test")

@bot.command()
async def mkTrip(ctx, input):
    await ctx.send("Im BAK BITCHES")
    tripParamiters = input.split(",",4)
    depID = tripParamiters[0]
    ariID = tripParamiters[1]
    outD = tripParamiters[2]
    retD = tripParamiters[3]

    newTrip: t = t.trip(depID,ariID,outD,retD)
    bot.tripDictionary[newTrip.tripName] = newTrip
    await ctx.send("New Trip Made : " + str(newTrip.tripName))
    await ref(ctx)

@bot.command()
async def ref(ctx):
    results:dict = {}

    for tripName in bot.tripDictionary: # for object in dictinary
        trip = bot.tripDictionary[tripName] # accessing the values of each object
        results = query(trip)
        #processing and printing data
        data = extract(results)
        await refineMsg(ctx,data)

@bot.command()
async def daily(ctx, input)-> None:
    #used to control if a search is done every day
    if input == 'y':
        await ctx.send(" OHHHHHHH YAH BABBYYYYYYY")
        bot.repeat = True
    if input == 'n':
        bot.repeat = False
        await ctx.send("CYA BOZO IM OUT DIS BIH,")
    await dailyLoop(ctx)

async def dailyLoop(ctx):
    #dose a query every 24 hours
    while (bot.repeat):
        await ref(ctx)
        await asyncio.sleep(86400)

async def sendMsg(message: Message, user_message: str) -> None:

        await message.author.send(user_message)

def query(trip):
    #serpAPI search paramiters
    param = {
        "engine": "google_flights",
        "departure_id": trip.departure_id,
        "arrival_id": trip.arrival_id,
        "outbound_date": trip.outbound_date,
        "return_date": trip.return_date,
        "currency": "USD",
        "hl": "en",
        "api_key": serpKey,
        "sort_by": [2]
    }

    search = GoogleSearch(param)
    results = search.get_dict()
    #returns a dictinary of all data pulled from the api
    return results

def extract(result):

    bestFlights: dict = result['other_flights'] #pulling data
    #the below is used to store the final data we want
    bigDic: dict = {}
    flightCount: int = 1

    for flightsObject in bestFlights:
        if flightCount <= 3: #limits the query to the first 3 flights

            #this is needed because each object in Best Flights is a dictionary, so to access specific data I need to go a layer deeper
            flightList = flightsObject['flights']
            flight = flightList[0]

            #stores data of each flight
            flightData: dict = {'price': '', 'duration': '', 'layover': '', 'depToken': ''}

            #pulling data
            p: str = flightsObject['price']
            dur: str = flightsObject['total_duration']
            depToken: str = flightsObject['departure_token']

            try: # checks if there is a layover or not

                layoverDic: dict = flightsObject['layovers']
                layoverData: dict = layoverExtract(layoverDic)
                flightData.update({'price':p ,'duration': dur,'layover':layoverData,'depToken':depToken})

            except KeyError:

               # print("This flight dose not have layover.")
                flightData.update({'price':p ,'duration': dur,'layover':'NA','depToken':depToken})
            bigDic.update({flightCount: flightData})
            flightCount += 1  # index
        else: break
    return bigDic


def layoverExtract(layoverDic):
    #dictinary to return pulled data
    layovereData: dict = {'location': '','duration':''}

    #pulling data
    for flight in layoverDic:
        loc: str = flight['name']
        dur: str = flight['duration']
    #storing data
    layovereData.update({'location' : loc,'duration': dur})
    return layovereData

async def refineMsg(ctx,data):

    for flight in data: #pulling and assigning data

        await ctx.send("this is option " + str(flight))

        # formating and grabing data
        flightData = data[flight]
        p: int = int(flightData['price'])
        price: str = str(round(p,2))
        d: float = (int(flightData['duration'])) / 60
        duration: str = str(round(d,2))
        layover: str = flightData['layover']

        await ctx.send("this flight will cost $" + price)
        await ctx.send("this flight is %s hours long (including the layover duration" % (duration))

        #checking for layovers
        if layover != 'NA':
            layLoc: str = str(layover['location'])
            layD: float = (int(layover['duration'])) / 60
            layDur: str = str(round(layD,2))

            await ctx.send("this flight has a layover in " + layLoc)
            await ctx.send("the layover is %s hours long " %layDur)

        else: await ctx.send("This flight dose not have a layover")

        await ctx.send("______")
    print("done!")
    await ctx.send("done!")


#myTrip = t.trip("MSP","KEF","2025-06-13","2025-06-26")
#thisQ = query(myTrip)

def runBot() -> None:
    asyncio.run(bot.run(token = token))

