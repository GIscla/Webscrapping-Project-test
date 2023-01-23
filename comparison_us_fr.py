import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path_hot50=r'data/year_top_50'
path_hot100=r'data/year_hot100'

def load_top_50_us(annee):
    top_50_us = pd.read_csv(path_hot100+f"/{annee}.csv", sep=";", nrows=50)
    return top_50_us

def load_top_50_fr(annee):
    top_50_fr = pd.read_csv(path_hot50+f"/{annee}.csv", sep=";")
    return top_50_fr

########################################################################################

#retourne le pourcentage de similarité entre 2 top 50
def percent_similarity(df1,df2):
    listcomb=df1.title.values.tolist()+df2.title.values.tolist()
    final=list(set(listcomb))
    return((100-len(final))*2)    

#retourne le graph comparant la similarité des top 50 en France et aux USA
def graph_percent_simil(starty, endy, save_name=None):
    percent=[]
    date=[]
    for i in range(starty, endy+1, 4):
        percent.append(percent_similarity(load_top_50_fr(i), load_top_50_us(i)))
        date.append(i)
    fig, ax = plt.subplots()
    ax.plot(date,percent)
    ax.set_ylabel("Similitarity in percent")
    if save_name is not None:
        fig.savefig(save_name)
    
##########################################################################################

#retourne le pourcentage de musique (dans un top 50) appartenant à un genre donné lors d'un année donnée
def get_genre_percent(df,genre):
    nombre=0
    for i in range(50):
        if genre in df.genres.values[i]:
            nombre+=1
    return(nombre*2)

#retourne le graph comparant le pourcentage d'apparition d'un genre donnée entre la France et les USA
def graph_genre_percent(starty, endy, genre, save_name=None ) :
    number1=[]
    number2=[]
    date=[]
    fig, ax = plt.subplots()
    for i in range(starty, endy+1, 3):
        number1.append(get_genre_percent(load_top_50_us(i), genre))
        number2.append(get_genre_percent(load_top_50_fr(i), genre))
        date.append(i)
    ax.plot(date,number1,label="U.S.A.")
    ax.plot(date,number2,label="France")
    ax.set_ylabel("Percent in the Top 50")
    ax.legend()
    fig.savefig(save_name)

#Genre à montrer :
#Rock
#Pop
#Country
#R&B
#Rap/Hip-Hop
#Dance
#Disco
#Electro
#Techno/House

#########################################################################################

#pourcentage d'américain dans top français
def get_amer_percent(df):
    number=0
    for i in range(50):
        if pd.notnull(df.pays.values[i]):
            if ("États-Unis" in df.pays.values[i]) or ("États-Unis" in df.pays.values[i]) :
                number+=1
    return(number*2)

#pourcentage d'américain dans top français dans le temps
def graph_percent_amer(starty, endy, save_name=None):
    percent=[]
    date=[]
    fig, ax = plt.subplots()
    for i in range(starty, endy+1, 3):
        percent.append(get_amer_percent(load_top_50_fr(i)))
        date.append(i)
    ax.plot(date,percent)
    ax.set_ylabel("Number of americans in percent")
    fig.savefig(save_name)
    
    
#pourcentage d'américain et d'"inconnue" dans top français 
def get_amer_inc_percent(df):
    number=0
    for i in range(50):
        if pd.notnull(df.pays.values[i]):
            if ("États-Unis" in df.pays.values[i]) or ("États-Unis" in df.pays.values[i]) or ("Inconnue" in df.pays.values[i]) :
                number+=1
    return(number*2)

#pourcentage d'américain et d'"inconnue" dans top français dans le temps
def graph_percent_amer_inc(starty, endy):
    percent=[]
    date=[]
    for i in range(starty, endy+1, 3):
        percent.append(get_amer_inc_percent(load_top_50_fr(i)))
        date.append(i)
    plt.plot(date,percent)
    plt.ylabel("Number of americans in percent")
    plt.show()
    
    
def comparison_all(starty, endy, save_similarity=None, save_genre_comp=None, genre=None, save_american_percent=None):
    graph_percent_simil(starty, endy, save_similarity)
    graph_genre_percent(starty, endy, save_name=save_genre_comp, genre=genre)
    graph_percent_amer(starty, endy, save_american_percent)
    
