import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random


class Films:
    def __init__(self):
        self.config = self.get_config()
        self.films = self.get_films()
        self.counter = 0  # For counting how many comparisons have been made
        self.rating = 2.5  # The suggested rating for the user
        self.worse = 1  # counter for worse ratings
        self.better = 1  # counter for better ratings
        self.film_rating = 0  # the rating of the comparison film
        self.ratings = [2.5]  # list of comparison ratings
        self.username = self.config["username"]

    def get_config(self):
        with open("config.json", "r") as f:
            config = json.load(f)
        return config

    def check_user(self):
        username = self.get_config()["username"]
        # then we check if the username is valid
        r = requests.get(f"https://letterboxd.com/{username}/films")
        # user does not exist or no defined username
        if r.status_code == 404 or r.url == 'https://letterboxd.com/films/':
            return False
        html_content = r.text
        return html_content

    def convert_rating(self, rating):
        rating_dict = {
            "★★★★★": 5,
            "★★★★½": 4.5,
            "★★★★": 4,
            "★★★½": 3.5,
            "★★★": 3,
            "★★½": 2.5,
            "★★": 2,
            "★½": 1.5,
            "★": 1,
            "½": 0.5
        }
        return rating_dict.get(rating, 0)

    def get_movie_posters(self):
        url = f"https://www.letterboxd.com/kommtoby/films"
        # we have to use selenium because the poster is loaded in with javascript
        options = webdriver.ChromeOptions()
        # Does not open the browser on the users pc
        options.add_argument('--headless')
        with webdriver.Chrome(options=options) as driver:
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, "image")))
            li_elements = driver.find_elements(By.CLASS_NAME, "image")
            posters = {}
            for li in li_elements:
                movie_name = li.get_attribute("alt")
                poster_url = li.get_attribute("src")
                posters[movie_name] = poster_url
        return posters

    def get_films(self):
        watched_films = {}
        html_content = self.check_user()
        if html_content:  # user exists
            soup = BeautifulSoup(html_content, 'html.parser')
            films = soup.find_all("li", {'class': "poster-container"})
            # shuffle the films so that the order is random
            random.shuffle(films)
            posters = self.get_movie_posters()
            for film in films:
                rating = film.text.split("\n")[1].split("     ")[
                    1].replace(" ", "")
                title = str(film.find("img")["alt"])
                watched_films[title] = [
                    self.convert_rating(rating), posters[title]]
            return watched_films
        else:  # user does not exist
            return False
