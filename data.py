"""
This file loads the data from the data directory and shows you how.
Feel free to change the contents of this file!
Do ensure these functions remain functional:
    - get_business(city, business_id)
    - get_reviews(city, business_id=None, user_id=None, n=10)
    - get_user(username)
"""

import os
import json
import random

import collections
import pandas as pd
import numpy as np
import math

DATA_DIR = "data"


def load_cities():
    """
    Finds all cities (all directory names) in ./data
    Returns a list of city names
    """
    return [x for x in os.listdir(DATA_DIR) if x!='.DS_Store']


def load(cities, data_filename):
    """
    Given a list of city names,
        for each city extract all data from ./data/<city>/<data_filename>.json
    Returns a dictionary of the form:
        {
            <city1>: [<entry1>, <entry2>, ...],
            <city2>: [<entry1>, <entry2>, ...],
            ...
        }
    """
    data = {}
    for city in cities:
        city_data = []
        with open(f"{DATA_DIR}/{city}/{data_filename}.json", "r") as f:
            for line in f:
                city_data.append(json.loads(line))
        data[city] = city_data
    return data


def get_business(city, business_id):
    """
    Given a city name and a business id, return that business's data.
    Returns a dictionary of the form:
        {
            name:str,
            business_id:str,
            stars:str,
            ...
        }
    """
    for business in BUSINESSES[city]:
        if business["business_id"] == business_id:
            return business
    raise IndexError(f"invalid business_id {business_id}")


def get_reviews(city, business_id=None, user_id=None, n=10):
    """
    Given a city name and optionally a business id and/or auser id,
    return n reviews for that business/user combo in that city.
    Returns a dictionary of the form:
        {
            text:str,
            stars:str,
            ...
        }
    """
    def should_keep(review):
        if business_id and review["business_id"] != business_id:
            return False
        if user_id and review["user_id"] != user_id:
            return False
        return True

    reviews = REVIEWS[city]
    reviews = [review for review in reviews if should_keep(review)]
    return random.sample(reviews, min(n, len(reviews)))


def get_user(username):
    """
    Get a user by its username
    Returns a dictionary of the form:
        {
            user_id:str,
            name:str,
            ...
        }
    """
    for city, users in USERS.items():
        for user in users:
            if user["name"] == username:
                return user
    raise IndexError(f"invalid username {username}")


def create_frame(stad=None):
    city = stad
    bedrijven_in_city = BUSINESSES[city]

    row_bus = []
    for i in bedrijven_in_city:
        row_bus.append(i['business_id'])

    users_in_city = USERS[city]

    col_us = []
    for x in users_in_city:
        col_us.append(x['user_id'])

    dataframe = pd.DataFrame(np.nan, columns=col_us, index=row_bus)

    for user in col_us:
        for business in row_bus:
            rev = get_reviews(city, business, user)
            if rev:
                rating = rev[0]['stars']
                # print(rating)
                dataframe[user][business] = rating
    # print(dataframe)
    return dataframe

def mean_center_columns(matrix):
    # Subtract mean of ratings from ratings
    mean_matrix = matrix.mean()
    return matrix - mean_matrix



def cos_similarity(matrix, id1, id2):
    """Compute eclid distance betwee two rows"""
    # only take the features that have values for both id1 and id2
    selected_features = matrix.loc[id1].notna() & matrix.loc[id2].notna()
    
    # if no matching features, return 0.0
    if not selected_features.any():
        return 0.0
    
    # get the features from the matrix
    features1 = matrix.loc[id1][selected_features]
    features2 = matrix.loc[id2][selected_features]
    
    # if one movie is only rated with zero
    if not features1.any():
        return 0.0
    if not features2.any():
        return 0.0
    
    # calculate the top part of the numerator
    teller = sum(features1 * features2)
    
    # calculate the denominator
    noemer = (math.sqrt(np.square(features1).sum())) * (math.sqrt(np.square(features2).sum()))
    
    return teller/noemer


def create_similarity_matrix_cosine(matrix):
    """ creates the similarity matrix based on cosine similarity """
    similarity_matrix = pd.DataFrame(0, index=matrix.index, columns=matrix.index, dtype=float)
    
    # fill in matrix per user combination
    for user1 in matrix.index:
        for user2 in matrix.index:
            if user1 == user2:
                similarity_matrix[user1][user2] = 1
            else:
                similarity = cos_similarity(matrix, user1, user2)
                if similarity != 0:
                    similarity_matrix[user1][user2] = similarity
                else:
                    similarity_matrix[user1][user2] = 0
    return similarity_matrix

