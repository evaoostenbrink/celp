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

        # for each business in the selected city, link to categorie and placed in dict
        # dict contains business_id : categories
        dic_cat = {}
        for bus in bus_city:
            cat_list = bus['categories'].split(", ")
            dic_cat[bus['business_id']] = cat_list

        # calculate similarity between selected business and all other businesses in city
        sim_cat = {}
        for key in dic_cat.keys():

            # devide categories overlap by maximum amount of categories
            overlap = len(set(dic_cat[key]) & set(categories_split))
            most_cat = max(len(dic_cat[key]), len(categories_split))
            similarity = overlap / most_cat

            # place similarity in dict if similarity is not zero
            if similarity != 0:
                sim_cat[key] = similarity

        # transform dict to list of tuples and sort by similarity
        sorted_sim = sorted(sim_cat.items(), key=lambda kv: kv[1], reverse=True)

        # group similarities if similarity values are the same
        grouped_sim_list = []
        equal = []
        for i in range(len(sorted_sim)-1):
            if sorted_sim[i][1] == sorted_sim[i+1][1]:
                equal.append(sorted_sim[i])
            if sorted_sim[i][1] != sorted_sim[i+1][1]:
                equal.append(sorted_sim[i])
                grouped_sim_list.append(equal)
                equal = []

        # create list with dicts containing rating and review count
        stars_and_reviews = []
        for group in grouped_sim_list:
            group = dict(group)
            for key in group:
                key_data = data.get_business(city, key)
                group[key] = [key_data['stars'], key_data['review_count']]
            stars_and_reviews.append(group)

        # sort on stars, if stars are same value sort on review count
        final_list = []
        for equals in stars_and_reviews:
            sorted_items = sorted(equals.items(), key=lambda kv: kv[1], reverse=True)

            # put all business id's in final list except for selected business
            for business in sorted_items:
                if business[0] != business_id:
                    final_list.append(business[0])
        
        # get all information for top10
        recommendation = []

        if len(final_list) >= 10:
            for business in final_list[0:10]:
                dic_business = data.get_business(city, business)
                recommendation.append(dic_business)
        
        else:
            for business in final_list:
                dic_business = data.get_business(city, business)
                recommendation.append(dic_business)

            needed_rec = 10 - len(final_list)
            
            temporary_cities_list = CITIES

            while True:
                stad = random.choice(temporary_cities_list)
                if stad != city and len(BUSINESSES[stad]) >= needed_rec:
                    city = stad
                    break
            
            bus_city = BUSINESSES[city]
            
            # for each business in the selected city, link to categorie and placed in dict
            # dict contains business_id : categories
            dic_cat = {}
            for bus in bus_city:
                cat_list = bus['categories'].split(", ")
                dic_cat[bus['business_id']] = cat_list

            # calculate similarity between selected business and all other businesses in city
            sim_cat = {}
            for key in dic_cat.keys():

                # devide categories overlap by maximum amount of categories
                overlap = len(set(dic_cat[key]) & set(categories_split))
                most_cat = max(len(dic_cat[key]), len(categories_split))
                similarity = overlap / most_cat

                # place similarity in dict
                sim_cat[key] = similarity

            # transform dict to list of tuples and sort by similarity
            sorted_sim = sorted(sim_cat.items(), key=lambda kv: kv[1], reverse=True)

            # group similarities if similarity values are the same
            grouped_sim_list = []
            equal = []
            for i in range(len(sorted_sim)-1):
                if sorted_sim[i][1] == sorted_sim[i+1][1]:
                    equal.append(sorted_sim[i])
                if sorted_sim[i][1] != sorted_sim[i+1][1]:
                    equal.append(sorted_sim[i])
                    grouped_sim_list.append(equal)
                    equal = []

            # create list with dicts containing rating and review count
            stars_and_reviews = []
            for group in grouped_sim_list:
                group = dict(group)
                for key in group:
                    key_data = data.get_business(city, key)
                    group[key] = [key_data['stars'], key_data['review_count']]
                stars_and_reviews.append(group)

            # sort on stars, if stars are same value sort on review count
            final_list = []
            for equals in stars_and_reviews:
                sorted_items = sorted(equals.items(), key=lambda kv: kv[1], reverse=True)

                # put all business id's in final list except for selected business
                for business in sorted_items:
                    if business[0] != business_id:
                        final_list.append(business[0])
            
            for business in final_list[0:needed_rec]:
                dic_business = data.get_business(city, business)
                recommendation.append(dic_business)

        return recommendation    
    
    elif scenario == 4:
        print("start recommending scenario 4")

    
    return random.sample(BUSINESSES[city], n)
