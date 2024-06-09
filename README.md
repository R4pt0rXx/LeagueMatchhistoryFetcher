# LeagueMatchhistoryFetcher
This program fetches the last x (max 10) matches of the given Queue of a given user while using an API Key provided by the user.

After successfully fetching the matches, they get copied to the clipboard so you could paste the data in some Excel. 

This program was designed for personal use to track Stats of Custom Games (SCRIMS / PL / UL).

## Parameter:

Match Count - Given a number x between 1 to 10 the last x Matches will be fetched from the users list.

Summoner Name - The program needs a Summoner Name including the Hastag Tag to find the games

API Key - In order to get access to the fetching of the RIOT API, you will need an API Key. Get it from https://developer.riotgames.com/

Match Type - To filter by Queuetype, enter F for Flex Queue, C for Custom Games, S for Solo Queue. Currently there is no method to get all Queuetypes at once.

Role - Enter the Role you want the stats for within the game. 


## Feedback: 

The User will get Feedback within two Text fields (Fetched Match + Messages) providing informations about what the Program did so far. 
