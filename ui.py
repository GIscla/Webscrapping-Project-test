from flask import Flask, flash, render_template, request, redirect, url_for
import shutil
import os
import csv
import hot100_analysis as hot100
import top50_analysis as top50
import comparison_us_fr as comp

UPLOAD_FOLDER = 'static/uploads/'
SECRET_KEY = "secret key"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = SECRET_KEY


@app.route("/")
@app.route("/menu")
def page_menu():
    return render_template('menu.html')


@app.route("/menu", methods=['POST'])
def page_hot100():
    year = int(request.form["year"])
    month = int(request.form["month"])
    with open(f"data/month_top_100/{year}-{month}.csv") as file:
        reader = csv.reader(file, delimiter=';')
        data = list(reader)
    return render_template('hot100.html', csv=data, date=f"{year}-{month}")


@app.route("/stats_hot100")
def page_stats_hot100():
    data_file = "data/HOT100_year_bis.csv"
    save_genre = f"{UPLOAD_FOLDER}genres.png"
    save_duration = f"{UPLOAD_FOLDER}duration.png"
    hot100.music_evolution(1958, 2022, precision=20, file=data_file, save_genre=save_genre, save_duration=save_duration)
    return render_template('stats.html', genre_file=save_genre, duration_file=save_duration)


@app.route("/stats_top50")
def page_stats_top50():
    data_file = "data/Top50_year_bis.csv"
    save_genre = f"{UPLOAD_FOLDER}genres.png"
    save_duration = f"{UPLOAD_FOLDER}duration.png"
    top50.music_evolution(1961, 2022, precision=20, file=data_file, save_genre=save_genre, save_duration=save_duration)
    return render_template('stats.html', genre_file=save_genre, duration_file=save_duration)


@app.route("/etude_comparative")
def page_etude_comparative():
    save_similarity = f"{UPLOAD_FOLDER}similarity.png"
    save_genre_comp = f"{UPLOAD_FOLDER}genres_comp.png"
    save_percent_american = f"{UPLOAD_FOLDER}percent_american.png"
    genre="Rock"
    comp.comparison_all(1961, 2022, save_similarity=save_similarity, save_genre_comp=save_genre_comp,
                        save_american_percent=save_percent_american, genre=genre)
    return render_template('stats.html', similarity_file=save_similarity,
                           genre_comp_file=save_genre_comp, american_prop_file=save_percent_american)


if __name__ == "__main__":
    shutil.rmtree("static/uploads")
    os.mkdir("static/uploads")
    app.run(host="localhost", port=8080)