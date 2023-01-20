from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import pandas as pd
import time
import collections
from functools import wraps
import deezer_api as deez

from tqdm import tqdm
tqdm.pandas()

chromedriver_path = r"modules/chromedriver.exe"


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
    table = parser.find("div",
                        attrs={"class": "chart-results-list // lrv-u-padding-t-150 lrv-u-padding-t-050@mobile-max"})
    return table


to_remove_from_song_titles = ['Imprint/Promotion Label:',
                              'Songwriter(s):',
                              'Producer(s):']


def extract_song_titles(table):
    song_titles = table.find_all("h3")
    ori_songlist = [h.text.strip() for h in song_titles[2:]]
    songlist = [word for word in ori_songlist if word not in to_remove_from_song_titles]
    return songlist


def extract_artists(table):
    to_remove_from_artists = ["", 'Share Chart on Twitter', 'Share Chart on Embed', 'This Week',
                              'Award',
                              'Last Week',
                              'Peak Pos.',
                              'Wks on Chart',
                              'Twitter',
                              'Share Chart on Copy Link',
                              'Copy Link',
                              'Share Chart on Facebook',
                              'Facebook',
                              'Embed',
                              'RIAA Certification:',
                              'Diamond',
                              "Platinum",
                              'Platinum x2',
                              'Platinum x3',
                              'Platinum x4',
                              'Platinum x5',
                              'Platinum x6',
                              'Platinum x7',
                              'Platinum x8',
                              'Platinum x9',
                              'RE-\nENTRY',
                              'Gold',
                              'NEW',
                              "-"]

    artists = table.find_all("span")
    artists = [h.text.strip() for h in artists]
    artists = [artists[i] for i in range(len(artists)) if artists[i] not in to_remove_from_artists if
               not artists[i].isdigit()]
    return artists


def convert_to_top_100(songlist, artists):
    top_100 = pd.concat([pd.Series(songlist), pd.Series(artists)], axis=1)
    top_100.rename(columns = {0:"title", 1:"artist"}, inplace=True)
    return top_100


def additional_infos(row):
    track_infos = deez.get_track_additional_infos(row.title, row.artist)
    row.genres = track_infos["genres"]
    row.duration = track_infos['duration']
    row.explicit_content = track_infos['explicit_lyrics']
    return row


def genres(row):
    row.genres = deez.get_track_genres(row.title, row.artist)
    return row


service = ChromeService(executable_path=chromedriver_path)
options = webdriver.ChromeOptions()
options.add_argument('-headless')


@timeit
def get_top_100(year, month, day, service=service, verbose=0, additional=False):
    driver = webdriver.Chrome(service=service, options=options)
    month = str(month)
    if len(month)==1:
        month = "0" + month
    day = str(day)
    if len(day)==1:
        day = "0" + day
    link = f"https://www.billboard.com/charts/hot-100/{year}-{month}-{day}/"
    src = get_page_source(link, driver)
    table = page_parser(src)
    songlist = extract_song_titles(table)
    artists = extract_artists(table)
    top_100 = convert_to_top_100(songlist, artists)
    if additional:
        top_100['genres'] = None
        top_100['duration'] = None
        top_100['explicit_content'] = None
        top_100 = top_100.apply(additional_infos, axis=1)
        if verbose==1:
            freq = collections.Counter(top_100.genres.sum())
            return top_100, dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
    return top_100


def top_100s(start, end):
    for annee in range(start, end):
        for month in range(1, 13):
            try:
                top_100 = get_top_100(annee, month, 1, additional=True)
                top_100.to_csv(
                    f"/month_top_100_temp/{annee}-{month}.csv",
                    sep=";")
            except:
                print(f"No top 100 in {annee}/{month}")


def hot100_year(year, month_folder=None):

    hot100_year = None

    def score(row):
        return 1/(row.name+1)

    def index_song(row):
        return str(row.artist) + " - " + str(row.title)

    for month in range(1, 12):
        try:
            hot100_month = pd.read_csv(f"data/month_top_100/{year}-{month}.csv", sep=";")
            hot100_month = hot100_month.drop(hot100_month.columns[0], axis=1)
            hot100_month['score'] = hot100_month.apply(score, axis=1)
            hot100_month['id'] = hot100_month.apply(index_song, axis=1)
            if hot100_year is None:
                hot100_year = hot100_month.copy()
            else:
                hot100_year = pd.concat([hot100_year, hot100_month])
        except:
            print(f"No top 100 in {year}")

    scores = hot100_year.groupby(by='id').score.sum().sort_values(ascending=False)

    def sort_year(row):
        return scores[row.id]

    all_song = hot100_year.drop("score", axis=1).drop_duplicates()
    all_song["score"] = all_song.apply(sort_year, axis=1)
    hot100 = all_song.sort_values(by="score", ascending=False)[:100].drop(["id", "score"], axis=1).reset_index(drop=True)

    return hot100


def hot100_years(start, end):
    for annee in tqdm(range(start, end+1)):
        hot100 = hot100_year(annee)
        hot100.to_csv(f"data/year_hot100/{annee}.csv", sep=";")


if __name__ == "__main__":
    hot100_years(1958, 2022)
    pass

