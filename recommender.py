from data import CITIES, BUSINESSES, USERS, REVIEWS, TIPS, CHECKINS
import data
import collections

import random

def recommend(user_id=None, business_id=None, city=None, n=10, scenario=None):
    """
    Returns n recommendations as a list of dicts.
    Optionally takes in a user_id, business_id and/or city.
    A recommendation is a dictionary in the form of:
        {
            business_id:str
            stars:str
            name:str
            city:str
            adress:str
        }
    """
    if not city:
        city = random.choice(CITIES)

    if scenario == 1:
        print("start recommending scenario 1")
    
    elif scenario == 2:
        print("start recommending scenario 2")
    
    elif scenario == 3:
        print("start recommending scenario 3")

        # get categories from selected business
        business_data = data.get_business(city, business_id)
        categories = business_data['categories']

        # turn string of categories into list
        categories_split = categories.split(", ")

        # take subset based on city
        bus_city = BUSINESSES[city]

        dic_cat = {}
        for bus in bus_city:
            cat_list = bus['categories'].split(", ")
            dic_cat[bus['business_id']] = cat_list

        sim_cat = {}
        for key in dic_cat.keys():
            overlap = len(set(dic_cat[key]) & set(categories_split))
            most_cat = max(len(dic_cat[key]), len(categories_split))
            similarity = overlap / most_cat
            if similarity != 0:
                sim_cat[key] = similarity

        sorted_x = sorted(sim_cat.items(), key=lambda kv: kv[1], reverse=True)

        print(sorted_x)
        print("BREAK")
        grote_list = []
        l = []
        for i in range(len(sorted_x)-1):
            if sorted_x[i][1] == sorted_x[i+1][1]:
                l.append(sorted_x[i])
            if sorted_x[i][1] != sorted_x[i+1][1]:
                l.append(sorted_x[i])
                grote_list.append(l)
                l = []
        print(grote_list)

    
    elif scenario == 4:
        print("start recommending scenario 4")

    
    return random.sample(BUSINESSES[city], n)
