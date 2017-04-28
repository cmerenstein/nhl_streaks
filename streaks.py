#!/usr/bin/python
import glob

all_streaks = []

def update_winners(winner, loser, row, current_streaks):
    global all_streaks

    try:
        current_streaks[winner].append(row)
    except KeyError:
        current_streaks[winner] = []
        current_streaks[winner].append(row)
    
    try:
        if len(current_streaks[loser]) >= 10:
#            print(len(current_streaks[loser]))
            all_streaks.append(current_streaks[loser])
    except KeyError:
        pass

    current_streaks[loser] = []
    
    return current_streaks

def get_streaks(row, current_streaks):

    # figure out who won
    away = row[1]
    away_goals = int(row[2])

    home = row[3]
    home_goals = int(row[4])
            
    if home_goals > away_goals:
        current_streaks = update_winners(home, away, row, current_streaks)
            
    elif away_goals > home_goals:
        current_streaks = update_winners(away, home, row, current_streaks)

    else: # isn't it kinda weird they used to have ties in hockey?
        try:
            if len(current_streaks[home]) >= 10:
                all_streaks.append(current_streaks[home])
        except KeyError:
            pass
        try: 
            if len(current_streaks[away]) >= 10:
                all_streaks.append(current_streaks[away])
        except KeyError:
            pass
        
        current_streaks[home] = []
        current_streaks[away] = []


    return current_streaks

def adjust_so(row, away_goals, home_goals):
    # they give a goal for a shootout win but it's not really a goal
    if row[5] == "SO":
        if away_goals > home_goals:
            return (away_goals - 1), home_goals
        else:
            return away_goals, (home_goals - 1)
    else:
        return away_goals, home_goals

def update_goals(row, goal_totals):
    # don't forget we need to keep track of total games played
    # because of the partial lockout season
    away = row[1]
    away_goals = int(row[2])

    home = row[3]
    home_goals = int(row[4])

    away_goals, home_goals = adjust_so(row, away_goals, home_goals)

    try:
        goal_totals[away][0] += away_goals
        goal_totals[away][1] += home_goals
        goal_totals[away][2] += 1
    except KeyError:
        goal_totals[away] = [0,0,1]
        goal_totals[away][0] = away_goals
        goal_totals[away][1] = home_goals
    try:
        goal_totals[home][0] += home_goals
        goal_totals[home][1] += away_goals
        goal_totals[home][2] += 1
    except KeyError:
        goal_totals[home] = [0,0,1]
        goal_totals[home][0] = home_goals
        goal_totals[home][1] = away_goals
    
    return goal_totals

def get_streak_team(row):
    away = row[1]
    away_goals = int(row[2])

    home = row[3]
    home_goals = int(row[4])

    if home_goals > away_goals:
        return home
    
    return away

def for_against(row, team): 
    away = row[1]
    away_goals = float(row[2])

    home = row[3]
    home_goals = float(row[4])

    away_goals, home_goals = adjust_so(row, away_goals, home_goals)

    if away == team:
        return away_goals, home_goals
    else:
        return home_goals, away_goals

def add_games_played(row, games_played):
    away = row[1]
    try:
        games_played[away] += 1
    except KeyError:
        games_played[away] = 1

    home = row[3]
    try:
        games_played[home] += 1
    except KeyError:
        games_played[home] = 1
    row.append(games_played[away])
    row.append(games_played[home])
    
    return games_played, row

seasons = {}

for csvfile in glob.glob("seasons/*csv"):
    
    games_played = {} # so we can get info from hockey-reference's play index
    season = csvfile.split("/")[-1].rsplit(".",1)[0]

    print csvfile
    current_streaks = {}
    goal_totals = {} # format - {team:[goals_for, goals_against, games]}

    with open(csvfile, 'r') as csv:
        header = True
        for line in csv:
       	    if header:
                header = False
            else:
                row = line.split(",")
                games_played, row = add_games_played(row, games_played) 

                row.append(season)
                try:
                    current_streaks = get_streaks(row, current_streaks)
                
                    goal_totals = update_goals(row, goal_totals)
                except ValueError: # this is for games that got rescheduled
                    pass
    for team in current_streaks.keys():
        if len(current_streaks[team]) >= 10:
            all_streaks.append(current_streaks[team])

    for team in goal_totals.keys():
        print team + "\t" +  str(goal_totals[team][0]) + "\t" + str(goal_totals[team][1])
    
    seasons[season] = goal_totals

streak_stats = open("streak_stats.csv", 'w')
streak_stats.write("season_team,games,season_gf,season_ga,streak_gf,streak_ga,non_streak_gf,non_streak_ga\n")

for streak in all_streaks:
    print(streak)
    print(str(len(streak)))

    season = streak[0][-1]
    team = get_streak_team(streak[0])
    print(season, team)
    streak_stats.write(season + ' ' + team + ',' + str(len(streak)) + ',')
  
    ## SEASON STATS  
    season_goals = seasons[season][team]
    season_gf_game = float(season_goals[0]) / float(season_goals[2])
    season_ga_game = float(season_goals[1]) / float(season_goals[2])
    streak_stats.write(str(season_gf_game) + ',' + str(season_ga_game) + ',')

    ## STREAK STATS
    streak_goals_for = 0.0
    streak_goals_against = 0.0
    games = float(len(streak))

    for game in streak:
        goals_for, goals_against = for_against(game, team)        
        streak_goals_for += goals_for
        streak_goals_against += goals_against

    goals_for_game = streak_goals_for / games
    goals_against_game = streak_goals_against / games
    streak_stats.write(str(goals_for_game) + ',' + str(goals_against_game) + ',')

    ## NON-STREAK STATS
    ns_gf_game = (season_goals[0] - streak_goals_for) / (season_goals[2] - games)
    ns_ga_game = (season_goals[1] - streak_goals_against) / (season_goals[2] - games)
    streak_stats.write(str(ns_gf_game) + ',' + str(ns_ga_game) + '\n')

streak_stats.close()
