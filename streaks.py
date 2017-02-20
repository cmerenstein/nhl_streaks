#!/usr/bin/python
import glob

all_streaks = {}

for csvfile in glob.glob("seasons/*csv"):
    print csvfile
    current_streaks = {}

    with open(csvfile, 'r') as csv:
        header = True
        for line in csv:
       	    if header:
                header = False
            else:
                row = line.split(",")
                try:
                    # figure out who won
                    away = row[1]
                    away_goals = int(row[2])
                
                    home = row[3]
                    home_goals = int(row[4])
                            
                    if home_goals > away_goals:
                        try:
                            current_streaks[home] += 1
                        except KeyError:
                            current_streaks[home] = 1
                                    
                        current_streaks[away] = 0
                            
                    elif away_goals > home_goals:
                        try:
                            current_streaks[away] += 1
                        except KeyError:
                            current_streaks[away] = 1
                    
                        current_streaks[home] = 0
                    else: # isn't it kinda weird they used to have ties in hockey?
                        current_streaks[home] = 0
                        current_streaks[away] = 0
                except ValueError: # This is the best way to handle games that are rescheduled and therefore don't have a score
                        pass
    print current_streaks
