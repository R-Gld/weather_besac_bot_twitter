import glob
import os
import shutil
from os import path, listdir
from os.path import isfile, join
from datetime import date

import cv2
import requests
import base64

default_fps = 60


def __getAccessToken(consumer_key, consumer_secret_key):
    key_secret = '{}:{}'.format(consumer_key, consumer_secret_key).encode('ascii')
    b64_encoded_key = base64.b64encode(key_secret).decode("ascii")
    # Decode b64_encoded_key ?
    base_url = 'https://api.twitter.com/'
    auth_url = '{}oauth2/token'.format(base_url)
    auth_headers = {
        'Authorization': 'Basic {}'.format(b64_encoded_key),
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    auth_data = {
        'grant_type': 'client_credentials'
    }
    auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)
    return auth_resp.json()['access_token']


def __uploadVideoGetMediaID(video_path):
    file = open(video_path, 'rb')
    data = file.read()
    resource_url = 'https://upload.twitter.com/1.1/media/upload.json'
    parameters = {
        'media': data,
        'media_category': 'TweetVideo'}

    headers = {
        'Authorization': 'Bearer {}'.format(
            __getAccessToken("nNVMDqorcEIvmYXP7Rck81tNs", "hV8odBkSUyjm06Gci86aZDy2r52qDhZFUx9EoHxABOCkuTnZXA"))
    }

    return requests.post(resource_url, headers=headers, params=parameters)


def downloadImage(url: str):
    return downloadImageWithDir(url, "")


def downloadImageWithDir(url: str, directory: str):
    name = url.split("/")[-1]
    return downloadImageWithDirName(url, directory, name)


