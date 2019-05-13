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

        grote_list = []
        equal = []
        for i in range(len(sorted_x)-1):
            if sorted_x[i][1] == sorted_x[i+1][1]:
                equal.append(sorted_x[i])
            if sorted_x[i][1] != sorted_x[i+1][1]:
                equal.append(sorted_x[i])
                grote_list.append(equal)
                equal = []

        stars_and_reviews = []
        for group in grote_list:
            group = dict(group)
            for key in group:
                key_data = data.get_business(city, key)
                key_stars = key_data['stars']
                key_reviews = key_data['review_count']
                group[key] = [key_stars, key_reviews]
            stars_and_reviews.append(group)

        final_list = []
        for equals in stars_and_reviews:
            sorted_items = sorted(equals.items(), key=lambda kv: kv[1], reverse=True)
            for business in sorted_items:
                final_list.append(business[0])
        
        recommendation = []
        if len(final_list) >= 10:
            for business in final_list[0:10]:
                dic_business = data.get_business(city, business)
                recommendation.append(dic_business)   

        print(recommendation)
        return recommendation    
    
    elif scenario == 4:
        print("start recommending scenario 4")

    
    return random.sample(BUSINESSES[city], n)
