# This is a python file you need to have in the same directory as your code so you can import it
import fitbit_api.gather_keys_oauth2 as Oauth2
import fitbit
import pandas as pd 
import datetime
import requests
from flask import jsonify, request

# You will need to put in your own CLIENT_ID and CLIENT_SECRET as the ones below are fake
CLIENT_ID='23QRB9'
CLIENT_SECRET='6bfec81a8f337d8e8b233b375ae3b885'

class FitbitIntegration():

    def authorise(self):

        print("fit bit 1 -------------------------------------------------------------")

        server=Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)

        print("fit bit 2 -------------------------------------------------------------")

        server.browser_authorize()

        print("fit bit 3 -------------------------------------------------------------")

        ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
        REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])

        print("fit bit 4-------------------------------------------------------------")

        print("ACCESS_TOKEN" + ACCESS_TOKEN)
        print("REFRESH_TOKEN" + REFRESH_TOKEN)

        print("fit bit 5 -------------------------------------------------------------")

        auth2_client=fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)

        print("fit bit 6 -------------------------------------------------------------")

        USER_ID = 'BFJ5X6'

        URL = "https://api.fitbit.com/1/user/"+USER_ID+"/profile.json"

        HEADERS = {"accept":"application/json", "authorization":"Bearer "+ACCESS_TOKEN}

        r = requests.get(URL, headers=HEADERS)

        print("fit bit 7 -------------------------------------------------------------")

        data = r.json()

        user_data = data["user"]

        date_of_birth = user_data["dateOfBirth"]
        height = user_data["height"]
        weight = user_data["weight"]
        avg_daily_steps = user_data["averageDailySteps"]

        print("fit bit 8 -------------------------------------------------------------")

        response = {"date_of_birth": date_of_birth, "height": height, "weight": weight, "avg_daily_steps": avg_daily_steps}

        return jsonify(response)