def select_neighborhood(similarity_matrix, utility_matrix, target_user, target_film):
    """selects all items with similarity > 0"""
    # Check if input is valid
    if target_user in utility_matrix.columns and target_film in utility_matrix.index:
        
        # Filter the movies target user has seen
        seen = utility_matrix[target_user].dropna()
        similarity_matrix = similarity_matrix.loc[seen.index]

        # Filter movies that are similar to target film
        similar = similarity_matrix[similarity_matrix[target_film] > 0]
        return similar[target_film]
    

# Check for valid input added to function
def weighted_mean(neighborhood, utility_matrix, user_id):
    
    # check for valid input
    if isinstance(neighborhood, pd.Series):
        if not neighborhood.any():
            return 0

    else:
        if not neighborhood:
            return 0
    
    # Filter matrix on seen movies and on given userId
    rating = utility_matrix[user_id]
    rating = rating[neighborhood.index]

    # Calculate predicted rating with weighted mean
    return ((rating * neighborhood).sum()) / neighborhood.sum() 


# define a helper function for accessing data
def get_rating(ratings, userId, itemId):
    """Given a userId and movieId, this function returns the corresponding rating.
       Should return NaN if no rating exists."""
    
    # Get the row where userId and movieId correspond with given Ids
    row = ratings.loc[(ratings['users'] == userId) & (ratings['index'] == itemId)]
    
    # return rating if available else return NaN
    if row["rating"].empty is True:
        return np.nan
    else:    
        rating = float(row["rating"])
        return rating

def pivot_ratings(ratings):
    """ takes a rating table as input and computes the utility matrix """
    # get movie and user id's
    items = ratings['index'].unique()
    userIds = ratings['users'].unique()
    
    # create empty data frame
    pivot_data = pd.DataFrame(np.nan, columns=userIds, index=items, dtype=float)
    
    # use the function get_rating to fill the matrix
    for user in userIds:
        for item in items:
            pivot_data[user][item] = get_rating(ratings, user, item)
    return pivot_data

# def predict_ratings_item_based(similarity, utility, test_data):
#     # Create new column    
#     test_data["predicted rating"] = 0
    
#     # Calculate predicted rating for all different combinations
#     for target_user in test_data["users"].unique():
#         for target_film in test_data["index"].unique():
            
#             # Get index of combination
#             row = test_data.loc[(test_data['users'] == target_user) & (test_data['index'] == target_film)].index

#             # Get neighborhood of combination
#             neighborhood = select_neighborhood(similarity, utility, target_user, target_film)

#             # Calculate predicted rating
#             _weighted_mean = weighted_mean(neighborhood, utility, target_user)

#             # Place predicted rating in DataFrame
#             test_data.loc[row,"predicted rating"] = _weighted_mean
            
#     # Make sure correct type
#     test_data["predicted rating"].astype(float, inplace=True)
#     return test_data


def prediction(similarity, utility, user, movie):
    # maak een functie waar de neighbors worden berekend en de weighted mean wordt berekend
    neighbors = select_neighborhood(similarity, utility, user, movie)
    return weighted_mean(neighbors, utility, user)

def predict_ratings_item_based(similarity, utility, test_data):
    # voeg een nieuwe kolom toe waar de uitkomst van de prediction functie wordt toegepast 
    test_data['predicted rating'] = test_data.apply(lambda row: prediction(similarity, utility, row['users'], row['index']), axis=1)
    return test_data

def mse(predicted_ratings):
    predicted_ratings["difference"] = predicted_ratings["rating"] - predicted_ratings["predicted rating"]
    return (np.square(predicted_ratings["difference"]).sum()) / (predicted_ratings["difference"].count())



CITIES = load_cities()
USERS = load(CITIES, "user")
BUSINESSES = load(CITIES, "business")
REVIEWS = load(CITIES, "review")
TIPS = load(CITIES, "tip")
CHECKINS = load(CITIES, "checkin")

# WESTLAKEFRAME = create_frame('westlake')
# SUNCITYFRAME = create_frame('suncity')
# CHARDONFRAME = create_frame('chardon')