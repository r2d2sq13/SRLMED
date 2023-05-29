import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import math
import folium
from streamlit_folium import folium_static

# Wczytanie danych z pliku CSV
@st.cache
def load_data():
    return pd.read_csv('dane1.csv')

data = load_data()

st.title("Przykładowa aplikacja Streamlit")

# Liczba rekordów zaczytanych z pliku CSV
liczba_rekordow = len(data)
st.write(f"Liczba rekordów zaczytanych z pliku CSV: {liczba_rekordow}")

# Definicja wag dla kryteriów selekcji
weights = st.sidebar.slider('Wagi dla kryteriów selekcji', min_value=0.0, max_value=1.0, value=0.3, step=0.05)

# Miejsce na resztę kodu...

# Funkcja do zmiany wag
def zmien_wagi():
    st.write("Zmiana wag kryteriów:")
    for kryterium, waga in weights.items():
        waga = st.sidebar.slider(kryterium, min_value=0.0, max_value=1.0, value=waga, step=0.05)
        weights[kryterium] = waga
    st.write("Zaktualizowano wagi kryteriów!")

zmien_wagi()

# Obliczenie wskaźnika dla każdej jednostki na podstawie wag kryteriów
ratios = {}
for i, record in data.iterrows():
    jednostka = record['Nazwa_jednostki']
    ratio = 0
    for kryterium, waga in weights.items():
        value = record[kryterium].replace(',', '.')
        if kryterium == 'pow_ob_ch_km_kw':
            value = math.ceil(float(value))
        ratio += float(value) * waga
    ratios[jednostka] = ratio

# Wybór jednostek do uwzględnienia w obliczeniach
wybor = st.selectbox("Wybierz jednostki do uwzględnienia w obliczeniach:", ["Wszystkie jednostki", "Jednostki powyżej >=9 strażaków na zmianie"])
if wybor == "Wszystkie jednostki":
    jednostki_do_obliczen = data
elif wybor == "Jednostki powyżej >=9 strażaków na zmianie":
    jednostki_do_obliczen = data[data['Liczba_strazakow_na_zm'] >= 9]

# Obliczenie wskaźnika dla wybranych jednostek na podstawie wag kryteriów
ratios = {}
for i, record in jednostki_do_obliczen.iterrows():
    jednostka = record['Nazwa_jednostki']
    ratio = 0
    for kryterium, waga in weights.items():
        value = record[kryterium].replace(',', '.')
        if kryterium == 'pow_ob_ch_km_kw':
            value = math.ceil(float(value))
        ratio += float(value) * waga
    ratios[jednostka] = ratio

# Wyświetlenie liczby karetek do rozdysponowania
liczba_karetek = st.number_input("Podaj liczbę karetek do rozdysponowania: ", min_value=0, max_value=100, value=1, step=1)

# Wybór jednostek z najwyższym wskaźnikiem
priorytetowe_lokalizacje = sorted(ratios, key=ratios.get, reverse=True)[:liczba_karetek]

# Miejsce na resztę kodu...

# Wyświetlenie lokalizacji priorytetowych na mapie OSM
mapa = folium.Map(location=[52.237049, 21.017532], zoom_start=10)

# Przygotowanie danych geograficznych i etykiet
geographic_data = [[float(record['Lat']), float(record['Long'])] for i, record in data.iterrows()]
labels = [[record['Nr_ID_JRG'], record['Nazwa_jednostki'], record['Nazwa_komendy_KW']] for i, record in data.iterrows()]

# Wykorzystanie algorytmu K-means do grupowania lokalizacji priorytetowych
kmeans = KMeans(n_clusters=liczba_karetek, random_state=0).fit(geographic_data)
cluster_centers = kmeans.cluster_centers_

# Dodanie znaczników na mapie dla lokalizacji priorytetowych
for i in range(len(cluster_centers)):
    folium.Marker(
        location=cluster_centers[i],
        icon=folium.Icon(color='red', icon='star'),
        popup=folium.Popup(labels[i][0] + '<br>' + labels[i][1] + '<br>' + labels[i][2], max_width=200)
    ).add_to(mapa)

# Dodanie warstwy dla wszystkich jednostek
for i, record in data.iterrows():
    folium.Marker(
        location=[float(record['Lat']), float(record['Long'])],
        icon=folium.Icon(color='green', icon='fire'),
        popup=folium.Popup(record['Nr_ID_JRG'] + '<br>' + record['Nazwa_jednostki'] + '<br>' + record['Nazwa_komendy_KW'], max_width=100)
    ).add_to(mapa)

# Wyświetlenie mapy
folium_static(mapa)

