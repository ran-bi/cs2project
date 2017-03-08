import pandas as pd
import numpy as np
import random
import googlemaps
import datetime
import statistics
import csv
import re
import ast
import os


'''
AIRBNB = airbnb(datetime.datetime(2017,4,20), datetime.datetime(2017,4,22), 50, 400)
BOOKING = booking(datetime.datetime(2017,4,20), datetime.datetime(2017,4,22), 50, 400)
LOCATIONS = AIRBNB.append(BOOKING, ignore_index = True)
'''

TOMORROW = datetime.date.today() + datetime.timedelta(days=1)
T = datetime.datetime.combine(TOMORROW, datetime.time(10,0))

#ATTRACTIONS = pd.read_csv('Attraction List.csv', index_col = 'Identifier')
ATTRACTIONS = pd.read_csv(os.path.join(os.path.dirname(__file__), "Attraction List.csv"), index_col = 'Identifier')

#TRANSIT_MODE = 'driving'

def transit_time(start_index, end_index, start_df, end_df, transit_mode):
    '''
    Get the transit time between two spots, transit_mode includs 'transit', 'driving'

    Inputs:
        start_index, end_index: integer
        transit_mode: string

    Outputs:
        transit_time: mints integer
    '''

    gmaps = googlemaps.Client(key='AIzaSyCaHWPcxxYS4MCt9eLILdU7E0rdsmiBVSc')
    start_point = start_df.loc[start_index][0]
    end_point = end_df.loc[end_index][0]
    print(start_point, end_point)
    distance_result = gmaps.distance_matrix(start_point, end_point, mode=transit_mode, departure_time=T)
    time_element = distance_result['rows'][0]['elements'][0]['duration']['text']
    time_element = time_element.replace('s','')
    time_element = time_element.replace('min','')
    time_element = time_element.replace(' ','')
    if re.search('hour', time_element):
        time_element = time_element.replace('hour',':')
        time_element = time_element.replace(' ','')
        h,m = time_element.split(':')
        transit_time = int(h)*60 + int(m)
    else:
        transit_time = int(time_element)
    print(transit_time)
    return transit_time

def select_attraction(df, pref_input, day=1):   
    if day == 1:
        threshold = (6, 8)  #[6,8]
    else:
        threshold = (12, 15)  #[12,15]
    
    pref_n = len(pref_input)
    
    prefs = []
    sum_hours = 0
    selected = []
  
    if pref_n >= 1:
        prefs.append([df[pref_input[0]] == 1, df[pref_input[0]] == 0])
        
        if pref_n >= 2:
            prefs.append([df[pref_input[1]] == 1, df[pref_input[1]] == 0])
        
            if pref_n >= 3:
                prefs.append([df[pref_input[2]] == 1, df[pref_input[2]] == 0])
    
    criteria = [[[0],[1]],[(0,0),(0,1),(1,0),(1,1)],
                [(0,0,0),(0,0,1),(0,1,0),(1,0,0),(0,1,1),(1,0,1),(1,1,0),(1,1,1)]]
    
    for i in range(2**pref_n):
        if pref_n == 0:
            df_select = df
        else:
            c = criteria[pref_n-1][i]
            select = prefs[0][c[0]]
            for j in range(1, pref_n):
                select = select & prefs[j][c[j]]
            df_select = df[select]
        
        similar = 0               
        for row in df_select.itertuples():
            sum_hours += row[2]
            if sum_hours > threshold[1]:
                sum_hours -= row[2]
                if sum_hours < threshold[0]:
                    continue
                return selected
            selected.append((row[0], row[2]))
            similar += 1
            if 0 < i < 2**pref_n-1 and similar > 1:
                break


#input: list of tuples
#recursion

def decide_next_spot(start_point, to_visit_, start_df, to_df, transit_mode):
    to_visit = to_visit_[:]
    next_ = 0
    min_ = transit_time(start_point, to_visit[next_][0], start_df, to_df, transit_mode)
    for i in range(1, len(to_visit)):
        time = transit_time(start_point, to_visit[i][0], start_df, to_df, transit_mode)
        if time < min_:
            min_ = time
            next_ = i
    next_spot = to_visit[next_]
    del to_visit[next_]
    
    return [(next_spot, to_visit), min_]


