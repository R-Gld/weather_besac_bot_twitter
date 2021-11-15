import json
import os
import random
from datetime import datetime

import WUtils
import requests
import tweepy
from apscheduler.schedulers.background import BackgroundScheduler

global api


def get_actual_weather():
    param_besac = {
        'access_key': '471566d415ea80b9c8a4fb8e7ae57685',
        'query': 'Besançon'
    }
    return json.loads(requests.get("http://api.weatherstack.com/current", params=param_besac).text)["current"]


def manualTweet(tweet_content: str):
    api.update_status(tweet_content)


def downloadLatestImage():
    rdm = random.randint(0, 2)
    rdm = 0
    if rdm == 0:
        url = "https://www.fczoom.com/camflore.jpg"
    elif rdm == 1:
        url = "https://www.fczoom.com/cam.jpg"
    else:
        url = "https://www.fczoom.com/cam-aerodrome-veze.jpg"

    code, name = WUtils.downloadImage(url)
    if code == 200:
        if rdm == 0:
            return name, "Vue de la Place Flore à Besançon:"
        elif rdm == 1:
            return name, "Vue du Faubourd Rivotte:"
        else:
            return name, "Vue l'Aérodrome de la Vèze"
    else:
        return "-1", "none"


def actual_meteo(tweet: bool = True):
    weather_json = get_actual_weather()
    temperature = weather_json["temperature"]
    apparentTemperature = weather_json["feelslike"]
    humidity = weather_json["humidity"]
    uv_index = weather_json["uv_index"]
    comment = WUtils.codes[str(weather_json["weather_code"])]

    # visibility = weather_json["visibility"] * 1.609344
    # f"\n 👀 Visibilité: {round(visibility, 2)} mètre" \
    tweet_str = "☀ Météo de #Besançon ☁" \
                f"\n ℹ Etat: {comment}" \
                f"\n 🌡 Température réelle/ressentie: {round(temperature, 3)}°C/{round(apparentTemperature, 3)}°C" \
                f"\n ☀ Indice UV: {uv_index}" \
                f"\n ➡ Pourcentage d'Humidité: {round(humidity, 3)}%"
    (img, comment) = downloadLatestImage()
    if img == "-1":
        if tweet:
            api.update_status(tweet_str)
            print(f"Tweet lancé sans image:\"\n{tweet_str}\n\"" + "\n" * 2)
        else:
            print(f"Simulation de tweet lancé sans image: \"\n{tweet_str}\n\"" + "\n" * 2)
    else:
        if tweet:
            api.update_with_media(img, tweet_str + "\n 📍 " + comment)
            print(f"Tweet lancé avec image:\"\n{tweet_str}\n\"\nImage: {comment}" + "\n" * 2)
        else:
            print(f"Simulation de tweet lancé avec image:\"\n{tweet_str}\n\"\nImage: {comment}" + "\n" * 2)
        os.remove(img)


def tweetTL(delete: bool = True):
    flore, rivotte = WUtils.createTL()

    id_flore = api.media_upload(flore)
    id_rivotte = api.media_upload(rivotte)

    api.update_status(flore, "🎥 Timelapse de la journée:\n 📍 Place flore:",
                      media_ids=[id_flore.media_id_string])
    api.update_status(rivotte, "🎥 Timelapse de la journée:\n 📍 Faubourd Rivotte:",
                      media_ids=[id_rivotte.media_id_string])
    if delete: WUtils.deleteImages()


def getOAuthHandlerTokens():
    with open("OAuthHandler.txt") as f:
        l1 = f.readline()
        l2 = f.readline()
    return l1, l2


def getAccessToken():
    with open("AccessToken.txt") as f:
        l1 = f.readline()
        l2 = f.readline()
    return l1, l2


if __name__ == "__main__":
    print("Bienvenue sur le bot de météo de BESANÇON")
    # yn = str(input("Voulez vous lancer le bot ? (y/n)"))
    yn = "y"
    if yn == "y":
        OAuth1, OAuth2 = getOAuthHandlerTokens()
        auth = tweepy.auth.OAuthHandler(OAuth1, OAuth2)

        accessToken1, accessToken2 = getAccessToken()
        auth.set_access_token(accessToken1, accessToken2)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        scheduler = BackgroundScheduler()
        job_1 = scheduler.add_job(func=actual_meteo, trigger="cron", hour="8,16")
        job_2 = scheduler.add_job(func=WUtils.downloadIFTL, trigger="cron", second="*/10")
        job_3 = scheduler.add_job(func=tweetTL, trigger="cron", hour="0")
        if not scheduler.running:
            scheduler.start()
        launched = datetime.now().timestamp()
        pause = False
        while True:
            cmd = str(input("\t> ")).lower().strip()
            if cmd == "uptime":
                print("Le bot a été lancé le " + datetime.fromtimestamp(launched).strftime("%d/%m/%G - %H:%M:%S"))
            elif cmd == "quit" or cmd == "exit":
                print("Le bot s'arrête.")
                print("Au revoir.")
                job_1.remove()
                job_2.remove()
                job_3.remove()
                scheduler.shutdown()
                WUtils.cancelActualTL()
                exit(2)
            elif cmd == "stweet":
                if pause:
                    print("Le bot est en pause, il est donc impossible de tweeter actuellement, tappez \"resume\" pour "
                          "relancer le bot.")
                else:
                    print("La météo est entrain d'être twitter.")
                    actual_meteo(False)
            elif cmd == "tweet":
                if pause:
                    print("Le bot est en pause, il est donc impossible de tweeter actuellement, tappez \"resume\" pour "
                          "relancer le bot.")
                else:
                    print("La météo est entrain d'être twitter.")
                    actual_meteo()
            elif cmd == "pause" or cmd == "resume":
                pause = not pause
                if pause:
                    job_1.pause()
                    job_2.pause()
                    job_3.pause()
                    print("Le bot a été mis en pause")
                else:
                    job_1.resume()
                    job_2.resume()
                    job_3.resume()
                    print("Le bot a été relancé.")
            elif cmd.split(" ")[0] == "mtweet":
                text = " ".join(cmd.split(" ")[1:])
                if text.strip() == "":
                    print("Une erreur est survenue, vous devez mettre un texte.")
                else:
                    print(f"Tweet Manuel: \n{text}")
                    manualTweet(text)
            elif cmd == "createvid":
                print("Création des vidéos.")
                fps_in = input(f"Nombre de fps (default: {WUtils.default_fps}):\n\t> ")
                if fps_in == "": fps_in = str(WUtils.default_fps)
                fps = eval(fps_in)
                WUtils.createTL(fps)
            elif cmd == "tweettimelapse":
                tweetTL(False)
            else:
                print("Aide Commandes Bot Twitter:")
                print("\t- uptime - Donne la date de lancement du bot.")
                print("\t- tweet - Tweet la météo actuelle de besançon sur le compte.")
                print("\t- stweet - Créer un tweet de météo actuelle de besançon sans la tweeter.")
                print("\t- mtweet <texte>- Tweet le texte donner en argument.")
                print("\t- createvid - Créer les timelapse des images disponibles. (Default fps: {WUtils.default_fps})")
                print("\t- (pause|resume) - Met en pause ou relance le bot suivant le cas.")
                print("\t- (quit|exit) - Arrête le bot.")
    else:
        print("Le bot s'arrête")
        print("Au revoir.")
