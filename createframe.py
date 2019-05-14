from data import CITIES, BUSINESSES, USERS, REVIEWS, TIPS, CHECKINS
import data
import collections
import pandas as pd
import random
import numpy as np

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
            rev = data.get_reviews(city, business, user)
            if rev:
                rating = rev[0]['stars']
                # print(rating)
                dataframe[user][business] = rating
    # print(dataframe)
    return dataframe

# WESTLAKEFRAME = create_frame('westlake')
# SUNCITYFRAME = create_frame('suncity')
CHARDONFRAME = create_frame('chardon')