def downloadImageWithDirName(url: str, directory: str = "", name: str = ""):
    if directory != "" and directory[-1] not in ["/", "\\"]:
        directory += "/"
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        with open(directory + name, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return r.status_code, name


codes = {
    "113": "☀ Ensoleillé",
    "116": "🌤 Partiellement nuageux",
    "119": "☁ Nuageux",
    "122": "🌤 Couvert",
    "143": "🌁 Brume",
    "176": "🌧 Possibilité de pluie",
    "179": "❄ Possibilité de neige",
    "182": "❄ Possibilité de neige fondue",
    "185": "🌧 Possibilité de pluie verglassante",
    "200": "🌩 Orages à proximités",
    "277": "❄ Rafales de neige",
    "230": "🌪 Vent glacial violent",
    "248": "🌫 Brouillard",
    "260": "🌫 Brouillard givrant",
    "263": "🌧 Pluie fine",
    "281": "🌧 Pluie verglassante",
    "284": "🌧 Forte pluie verglassante",
    "293": "🌧 Pluie légère parsemée",
    "296": "🌧 Pluie légère",
    "299": "🌧 Pluie modérée par moments",
    "302": "🌧 Pluie modérée",
    "305": "🌧 Pluie forte par moments",
    "308": "🌧 Pluie forte",
    "311": "🌧 Pluie verglassante légère",
    "314": "🌧🧊 Pluie verglaçante modérée ou forte",
    "317": "❄ Légère neige fondue",
    "320": "🌧 Grésil modéré ou fort",
    "323": "❄🌨 Faible neige parsemée",
    "326": "❄🌨 Neige légère",
    "329": "❄🌨 Neige modérée parsemée",
    "332": "❄🌨 Neige modérée",
    "335": "❄🌨 Neige abondante parsemée",
    "338": "❄🌨 Neige abondante",
    "350": "🌧 Grêle",
    "353": "☁ Une légère averse",
    "356": "🌧 Averse de pluie modérée ou forte",
    "359": "🌧 Pluie torrentielle",
    "362": "🌧❄ Légères averses de neige fondue",
    "365": "🌧 Averses de grésil modérées ou fortes",
    "368": "❄ Légères averses de neige",
    "371": "❄🌨 Averses de neige modérées ou fortes",
    "374": "🌧 Légères averses de grésil",
    "377": "🌧 Averses modérées ou fortes de granules de glace",
    "386": "⛈ Pluie légère parsemée dans la région avec orage",
    "389": "⛈ Pluie modérée ou forte dans la zone avec tonnere",
    "392": "❄⚡ Légère neige parsemée dans la région avec du tonnerre",
    "395": "❄⚡ Neige modérée ou forte dans la région avec du tonnere"
}

"""
    => TimeLapse Part
"""


def cancelActualTL():
    flore, rivotte = __getOrCreateDirs1()
    for f in glob.glob(flore + "*.jpg"):
        os.remove(f)
    for f in glob.glob(rivotte + "*.jpg"):
        os.remove(f)


def __getOrCreateDir2():
    output_vid_dir = "output\\"
    if not path.exists(output_vid_dir) or not path.isdir(output_vid_dir):
        os.mkdir(output_vid_dir, 0o755)
    return output_vid_dir


def __getOrCreateDirs1():
    img_base = "images"
    dir_flore = img_base + "/flore"
    dir_rivotte = img_base + "/rivotte"
    # Create the directory if not exist
    if not path.exists(img_base) or not path.isdir(img_base):
        os.mkdir(img_base, 0o755)
        if not path.exists(dir_flore) or not path.isdir(dir_flore):
            os.mkdir(dir_flore, 0o755)
        if not path.exists(dir_rivotte) or not path.isdir(dir_rivotte):
            os.mkdir(dir_rivotte, 0o755)
    return dir_flore, dir_rivotte


def __getNextIndex(directory: str):
    files = [f for f in listdir(directory) if
             isfile(join(directory, f)) and (not f.startswith("image_") or not f[6:-4].isnumeric())]
    indexes = []
    for file in files:
        indexes.append(int(file[6:-4]))
    if len(indexes) == 0:
        export = 1
    else:
        export = max(indexes) + 1
    num = str(export)
    return "0" * (6 - len(num)) + num


def downloadIFTL():
    flore, rivotte = __getOrCreateDirs1()
    # Flore
    downloadImageWithDirName("https://www.fczoom.com/camflore.jpg", flore, "image_" + str(__getNextIndex(flore))
                             + ".jpg")
    # Rivotte
    downloadImageWithDirName("https://www.fczoom.com/cam.jpg", rivotte, "image_" + str(__getNextIndex(rivotte))
                             + ".jpg")
    print("debug downloadIFTL() launch")


def __createVid(img_src: str, output_dir: str, fps: int = default_fps):
    # get alll the images
    glob_l = glob.glob(img_src + "*.jpg")
    # Get the Size of the images
    img = cv2.imread(glob_l[0])
    height, width, layers = img.shape
    size = width, height
    img_array = []
    # Add all the files into the array
    for filename in glob_l:
        img_array.append(cv2.imread(filename))
    # Get the name of the video file
    img_src_loc = img_src.split("\\")[-2]
    strftime_pattern = "%d_%m_%Y"
    file = output_dir + f"output_{img_src_loc}_{date.today().strftime(strftime_pattern)}.mp4"
    # Create the video object
    out = cv2.VideoWriter(file, cv2.VideoWriter_fourcc(*'MP4V'), fps, size)
    # Add the images into the video
    for i in range(len(img_array)):
        out.write(img_array[i])
    # Export the video / Close the Video Writer
    out.release()
    return file, len(img_array)


def createTL(fps: int = default_fps):
    flore, rivotte = __getOrCreateDirs1()
    output = __getOrCreateDir2()
    # Flore
    # Create the video
    flore_vid, nb_flore = __createVid(flore, output, fps)
    print(f"Le timelapse de la place Flore a été enregistré sur \"{flore_vid}\" avec {nb_flore} images et {fps} fps."
          f"\nSoit une vidéo de {round(nb_flore / fps)} secondes.")
    # Rivotte
    # Create the video
    rivotte_vid, nb_rivotte = __createVid(rivotte, output, fps)
    print(f"Le timelapse de Rivotte a été enregistré sur \"{rivotte_vid}\" avec {nb_rivotte} images et {fps} fps."
          f"\nSoit une vidéo de {round(nb_rivotte / fps)} secondes.")

    return flore_vid, rivotte_vid


def deleteImages():
    flore, rivotte = __getOrCreateDirs1()
    _flore = [f for f in listdir(flore) if isfile(join(flore, f))]
    for file in _flore:
        os.remove(flore + file)
    _rivotte = [f for f in listdir(rivotte) if isfile(join(rivotte, f))]
    for file in _rivotte:
        os.remove(rivotte + file)
