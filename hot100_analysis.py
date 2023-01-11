import pandas as pd
import collections
import ast
import datetime as dt
from matplotlib import pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

GENRES = []


def load_top_100(annee, month):
    top_100 = pd.read_csv(f"data/month_top_100/{annee}-{month}.csv", sep=";")
    return top_100


def genres(row):
    row.genres = ast.literal_eval(row.genres)
    return row


def best_genres(top_100):
    freq = collections.Counter(top_100.apply(genres, axis=1).genres.sum())
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))


def avg_duration(top_100):
    minutes, seconds = divmod(round(top_100.duration.mean()), 60)
    return f"{minutes:02d}:{seconds:02d}"


def get_all_genres(df):
    global GENRES
    genres = []
    for i in range(len(df)):
        genres.extend(list(df.iloc[i].genres.keys()))
    GENRES = set(genres)
    return GENRES


def HOT100_history(start, end):
    data_top_100 = []
    for year in range(start, end):
        for month in range(1, 13):
            try:
                top_100 = load_top_100(year, month)
                data = dict()
                data["date"] = dt.datetime(year, month, 1)
                data["year"] = year
                data["month"] = month
                data["duration"] = round(top_100.duration.mean())
                data["genres"] = best_genres(top_100)
                data_top_100.append(data)
            except:
                print(f"No top100 in: {year}/{month}")
                pass
    df = pd.DataFrame(data_top_100)
    return df


def HOT_100_genres(df):
    all_genres = get_all_genres(df)
    for genre in all_genres:
        df[genre] = 0
        df[f"{genre}_prop"] = 0

    def genres_cat(row):
        for key in list(row.genres.keys()):
            row[key] = row.genres[key]
        return row

    def genres_prop(row):
        for key in list(row.genres.keys()):
            row[f"{key}_prop"] = round(row[key] * 100 / (sum(list(row.genres.values()))), 1)
        return row

    df = df.apply(genres_cat, axis=1)
    df = df.apply(genres_prop, axis=1)
    return df


def HOT100_history_by_year(df):
    global GENRES

    df_year = pd.DataFrame(df.year.unique(), columns=['year'])
    df_year["year"] = df_year.year.astype(int)
    df_year["duration"] = None

    for genre in GENRES:
        df_year[genre] = 0
        df_year[f"{genre}_prop"] = 0

    def year_genres(row):
        for genre in GENRES:
            row[genre] = df.groupby(by="year")[genre].sum()[row.year]
        return row

    def year_genres_prop(row):
        for genre in GENRES:
            somme = sum([row[g] for g in GENRES])
            row[f"{genre}_prop"] = round(row[genre] * 100 / somme, 1)
        return row

    def year_duration(row):
        row.duration = round(df.groupby(by="year").duration.mean()[row.year])
        return row

    df_year = df_year.apply(year_genres, axis=1)
    df_year = df_year.apply(year_genres_prop, axis=1)
    df_year = df_year.apply(year_duration, axis=1)
    return df_year


def plot_genres_evolution(df, precision=20, save_name=None):
    fig, ax = plt.subplots(figsize=(10, 5))

    genres_pop = dict()
    for genre in df.columns:
        try:
            genres_pop[genre] = df[f"{genre}_prop"].max()
        except:
            pass

    genres_pop = dict(sorted(genres_pop.items(), key=lambda x: x[1], reverse=True))

    for genre in list(genres_pop.keys())[:5]:
        X_Y_Spline = make_interp_spline(df.year, df[f"{genre}_prop"], 3)
        X_ = df.year.iloc[np.linspace(0, len(df)-1, precision)]
        Y_ = X_Y_Spline(X_)
        ax.plot(X_, Y_)

    ax.legend(list(genres_pop.keys())[:5])
    ax.set_ylabel("Hot100 %")
    if save_name is not None:
        fig.savefig(save_name)


def plot_duration_evolution(df, precision=20, save_name=None):
    fig, ax = plt.subplots(figsize=(10, 5))
    X_Y_Spline = make_interp_spline(df.year, df.duration, 3)
    X_ = df.year.iloc[np.linspace(0, len(df) - 1, precision)]
    Y_ = X_Y_Spline(X_)
    ax.plot(X_, Y_)
    ax.set_ylim(100, 350)
    ax.set_ylabel("durations(s)")
    if save_name is not None:
        fig.savefig(save_name)


def music_evolution(start, end, precision=20, file=None, save_genre=None, save_duration=None):
    if file:
        data = pd.read_csv(file, sep=";")
        data = data[(data.year >= start) & (data.year <= end)]
        data = data.drop(data.columns[0], axis=1)
    else:
        data = HOT100_history(start, end)
        data = HOT_100_genres(data)
        data = HOT100_history_by_year(data)
    plot_duration_evolution(data, precision, save_duration)
    plot_genres_evolution(data, precision, save_genre)


if __name__ == "__main__":
    df = HOT100_history(1958, 2022)
    df = HOT_100_genres(df)
    df = HOT100_history_by_year(df)
    df.to_csv(f"data/HOT100_year_bis.csv", sep=";")

