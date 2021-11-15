# Weather Bot Besac
**Weather_besac** is a French [twitter bot](https://twitter.com/BesanconMeteo) that tweet the weather of the city of Besançon in Franche-Comté in France every day at 8am and 4pm.

1. [Installation](#Installation)
1. [Library Used](#Library-Used)

## Installation

- Git clone the repository (`git clone https://github.com/R-Gld/weather_besac_bot_twitter.git`)
- Install the libraries (`pip install -r requirements.txt`)
- Launch the bot (`python3 main.py`)

## Library Used
- [Tweepy](https://github.com/tweepy/tweepy) (Used to connect to twitter)
- [requests](https://github.com/psf/requests) (Used to download every picture of Besançon)
- [APScheduler](https://github.com/agronholm/apscheduler/tree/master) (Advanced Python Scheduler) (Used to schedule every action on the bot like tweet the weather)
- [OpenCV](https://github.com/opencv/opencv-python)