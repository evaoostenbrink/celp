from data import CITIES, BUSINESSES, USERS, REVIEWS, TIPS, CHECKINS
import data
import collections
import pandas as pd
import random
import numpy as np
import math
from sklearn.model_selection import train_test_split

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

        # create list with businesses which have more than 10 reviews
        valid_businesses = []
        for var in BUSINESSES:
            for x in BUSINESSES[var]:
                if x['review_count'] > 10:
                    valid_businesses.append(x)

        # get all user ids
        all_user_ids = []
        for stad in USERS:
            for user in USERS[stad]:
                all_user_ids.append(user['user_id'])

        # print(all_user_ids)
            
    elif scenario == 2:
        print("start recommending scenario 2")

        # create list with how many reviews user has placed in each city
        review_in_city = []
        for city in REVIEWS:
            reviews_per_city = REVIEWS[city]
            for review in reviews_per_city:
                if user_id in review.values():
                    review_in_city.append(city)

        # check what city is most reviewed and where user comes from
        most_reviewed_city = collections.Counter(review_in_city).most_common()[0][0]
        print("city determined", most_reviewed_city)

        utility_matrix = data.create_frame(most_reviewed_city)
        print(" utility matrix created")
        print("utility", utility_matrix)

# ----------------------------------------------------------------------------------------------
     # for testing purposes
        # re_frame = utility_matrix.reset_index()
        # re_frame = re_frame.melt(id_vars=['index'], var_name='users', value_name='rating')
        # print("reframed", list(re_frame.columns.values))
        # print(re_frame)

        # train, test = train_test_split(re_frame, test_size=0.2)
        # print(len(train), len(test))
        # train = train.dropna()
        # test = test.dropna()
        # print(test)
        # kevin_test = test

        # utility_matrix_train = data.pivot_ratings(train)
        # mean_center_train = data.mean_center_columns(utility_matrix_train)
        # sim_cos_train = data.create_similarity_matrix_cosine(mean_center_train)

        # predicted_ratings = data.predict_ratings_item_based(sim_cos_train, utility_matrix_train, kevin_test)
        
        # predicted_ratings = predicted_ratings[predicted_ratings['predicted rating'] != 0]
        # print(predicted_ratings)
        # print(data.mse(predicted_ratings))

        
      
# ----------------------------------------------------------------------------------------------
        not_seen = []
        for index, row in utility_matrix.iterrows():
            if math.isnan(row[user_id]):
                not_seen.append(index)
        print("determined what user hasn't seen yet")
        print(not_seen)

        mean_centered_matrix = data.mean_center_columns(utility_matrix)
        print("matrix mean centered")

        similarity = data.create_similarity_matrix_cosine(mean_centered_matrix)
        print("similarity", similarity)

        pred = {}
        for item in not_seen:
            neighborhood = data.select_neighborhood(similarity, utility_matrix, user_id, item)
            rating_prediction = data.weighted_mean(neighborhood, utility_matrix, user_id)
            if rating_prediction != 0:
                pred[item] = rating_prediction
        print(pred, len(pred))

        sorted_pred_rating = sorted(pred.items(), key=lambda kv: kv[1], reverse=True)
        print(sorted_pred_rating)

        item_col_rec = []
        for prediction in sorted_pred_rating:
            item_col_rec.append(prediction[0])
        print(item_col_rec)

        recom = []
        if len(item_col_rec) >= 10:
            for business in item_col_rec[0:10]:
                dic_business = data.get_business(most_reviewed_city, business)
                recom.append(dic_business)
        return recom
    
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

        # check if length of list is bigger than or is 10, if so append top 10 businesses to recommendations
        if len(final_list) >= 10:
            for business in final_list[0:10]:
                dic_business = data.get_business(city, business)
                recommendation.append(dic_business)

            # for testing purposes. Check the terminal
            print("\n")
            print("NAME | SIMILARITY | AVERAGE RATING | REVIEW COUNT | CITY \n")
            for i in recommendation:
                print(i['name'], " | ", "similarity = ", sim_cat[i['business_id']], " | ", "Average rating =", i['stars'], " | ", "Review count =", i['review_count'], " | ", "City =", i['city'], "\n" )

        
        else:
            
            # if length of final_list is less than 10, first append all businesses we have got to recommandend
            for business in final_list:
                dic_business = data.get_business(city, business)
                recommendation.append(dic_business)

            # for testing purposes. Check the terminal
            print("\n")
            print("NAME | SIMILARITY | AVERAGE RATING | REVIEW COUNT | CITY \n")
            for i in recommendation:
                print(i['name'], " | ", "similarity = ", sim_cat[i['business_id']], " | ", "Average rating =", i['stars'], " | ", "Review count =", i['review_count'], " | ", "City =", i['city'], "\n" )
            already_in_rec = len(final_list)

            # check how much recommandations are needed to complete the top 10
            needed_rec = 10 - len(final_list)
            
            # create a list with all cities
            temporary_cities_list = CITIES

            while True:

                # pick a random city out of the list of all cities
                stad = random.choice(temporary_cities_list)

                # check if random picked city is equal to the current city
                # check if there are enough cities in the random picked city to fill the top 10
                # if so, break out of for loop
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
            
            # get all data from businesses and put it in the recommandations
            for business in final_list[0:needed_rec]:
                dic_business = data.get_business(city, business)
                recommendation.append(dic_business)
        
            # for testing purposes. Check the terminal
            for i in recommendation[already_in_rec:]:
                print(i['name'], " | ", "similarity = ", sim_cat[i['business_id']], " | ", "Average rating =", i['stars'], " | ", "Review count =", i['review_count'], " | ", "City =", i['city'], "\n" )

        return recommendation    
    
    elif scenario == 4:
        print("start recommending scenario 4")

    
    return random.sample(BUSINESSES[city], n)
