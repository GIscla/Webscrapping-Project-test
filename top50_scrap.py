from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import pandas as pd
import time
import collections
from functools import wraps
import deezer_api as deez
import wikipedia_scrap as wiki

from tqdm import tqdm
tqdm.pandas()

chromedriver_path = r"modules/chromedriver.exe"
artists_nationalities = dict()


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__} {args} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


def get_page_source(link, driver):
    driver.get(link)
    src = driver.page_source
    return src


def page_parser(page):
    parser = BeautifulSoup(page, "lxml")
    table = parser.find("tbody")
    return table


to_remove_from_song_titles = ['Imprint/Promotion Label:',
                              'Songwriter(s):',
                              'Producer(s):']


def extract_song_titles(table):
    song_titles = table.find_all("td")
    words = [h.text.strip() for h in song_titles]
    songlist = [words[i] for i in range(len(words)) if (i+1)%3==0]
    return songlist


def extract_artists(table):
    song_titles = table.find_all("td")
    words = [h.text.strip() for h in song_titles]
    artistlist = [words[i].title() for i in range(len(words)) if (i + 2) % 3 == 0]
    return artistlist


def convert_to_top_100(songlist, artists):
    top_100 = pd.concat([pd.Series(songlist), pd.Series(artists)], axis=1)
    top_100.rename(columns = {0:"title", 1:"artist"}, inplace=True)
    return top_100


def additional_infos(row):
    global artists_nationalities
    track_infos = deez.get_track_additional_infos(row.title, row.artist)
    row.genres = track_infos["genres"]
    row.duration = track_infos['duration']
    row.explicit_content = track_infos['explicit_lyrics']
    if row.artist not in artists_nationalities.keys():
        row.pays = wiki.extract_nationality(row.artist)
        artists_nationalities[row.artist] = row.pays
    else:
        row.pays = artists_nationalities[row.artist]
    return row


def genres(row):
    row.genres = deez.get_track_genres(row.title, row.artist)
    return row


service = ChromeService(executable_path=chromedriver_path)
options = webdriver.ChromeOptions()
options.add_argument('-headless')


@timeit
def get_top_50(year, service=service, verbose=0, additional=False):
    driver = webdriver.Chrome(service=service, options=options)
    link = f"https://tubesenfrance.com/annees-{str(year)[-2]}0/classements-de-{year}/"
    src = get_page_source(link, driver)
    table = page_parser(src)
    songlist = extract_song_titles(table)
    artists = extract_artists(table)
    top_100 = convert_to_top_100(songlist, artists)
    if additional:
        top_100['genres'] = None
        top_100['duration'] = None
        top_100['pays'] = None
        top_100['explicit_content'] = None
        top_100 = top_100.apply(additional_infos, axis=1)
        if verbose==1:
            freq = collections.Counter(top_100.genres.sum())
            return top_100, dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
    return top_100


def top_50s(start, end):
    for annee in range(start, end+1):
        top_50 = get_top_50(annee, additional=True)
        top_50.to_csv(
            f"./data/year_top_50/{annee}.csv",
            sep=";")


if __name__ == "__main__":
    top_50s(1998, 2022)
    pass

