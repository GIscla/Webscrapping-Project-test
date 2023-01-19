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
service = ChromeService(executable_path=chromedriver_path)
options = webdriver.ChromeOptions()
options.add_argument('-headless')


def get_page_source(link, driver):
    driver.get(link)
    src = driver.page_source
    return src


def page_parser(page, add=""):
    parser = BeautifulSoup(page, "lxml")
    table = parser.find("div",
                        attrs={"class": f"infobox_v3 noarchive{add}"})
    return table


def extract_nationality(artist):
    artist_base = artist
    driver = webdriver.Chrome(service=service, options=options)
    if "Feat." in artist:
        artist = artist.split(" Feat. ")[0]
    if "Mc" in artist:
        mc = artist.split("Mc")[1].title()
        artist = "".join(artist.split("Mc")[0] + "Mc" + mc)
    artist_format = "_".join(artist.split())
    try:
        page = get_page_source(f"https://fr.wikipedia.org/wiki/{artist_format}", driver)
        table = page_parser(page)
        if table is None:
            table = page_parser(page, add=" large")
        desc = table.find_all("tr")
    except:
        try:
            if " & " in artist:
                artist = artist.split(" & ")[0]
            artist_format = "_".join(artist.split())
            page = get_page_source(f"https://fr.wikipedia.org/wiki/{artist_format}", driver)
            table = page_parser(page)
            if table is None:
                table = page_parser(page, add=" large")
            desc = table.find_all("tr")
        except:
            try:
                artist_format_spe = artist_format + "_(groupe)"
                page = get_page_source(f"https://fr.wikipedia.org/wiki/{artist_format_spe}", driver)
                table = page_parser(page)
                if table is None:
                    table = page_parser(page, add=" large")
                desc = table.find_all("tr")
            except:
                try:
                    artist_format_spe = artist_format + "_(chanteur)"
                    page = get_page_source(f"https://fr.wikipedia.org/wiki/{artist_format_spe}", driver)
                    table = page_parser(page)
                    if table is None:
                        table = page_parser(page, add=" large")
                    desc = table.find_all("tr")
                except:
                    try:
                        artist_format_spe = artist_format + "_(rappeur)"
                        page = get_page_source(f"https://fr.wikipedia.org/wiki/{artist_format_spe}", driver)
                        table = page_parser(page)
                        if table is None:
                            table = page_parser(page, add=" large")
                        desc = table.find_all("tr")
                    except:
                        print(f"Nationalité de {artist_base} inconnue")
                        driver.close()
                        return "Inconnue"

    desc = [h.text.strip() for h in desc]
    nationality = [h[11:].replace(" ", "") for h in desc if h[:9] == "Naissance"]
    if len(nationality) == 0:
        nationality = [h[19:].split("(")[0].replace(" ", "") for h in desc if h[:14]=="Pays d'origine"]
        if len(nationality) == 0:
            print(f"Nationalité de {artist_base} inconnue")
            driver.close()
            return "Inconnue"
        else:
            nat = nationality[0]
    else:
        nat = nationality[0]
        nat = nat.split("(")[-1].replace(")", "").split(",")[-1]
    driver.close()
    return nat


if __name__ == "__main__":
    print(extract_nationality(""))
    pass

