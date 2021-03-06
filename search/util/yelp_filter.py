import rauth
import statistics
import ast

# params["limit"]
def get_search_parameters(lat,lon):
    #See the Yelp API for more details
    '''
    Prepare parameteres for get_results function

    Inputs:
        lat, lon: float, latitude, longitude of the spot

    Outputs:
        params: dictionary
    '''
    params = {}
    params["term"] = "restaurant"
    params["ll"] = "{},{}".format(str(lat),str(lon))
    params["radius_filter"] = "2000"
    params["limit"] = "20" #Yelp will only return a max of 40 results at a time

    return params

def get_results(params):
    '''
    Get requested data dictionary of the restaurants from Yelp API

    Inputs:
        params: dictionary

    Outputs:
        data: dictionary
    '''

    #Obtain these from Yelp's manage access page
    consumer_key = "yk-sQRKSX0mitrxx6VMN_g"
    consumer_secret = "L0Q9YXv0KT27XpJ3jQNkL2qCaZY"
    token = "4HL--_tknW9UyCSJL8xRGOm0ZP8b2J4p"
    token_secret = "tzfwqT1NUaGKQzuAdiatEHH4nWc"
    
    session = rauth.OAuth1Session(
        consumer_key = consumer_key
        ,consumer_secret = consumer_secret
        ,access_token = token
        ,access_token_secret = token_secret)
        
    request = session.get("http://api.yelp.com/v2/search",params=params)
    
    #Transforms the JSON API response into a Python dictionary
    data = request.json()
    session.close()
    
    return data

# limit_num
def get_food_index(index,df_location):
    '''
    Get the mean rating and review count of a spot as the food index

    Inputs:
        index: integer
        df_location: dataframe

    Outputs:
        (rating, review): tuple of float
    '''
    lat, lon = df_location.loc[index][0]
    # lat, lon = ast.literal_eval(df_location.loc[index][0])
    restaurant_dic = get_results(get_search_parameters(lat,lon))
    if 'businesses' not in restaurant_dic:
        return None
    else:
        limit_num = 20
        l = []
        for i in range(limit_num):

                rating = restaurant_dic['businesses'][i]['rating']
                review_count = restaurant_dic['businesses'][i]['review_count']
                a = [(rating, review_count)]
                l = l + a

        rating_l = []
        review_count_l = []
        for i in l:
            rating, review_count = i
            rating_l += [rating]
            review_count_l += [review_count]
        rating = statistics.mean(rating_l)
        review = statistics.mean(review_count_l)

        return (rating,review)

def get_benchmark(output, df_location, n): # for flexibility, mean+n*sd
    '''
    Get food index benchmark for the current candidate list, along with a dictionary of each spot's food index

    Inputs:
        output: candidate dictionary
        df_location: dataframe
        n: unit of sd, for the equation mean+n*sd

    Outputs:
        benchmark of rating, benchmark of review count, food index dictionary
    '''
    rating_l = []
    review_l = []
    dic = {}
    for key in output:
        rv = get_food_index(key, df_location)
        if rv:
            rating, review = rv
            rating_l += [rating]
            review_l += [review]
            dic[key] = rv
    rating_mean = statistics.mean(rating_l)
    review_mean = statistics.mean(review_l)
    rating_sd = statistics.stdev(rating_l)
    review_sd = statistics.stdev(review_l)
    return (rating_mean+n*rating_sd, review_mean+n*review_sd, dic)

def get_filter_l(output, df_location, n): # for flexibility, mean+n*sd
    '''
    Using food index to filter current candidate list

    Inputs:
        output: candidate dictionary
        df_location: dataframe
        n: unit of sd, for the equation mean+n*sd

    Outputs:
        filter_l: list of keys from output that are above food index benchmark
    '''
    rating_benchmark, review_benchmark, dic = get_benchmark(output, df_location, n)
    filter_l = []
    for key in output:
        if key in dic:
            rating, review = dic[key]            
            if rating >= rating_benchmark and review >= review_benchmark:
                filter_l += [key]
    return filter_l
