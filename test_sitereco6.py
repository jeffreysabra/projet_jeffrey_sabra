import streamlit as st
import pandas as pd
from PIL import Image
import requests
from sklearn.neighbors import NearestNeighbors
from streamlit_searchbox import st_searchbox
from typing import List, Tuple
import time
import os

st.set_page_config(layout="wide", page_title="Movies reco")
#finalmerge_reco = pd.read_csv('C:/Users/33668/Project_2/site_reco/finalmerge_reco.csv')

csv_filename = "finalmerge_reco.csv" 
# csv_path = "./" + csv_filename
# print(os.path.abspath())
finalmerge_reco = pd.read_csv("finalmerge_reco.csv")


#image = Image.open("C:/Users/33668/Project_2/site_reco/Cine creuse.png")
image = Image.open("Cine creuse.png")
st.sidebar.image(image, use_column_width=True)
#image2 = Image.open("C:/Users/33668/Project_2/site_reco/image_logo_gpe.png")
image2 = Image.open("image_logo_gpe.png")
st.sidebar.image(image2, use_column_width=True)

st.header('Quel film recherchez vous?')

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)



#functions

@st.cache_data
def search_button(searchterm: str) -> List[str]:
    if not searchterm:
        return []
    filtered_titles = finalmerge_reco[finalmerge_reco['title'].str.contains(searchterm, case=False)]
    result = filtered_titles['title'].values.tolist()
    
    return result

@st.cache_data
def machinelearning(input_title, finalmerge):
    movie_to_search = [input_title]
    movie_without = finalmerge.loc[finalmerge['title'] != input_title]
    X = movie_without.select_dtypes('number')
    model = NearestNeighbors(n_neighbors=5)
    model.fit(X)
    indices = []
    distances = [] 
    for name in movie_to_search:
        stats = finalmerge.loc[finalmerge['title'] == name, X.columns]
        result = model.kneighbors(stats)
        distances = result[0][0]
        indices = result[1][0]
    recommendations = list(movie_without.iloc[indices]['title'])
    return recommendations  

# Application

selected_values = st_searchbox(search_button, default=None, label="Entrez le nom d'un film", clear_on_submit=True, keys='movie_searchbox')



if selected_values:
    st.header(f'Nos suggestions liées à {selected_values}')
    recommendations = machinelearning(selected_values, finalmerge_reco)
    
    try:
        titles = recommendations
        results = []

        for title in titles:

            url = f"http://www.omdbapi.com/?t={title}&apikey="
            response = requests.get(url)
            data = response.json()
            results.append(data)
        
        col_count = len(results)
        cols = st.columns(col_count)
              
        for i in range(col_count):
            with cols[i]:
                index = finalmerge_reco.index[finalmerge_reco['title'] == titles[i]].tolist()
                full_url = finalmerge_reco['full_url'].values[index[0]]
                overview = finalmerge_reco.loc[index[0], 'overview']
                average_rating=round(finalmerge_reco.loc[index[0], 'weighted_rating'])
                container = st.container()
                container.markdown(
                    f'<style>div[role="listbox"] > div:nth-child({i+1}) > div.css-1g8hz5j.e5i1odf3 {{ width: 250px; }}</style>',
                    unsafe_allow_html=True
                )
                
                container.image(full_url, use_column_width=True)
                container.write(titles[i])  
                container.write(overview)
                container.write("Note moyenne des spectateurs: " + str(average_rating))                
    except:
        st.error('No film found with these titles')