def single_day_route(visited, to_visit, transit_mode, travel_t = 0):  
    if len(to_visit) == 0:
        return visited, travel_t
    
    [(next_spot, to_visit), t] = decide_next_spot(visited[-1][0], to_visit, ATTRACTIONS, ATTRACTIONS, transit_mode)
    visited.append(next_spot)
    travel_t += t
    
    return single_day_route(visited, to_visit, transit_mode, travel_t)


def first_day_route(visited, to_visit, transit_mode, sum_hours = 0, travel_t = 0, popped = None):
    if popped is None:
        popped = []
        
    if sum_hours > 8:
        place = visited.pop()
        popped.append(place)
        sum_hours -= place[1]
       
        if sum_hours >= 6:
            return (visited, travel_t), to_visit+popped
    
    if len(visited) == 1:
        sum_hours = visited[0][1]
        
    [(next_spot, to_visit), t] = decide_next_spot(visited[-1][0], to_visit, ATTRACTIONS, ATTRACTIONS, transit_mode)
    sum_hours += next_spot[1]
    visited.append(next_spot)
    travel_t += t

    return first_day_route(visited, to_visit, transit_mode, sum_hours, travel_t, popped)


def start_place_and_routes(all_to_visit, transit_mode, day=1):
    routes = {}
    
    for i in range(len(all_to_visit)):
        visited = [all_to_visit[i]]
        to_visit = all_to_visit[:i]+all_to_visit[i+1:]
        
        if day == 1:    
            route = single_day_route(visited, to_visit, transit_mode)
            routes[visited[0]] = route
        else:
            day_one_route, day_two_to_visit = first_day_route(visited, to_visit, transit_mode)
            routes[visited[0]] = [day_one_route, day_two_to_visit]
    
    return routes


def route_from_hotels(locations_lst, all_to_visit, routes, transit_mode, LOCATIONS, day=1):
    travel_info = {}
    for location in locations_lst:
        d = {}
        [(next_spot, to_visit), t_init] = decide_next_spot(location, all_to_visit, LOCATIONS, ATTRACTIONS, transit_mode)
        route = routes[next_spot]
        
        if day == 1:
            d["route"] = route[0]
            t_end = transit_time(route[0][-1][0], location, ATTRACTIONS, LOCATIONS, transit_mode)
            d["total travel time"] = t_init + route[1] + t_end    

        else:
            #Day 1
            d["day 1 route"] = route[0][0]
            t_end = transit_time(route[0][0][-1][0], location, ATTRACTIONS, LOCATIONS, transit_mode)
            day_one_t = t_init + route[0][1] + t_end
            #Day 2
            day_two_to_visit = route[1]
            [(next_spot_2, to_visit_2), t_init_2] = decide_next_spot(location, day_two_to_visit, LOCATIONS, ATTRACTIONS, transit_mode)
            route_2, t_2 = single_day_route([next_spot_2], to_visit_2)
            d["day 2 route"] = route_2
            t_end_2 = transit_time(route_2[-1][0], location, ATTRACTIONS, LOCATIONS, transit_mode)
            day_two_t = t_init_2 + t_2 + t_end_2
            
            d["total travel time"] = day_one_t + day_two_t
        
        travel_info[location] = d
    return travel_info

def filter_output(output, n): # for flexibility, mean+n*sd
    t_l = []
    filter_l = []
    filter_output = {}
    for key in output:
        t = output[key]["total travel time"]       
        t_l += [t]
    t_mean = statistics.mean(t_l)
    t_sd = statistics.stdev(t_l)
    t_benchmark = t_mean - n*t_sd
    for key in output:
        t = output[key]["total travel time"]
        if t <= t_benchmark:
            filter_l += [key]
    for i in filter_l:
        filter_output[i] = output[i]
        
    return (filter_output) 

def select_by_routes(prefs, LOCATIONS, day, transit_mode, n=0):
    all_to_visit = select_attraction(ATTRACTIONS, prefs, day)
    routes = start_place_and_routes(all_to_visit, transit_mode, day)
    d = route_from_hotels(range(len(LOCATIONS)), all_to_visit, routes, transit_mode, LOCATIONS,day)
    output = filter_output(d, n)
    return output


