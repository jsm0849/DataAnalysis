import sqlite3
import streamlit
import requests
import datetime
import pytz

page_title = "Collecting Dex Data"
page_icon = ":seedling:"
layout = "centered"

# Connecting to the database
connection = sqlite3.connect("DB.db")
cursor = connection.cursor()

streamlit.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

streamlit.header(f"Welcome to SproutCast! Your Gardening Companion")
streamlit.subheader(f"Tell us about your garden! Please enter your information below. SproutCast will use your inputs" +
                    " along with local weather data to predict how much water you should be giving your garden " +
                    "using machine learning!")
with (streamlit.form("input_form")):
    pair = streamlit.text_input("Enter your Dexscreener Pair ID: ", key="pairId")
    submitted = streamlit.form_submit_button("Submit Form")

    if submitted:
        pairId = str(streamlit.session_state["pairId"])
        response = requests.get(
            "https://api.dexscreener.com/latest/dex/pairs/solana/" + pairId,
            headers={},
        )
        if response.status_code == 200:
            data = response.json()

            pairAddress = data["pairs"][0]["pairAddress"]
            tokenAddress = data["pairs"][0]["baseToken"]["address"]

            buysM5 = data["pairs"][0]["txns"]["m5"]["buys"]
            buysH1 = data["pairs"][0]["txns"]["h1"]["buys"]
            sellsM5 = data["pairs"][0]["txns"]["m5"]["sells"]
            sellsH1 = data["pairs"][0]["txns"]["h1"]["sells"]

            volM5 = data["pairs"][0]["volume"]["m5"]
            volH1 = data["pairs"][0]["volume"]["h1"]

            priceM5 = data["pairs"][0]["priceChange"]["m5"]
            priceH1 = data["pairs"][0]["priceChange"]["h1"]

            liquidity = data["pairs"][0]["liquidity"]["usd"]

            marketCap = data["pairs"][0]["marketCap"]

            paidResponse = requests.get("https://api.dexscreener.com/orders/v1/solana/" + tokenAddress, headers={},)
            paidData = paidResponse.json()
            paidProfile = 0
            paidAd = 0
            for item in paidData:
                if item["type"] == "tokenProfile" and item["status"] == "approved":
                    paidProfile = 1
                elif item["type"] == "tokenAd" and item["status"] == "approved":
                    paidAd = 1

            if "socials" in data:
                socials = 1
            else: socials = 0

            if "websites" in data:
                websites = 1
            else: websites = 0

            if "boosts" in data:
                boosts = data["pairs"][0]["boosts"]["active"]
            else: boosts = 0

            timezone = pytz.timezone("America/New_York")
            now = datetime.datetime.now(timezone)
            current_minutes = (now.hour * 60) + now.minute
            dayOfWeek = now.weekday()

            command = ("INSERT INTO tokens VALUES('" + str(pairAddress) + "', '" + str(tokenAddress) + "', '" + str(buysM5) + "', '" +
                                    str(buysH1) + "', '" + str(sellsM5) + "', '" + str(sellsH1) + "', '" + str(volM5) + "', '" + str(volH1) + "', '" +
                                    str(priceM5) + "', '" + str(priceH1) + "', '" + str(liquidity) + "', '" + str(marketCap) + "', '" +
                                    str(paidProfile) + "', '" + str(paidAd) + "', '" + str(websites) + "', '" + str(socials) + "', '" + str(boosts) + "', '" +
                                    str(dayOfWeek) + "', '" + str(current_minutes) + "', 'default')")
            #streamlit.header(command)
            cursor.execute(command)
            connection.commit()
            cursor.execute("SELECT * FROM tokens")
            tokens = cursor.fetchall()
            for row in tokens:
                streamlit.subheader(row[0])
            #streamlit.subheader("Pair Address: " + str(pairAddress) +
            #                    "\nToken Address: " + str(tokenAddress) +
            #                    "\nBuys 5m: " + str(buysM5) +
            #                    "\nBuys 1h: " + str(buysH1) +
            #                    "\nSells 5m: " + str(sellsM5) +
             #                   "\nSells 1h: " + str(sellsH1) +
            #                    "\nVolume 5m: " + str(volM5) +
            #                    "\nVolume 1h: " + str(volH1) +
            #                    "\nPrice 5m: " + str(priceM5) +
            #                    "\nPrice 1h: " + str(priceH1) +
            #                    "\nLiquidity: $" + str(liquidity) +
            #                    "\nMarket Cap: $" + str(marketCap) +
            #                    "\nPaid Profile: " + str(paidProfile) +
            #                    "\nPaid Ad: " + str(paidAd) +
            #                    "\nWebsites: " + str(websites) +
            #                    "\nSocials: " + str(socials) +
            #                    "\nBoosted: " + str(boosts))

with streamlit.form("result_form"):
    resultPair = streamlit.text_input("Enter your Dexscreener Pair ID: ", key="resultPairId")
    result = streamlit.radio(
        "Select coin result:",
        [":Success", ":Failure"],
        captions=[
            "Success",
            "Failure",
        ],
        horizontal=True,
    )

    submittedb = streamlit.form_submit_button("Submit Form")

    if submittedb:
        if result == ":Success":
            streamlit.subheader("Success")

connection.close()