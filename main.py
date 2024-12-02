import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

teams = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS"
}

def get_key_from_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None  # If value is not found

def get_lineups(urls, sample):
    lineups = []
    for url in urls[:sample]:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="lxml")
        data = soup.find_all('p',{'class':'text1'})
        for i in data:
            temp = str(i).split("<br/>")[:]
            time = temp[0].split(" ")
            temp = temp[-6:]
            temp[-1]=temp[-1][:-4]
            temp.append(subtractTime(time[3],time[6]))
            team_name = get_key_from_value(teams, team).split(" ")[-1]
            if(team_name =="Blazers"):
                team_name="Trail Blazers"
            if temp[0].startswith(team_name):
                temp[0]=int(temp[0].split(" ")[-1])
                
                dup = False
                lineupSet = set(temp[1:-1])
                for name in lineupSet:
                    if("\x92" in name):
                        lineupSet.remove(name)
                        lineupSet.add(name[0:name.index("\x92")] + "'" + name[name.index("\x92")+1:])
                for l in lineups:
                    if(lineupSet == l[0]):
                        l[1] += int(temp[0])
                        l[2] = addTime(l[2], temp[-1])
                        dup = True
                if(not dup):
                    lineups.append([lineupSet, int(temp[0]), temp[-1]])
    return Sort(lineups)

def addTime(time1, time2):
    min1, sec1 = time1.split(":")
    min2, sec2 = time2.split(":")
    seconds_delta = int(min1)*60 + int(sec1) + (int(min2)*60 + int(sec2))
    minutes_delta = str(seconds_delta // 60)
    seconds_delta = str(seconds_delta % 60)
    if len(minutes_delta)<2:
        minutes_delta = "0"+str(minutes_delta)
    if len(seconds_delta)<2:
        seconds_delta = "0" + str(seconds_delta)
    return minutes_delta+ ":" +seconds_delta

def subtractTime(time1, time2):
    min1, sec1 = time1.split(":")
    min2, sec2 = time2.split(":")
    seconds_delta = int(min1)*60 + int(sec1) - (int(min2)*60 + int(sec2))
    minutes_delta = str(seconds_delta // 60)
    seconds_delta = str(seconds_delta % 60)
    if len(minutes_delta)<2:
        minutes_delta = "0"+str(minutes_delta)
    if len(seconds_delta)<2:
        seconds_delta = "0" + str(seconds_delta)
    return minutes_delta+ ":" +seconds_delta

def prettyPrint(lineups):
    # Create a list of dictionaries to structure the data
    data = []
    for lineup in lineups:
        data.append({
            "Lineup": ", ".join(lineup[0]),  # Combine the lineup into a single string
            "+/-": lineup[1],               # The +/- value
            "Minutes": lineup[2]            # The minutes
        })
    
    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(data)

    # Remove the index explicitly by resetting and dropping it
    df.reset_index(drop=True, inplace=True)

    # Use st.table to display the data without indexing
    st.dataframe(df)

        
def Sort(sub_li):
    l = len(sub_li)
    for i in range(0, l):
        for j in range(0, l-i-1):
            if (sub_li[j][1] < sub_li[j + 1][1]):
                tempo = sub_li[j]
                sub_li[j]= sub_li[j + 1]
                sub_li[j + 1]= tempo
    return sub_li

st.title("Lineup Tracker")

selected_team = st.selectbox("Select a team", teams.keys())

if selected_team:
    team = teams[selected_team]
    bigsoup = BeautifulSoup(requests.get("http://popcornmachine.net/").text, features="lxml")
    urls = ["https://popcornmachine.net/" + t["href"] for t in bigsoup.find_all("a") if t["href"].startswith("gf") and team in t["href"]]
    games = [str(i + 1) + ". " + urls[i][-6:-3] + " vs " + urls[i][-3:] for i in range(len(urls))]
    if games:
        st.markdown("### Games Available:")

        # Add a scrollable box for the games list
        scrollable_style = """
        <style>
        .scrollable-box {
            height: 200px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
            background-color: #black;
        }
        </style>
        """
        st.markdown(scrollable_style, unsafe_allow_html=True)

        # Combine all games into a single HTML string
        games_html = '<div class="scrollable-box">'
        for game in games:
            games_html += f"<p>{game}</p>"
        games_html += "</div>"

        # Render the entire scrollable box with the games inside
        st.markdown(games_html, unsafe_allow_html=True)
        
        st.write("\n")

        sample = st.number_input("How many games would you like to track?", min_value=1, max_value=len(games))
        if st.button("Find lineups"):
            lineups = get_lineups(urls, sample)
            prettyPrint(lineups)
        
    
    # selected_games = st.selectbox("Select games", games)