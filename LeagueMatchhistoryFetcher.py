import pyperclip
import sys
import argparse
import datetime
import riotwatcher
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import os

LOL_REGION = 'euw1'
RIOT_REGION = "europe"
POSITIONS = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]

root = Tk()
root.title("Matchhistory to Clipboard Generator")
root.geometry("750x600")

# Label + Entry for Match Count
labelMatches = Label(root, text="How many Matches?")
labelMatches.grid(row=0, column=0)
labelMTypeE = Label(root, text="(Maximum 10 | Minimum 1)")
labelMTypeE.grid(row=0, column=2)
matchesc = Entry(root, width=30)
matchesc.grid(row=0, column=1, padx=15, pady=5)
matchesc.insert(0,1)

# Label + Entry Player Name
labelName = Label(root, text="Summoner Name:")
labelName.grid(row=1, column=0)
labelMTypeE = Label(root, text="(Enter your Riot ID including #)")
labelMTypeE.grid(row=1, column=2)
lNamec = Entry(root, width=30)
lNamec.grid(row=1, column=1, padx=15, pady=5)

# Label + Entry for API Key
labelAPI = Label(root, text="API Key:")
labelAPI.grid(row=2, column=0)
labelApiKE = Label(root, text="(Get the API Key from 'https://developer.riotgames.com/')")
labelApiKE.grid(row=2, column=2)
bullet = "\u2022" #specifies bullet character
lAPIc = Entry(root, show=bullet, width=30)
lAPIc.grid(row=2, column=1, padx=15, pady=5)

# Matchtype
labelMType = Label(root, text="Match Type:")
labelMType.grid(row=3, column=0)
labelMTypeE = Label(root, text="(F = Flex Queue, C = Custom Games, S = Solo Queue)")
labelMTypeE.grid(row=3, column=2)
matchTc = Entry(root, width=30)
matchTc.grid(row=3, column=1, padx=15, pady=5)
matchTc.insert(0,"F")

# Rolle
rolleName = Label(root, text="Rolle:")
rolleName.grid(row=4, column=0)
rolleNameE = Label(root, text="(Top, Jungle, Mid, ADC, Support)")
rolleNameE.grid(row=4, column=2)
rolleNamec = Entry(root, width=30)
rolleNamec.grid(row=4, column=1, padx=15, pady=5)

# Fetched Matches Entry
FetchedMatchLabel = Label(root, text= "Fetched Match:")
FetchedMatchLabel.grid(row=7, column=0)
FetchedMatchEntry = Text(root, width=65, height=10)
FetchedMatchEntry.insert(1.0, "No Match fetched yet!")
FetchedMatchEntry.grid(row=7, column=1, columnspan= 2, padx=15, pady=5)

# Error Entry
ErrorLabel = Label(root, text="Messages:")
ErrorLabel.grid(row=8, column=0)
ErrorEntry = Text(root, width=65, height=8)
ErrorEntry.insert(1.0, "No Errors yet!")
ErrorEntry.grid(row=8, column=1, columnspan= 2, padx=15, pady=5)

# Clear Button for everything
def button_clear():
    matchesc.delete(0, END)
    lNamec.delete(0, END)
    lAPIc.delete(0, END)
    matchTc.delete(0, END)
    matchesc.insert(0, 1)
    matchTc.insert(0,"F")

# Clear Button
clearbtn = Button(root, text="Clear", command=button_clear)
clearbtn.grid(row=6, column=0)
        
# Fetch Matches Function
def fetchMatches():
    # Some Variables
    matchCount = int(matchesc.get())
    tempName = lNamec.get()
    tempApi = lAPIc.get()
    APIlen = len(tempApi)
    tempMT = matchTc.get()  
    ErrorEntry.delete(1.0, END)
    FetchedMatchEntry.delete(1.0, END)
    rolleGet = rolleNamec.get()
    if(tempMT == "C"):
        queuetype = 0
    if(tempMT == "F"):
        queuetype = 440
    if(tempMT == "S"):
        queuetype = 420
    
    # Check Inputs
    if matchesc.get().isdigit() == False:
        messagebox.showwarning("Invalid Input in", "Invadlid Input, 'Matches' needs to be a number")
        return
    elif int(matchCount) < 1:
        messagebox.showwarning("Invalid Input", "Cannot be less than 1")
        return
    elif int(matchCount) > 10:
        messagebox.showwarning("Invalid Input", "Cannot be greater than 10")
        return
    elif tempName.count('#') != 1:
        messagebox.showwarning("Invalid Input", "Wrong format of the Summoner Name")
        return
    elif APIlen <= 10:
        messagebox.showwarning("Invalid Input", "API Key might be wrong (too small)")
        return
    elif tempMT != 'F' and tempMT != 'C' and tempMT != 'S':
        messagebox.showwarning("Invalid Input", "Invalid Game Type")
        return
    elif rolleGet != "Top" and rolleGet != "Jungle" and rolleGet != "Mid" and rolleGet != "ADC" and rolleGet != "Support": 
        messagebox.showwarning("Invalid Input", "Invalid Role")
        return
    
    # Split GameName and Tag
    gameName, tagline = tempName.split('#')

    # Setup API Key
    LOL_WATCHER = riotwatcher.LolWatcher(tempApi)
    RIOT_WATCHER = riotwatcher.RiotWatcher(tempApi)

    # Get PUUID (three attempts)
    puuid = None
    for _ in range(0, 3):
        try:
            puuid = RIOT_WATCHER.account.by_riot_id(RIOT_REGION, gameName, tagline)["puuid"]
            break
        except riotwatcher.ApiError as err:
            if err.response.status_code == 429:
                ErrorEntry.insert(1.0,"We should retry in again...\n")
                continue
            elif err.response.status_code == 403:
                ErrorEntry.delete(1.0, END)
                ErrorEntry.insert(1.0,"API Key expired/invalid!\n")
                break
            else:
                ErrorEntry.delete(1.0, END)
                ErrorEntry.insert(1.0,"Unknown error occured while fetching puuid:\n{err}")
                break
    if puuid is None:
        ErrorEntry.insert(1.0,"Could not request PUUID for some reason!\n")

    # Get match list (three attempts)
    lastGamesList = None
    for _ in range(0, 3):
        try:
            lastGamesList = LOL_WATCHER.match.matchlist_by_puuid(LOL_REGION, puuid, start=0, count=10, queue=queuetype)
        except riotwatcher.ApiError as err:
            ErrorEntry.insert(1.0,"Unknown error occured while fetching match list:\n{err}")
    if lastGamesList is None:
        ErrorEntry.insert(1.0,"Could not request match list.")

    # Get champion ddragon file (for correct champion names)
    try:
        champs = LOL_WATCHER.data_dragon.champions('14.11.1')  #UPDATE PATCH HERE if a new champ is missing
        #champfile = open('E:\Sonstiges\PythonProj\champst.json','r', encoding='utf-8')
        #champs = champfile.read()
        #champfile.close()
    except riotwatcher.ApiError as err:
        ErrorEntry.insert(1.0,"Unknown error while fetching the ddragon:\n{err}")

    # Get matches
    matchIdx = 0
    remainingMatches = matchCount
    statStrings = {position: "" for position in POSITIONS}
    while remainingMatches > 0 and matchIdx < len(lastGamesList):
        try:
            stats = LOL_WATCHER.match.by_id(LOL_REGION, lastGamesList[matchIdx])
            matchIdx += 1

            # Ignore custom games with less than 10 players
            if len(stats["metadata"]["participants"]) != 10:
                continue

            # Find player
            participantIndex = next((i for i, p in enumerate(stats["info"]["participants"]) if
                                     p["riotIdGameName"].lower() == gameName.lower()), None)
            if participantIndex is None:
                ErrorEntry.delete(1.0, END)
                ErrorEntry.insert(1.0,"Script error: Could not find player with game name {gameName} in the game with id")
                break
            participant = stats["info"]["participants"][participantIndex]

            # Check if champ is known
            if participant["championName"] not in champs["data"]:
                ErrorEntry.delete(1.0, END)
                ErrorEntry.insert(1.0,"Unknown champion you probably have to update the version of the ddragon-champion.json-file")
                break

            # Show Games in Log
            gameTime = datetime.datetime.fromtimestamp(stats["info"]["gameEndTimestamp"] / 1000).strftime('%c')
            FetchedMatchEntry.insert(1.0, f'Match found at {gameTime} as {champs["data"][participant["championName"]]["name"]} '
                f'({participant["kills"]}/{participant["deaths"]}/{participant["assists"]}) \n')
            

            # Store stats for game
            remainingMatches -= 1
            participantTeam = participant["teamId"]
            for position in POSITIONS:
                # Find player in position
                positionIndex = next((i for i, p in enumerate(stats["info"]["participants"]) if
                                      p["teamPosition"] == position and p["teamId"] == participantTeam), None)
                if positionIndex is None:
                    ErrorEntry.delete(1.0, END)
                    ErrorEntry.insert(1.0,'Script error: Could not find player with position {position} and game name {gameName} '
                        f'in team {participantTeam} in the game with id {lastGamesList[matchIdx]}!')
                    break
                positionParticipant = stats["info"]["participants"][positionIndex]

                # Find lane opponent
                laneOpponentIndex = next((i for i, p in enumerate(stats["info"]["participants"]) if
                                          p["teamPosition"] == position and p["teamId"] != participantTeam), None)
                if laneOpponentIndex is None:
                    ErrorEntry.delete(1.0, END)
                    ErrorEntry.insert(1.0,
                        f'Script error: Could not find lane opponent of player with position {position} '
                        f'and game name {gameName} in team {participantTeam} '
                        f'in the game with id {lastGamesList[matchIdx]}!')
                    break
                laneOpponent = stats["info"]["participants"][laneOpponentIndex]

                # Construct strings (tab characters indicate a new column, newlines a new row)
                statStrings[
                    position] += (f'{champs["data"][positionParticipant["championName"]]["name"]}\t'
                                  f'{champs["data"][laneOpponent["championName"]]["name"]}\t'
                                  f'{positionParticipant["kills"]}\t'
                                  f'{positionParticipant["deaths"]}\t'
                                  f'{positionParticipant["assists"]}\t'
                                  f'{positionParticipant["wardsPlaced"]}\t'
                                  f'{positionParticipant["visionWardsBoughtInGame"]}\t'
                                  f'{positionParticipant["wardsKilled"]}\t'
                                  f'{positionParticipant["totalDamageDealtToChampions"]}\t'
                                  f'''{positionParticipant["totalMinionsKilled"] + 
                                     positionParticipant["neutralMinionsKilled"]}\n''')
        except riotwatcher.ApiError as err:
            ErrorEntry.insert(1.0,'Unknown error occured while fetching match {lastGamesList[matchIdx]}:\n{err}')

    if matchIdx >= len(lastGamesList):
        ErrorEntry.delete(1.0, END)
        ErrorEntry.insert(1.0,
            f'Didn\'t fetch any more games (increase the "count" parameter of matchlist_by_puuid '
            f'if you are terribly interested)')
    
    if(rolleGet == "Top"):
        pyperclip.copy(statStrings['TOP'])
        ErrorEntry.delete(1.0, END)
        ErrorEntry.insert(1.0,f'Copied stats for position Top to the clipboard.')
    if(rolleGet == "Jungle"):
        pyperclip.copy(statStrings['JUNGLE'])
        ErrorEntry.delete(1.0, END)
        ErrorEntry.insert(1.0,f'Copied stats for position Jungle to the clipboard.')
    if(rolleGet == "Mid"):
        pyperclip.copy(statStrings['MIDDLE'])
        ErrorEntry.delete(1.0, END)
        ErrorEntry.insert(1.0,f'Copied stats for position Mid to the clipboard.')
    if(rolleGet == "ADC"):
        pyperclip.copy(statStrings['BOTTOM'])
        ErrorEntry.delete(1.0, END)
        ErrorEntry.insert(1.0,f'Copied stats for position ADC to the clipboard.')
    if(rolleGet == "Support"):
        pyperclip.copy(statStrings['UTILITY'])
        ErrorEntry.delete(1.0, END)
        ErrorEntry.insert(1.0,f'Copied stats for position Support to the clipboard.')

# Generate Matches Button Configuration
fetchMatchesBtn = Button(root, text="Fetch Matches", command=fetchMatches)
fetchMatchesBtn.grid(row=6, column=1)

def on_close():
    response=messagebox.askyesno('Exit','Are you sure you want to exit?')
    if response:
        root.destroy()
root.protocol('WM_DELETE_WINDOW',on_close)

root.mainloop()