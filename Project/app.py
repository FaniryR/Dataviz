import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import altair as alt
import pydeck as pdk
import bar_chart_race as bcr


# Load data and initializations
data_filepath = "Project/consommation-regionale-gnc.csv"
shapefile_path = "Project/regions-20180101.shp"
    

def load_and_prepare_data(filepath, delimiter=';'):
    df = pd.read_csv(filepath, delimiter=delimiter)
    df[['latitude', 'longitude']] = df['centroid'].str.split(',', expand=True)
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].str.replace('"', '').astype(float)
    df.drop(columns=['geom', 'centroid'], inplace=True)
    return df


def merge_with_shapefile(data_df, shapefile_path):
    regions_shapefile = gpd.read_file(shapefile_path)
    regions_shapefile['code_insee'] = regions_shapefile['code_insee'].astype(int)
    merged_gdf = regions_shapefile.merge(
        data_df, left_on='code_insee', right_on='code_insee_region', how='left')
    return merged_gdf


def plot_comparison_chart(df_comparison, year1, year2):
    comparison_chart = alt.Chart(df_comparison).mark_bar().encode(
        x='region:N',
        y=alt.Y('consommation_gwh_pcs:Q', stack=True,
                title='Consommation (GWh PCS)'),
        color='annee:N',
        tooltip=['region', 'consommation_gwh_pcs']
    ).properties(
        title=f"Comparaison de la consommation de GNC entre {year1} et {year2}",
        width=700,
        height=400
    )
    st.altair_chart(comparison_chart, use_container_width=True)


def plot_trend_chart(df_region, region):
    trend_chart = alt.Chart(df_region).mark_line(point=True).encode(
        x='annee:O',
        y='consommation_gwh_pcs:Q',
        tooltip=['annee', 'consommation_gwh_pcs']
    ).properties(
        title=f"Tendance de la consommation de GNC pour {region}",
        width=700,
        height=400
    )
    st.altair_chart(trend_chart, use_container_width=True)


def plot_pie_chart(data, year):
    pie_chart = alt.Chart(data[data['annee'] == year]).mark_arc(innerRadius=50).encode(
        theta='consommation_gwh_pcs:Q',
        color='region:N',
        tooltip=['region', 'consommation_gwh_pcs']
    ).properties(
        title=f"Répartition de la consommation de GNC par région en {year}",
        width=400,
        height=400
    )
    st.altair_chart(pie_chart, use_container_width=True)


def plot_variation_chart(data_sorted, year1, year2):
    df_variation = data_sorted[data_sorted['annee'] == year2]
    variation_chart = alt.Chart(df_variation).mark_bar().encode(
        x='region:N',
        y=alt.Y('variation:Q', title="Variation annuelle (%)"),
        color=alt.condition(
            alt.datum.variation > 0,
            alt.value('green'),
            alt.value('red')
        ),
        tooltip=['region', 'variation']
    ).properties(
        title=f"Variation annuelle de la consommation de GNC entre {year1} et {year2}",
        width=700,
        height=400
    )
    st.altair_chart(variation_chart, use_container_width=True)




def main(data_filepath, shapefile_path):
    
    data = load_and_prepare_data(data_filepath, delimiter=';')
    merged_geodata = merge_with_shapefile(data, shapefile_path)
    st.title("Dashboard sur la consommation de GNC par région en France")
    st.write("""
Bienvenue sur ce tableau de bord qui présente la consommation de GNC par région en France.
GNC signifie Gaz Naturel Comprimé. C'est une alternative écologique aux carburants traditionnels pour les véhicules.
""")
    st.write("Vue d'ensemble des données:")
    st.write(data.head())

    # Sidebar and filters
    with st.sidebar:
        st.header("Filtres")
        st.write("""
        Utilisez les curseurs ci-dessous pour sélectionner deux années différentes afin de comparer la consommation de GNC entre elles.
        """)
        year1 = st.slider("Sélectionnez la première année", min_value=data['annee'].min(
        ), max_value=data['annee'].max(), value=data['annee'].min())
        year2 = st.slider("Sélectionnez la deuxième année", min_value=data['annee'].min(
        ), max_value=data['annee'].max(), value=data['annee'].max())
        selected_region = st.selectbox(
            "Sélectionnez une région pour voir la tendance de consommation", data['region'].unique())
        st.write("*** RAOBELINA Faniry***")
        st.write("#dataviz2023efrei")
        st.markdown("[GitHub](https://github.com/FaniryR)") 
        st.markdown("[LinkedIn](https://linkedin.com/in/faniry-raobelina/)")

    # Plotting comparison chart
    df_comparison = data[(data['annee'] == year1) | (data['annee'] == year2)]
    comparison_chart = alt.Chart(df_comparison).mark_bar().encode(
        x='region:N',
        y=alt.Y('consommation_gwh_pcs:Q', stack=True,
                title='Consommation (GWh PCS)'),
        color='annee:N',
        tooltip=['region', 'consommation_gwh_pcs']
    ).properties(
        title=f"Comparaison de la consommation de GNC entre {year1} et {year2}",
        width=700,
        height=400
    )
    st.altair_chart(comparison_chart, use_container_width=True)

    # Plotting trend chart
    df_region = data[data['region'] == selected_region]
    trend_chart = alt.Chart(df_region).mark_line(point=True).encode(
        x='annee:O',
        y='consommation_gwh_pcs:Q',
        tooltip=['annee', 'consommation_gwh_pcs']
    ).properties(
        title=f"Tendance de la consommation de GNC pour {selected_region}",
        width=700,
        height=400
    )
    st.altair_chart(trend_chart, use_container_width=True)

    # Plotting pie chart
    pie_chart = alt.Chart(data[data['annee'] == year1]).mark_arc(innerRadius=50).encode(
        theta='consommation_gwh_pcs:Q',
        color='region:N',
        tooltip=['region', 'consommation_gwh_pcs']
    ).properties(
        title=f"Répartition de la consommation de GNC par région en {year1}",
        width=400,
        height=400
    )
    st.altair_chart(pie_chart, use_container_width=True)

    # Descriptive statistics
    st.write("""
Ci-dessous, vous trouverez quelques statistiques descriptives sur la consommation de GNC pour l'année sélectionnée.
Cela inclut la moyenne, la médiane, les valeurs minimales et maximales, etc.
""")
    st.subheader(f"Statistiques descriptives pour {year1}")
    st.write(data[data['annee'] == year1]['consommation_gwh_pcs'].describe())

    # Histogram for the consumption distribution
    hist_chart = alt.Chart(data[data['annee'] == year1]).mark_bar().encode(
        alt.X("consommation_gwh_pcs:Q", bin=alt.Bin(
            maxbins=30), title="Consommation (GWh PCS)"),
        y='count()'
    ).properties(
        title=f"Distribution de la consommation de GNC en {year1}",
        width=700,
        height=400
    )
    st.altair_chart(hist_chart, use_container_width=True)

    # Top and bottom consuming regions
    st.subheader(f"Top 3 des régions consommatrices en {year1}")
    top_regions = data[data['annee'] == year1].nlargest(3, 'consommation_gwh_pcs')
    st.write(top_regions[['region', 'consommation_gwh_pcs']])

    st.subheader(f"3 régions les moins consommatrices en {year1}")
    bottom_regions = data[data['annee'] == year1].nsmallest(3, 'consommation_gwh_pcs')
    st.write(bottom_regions[['region', 'consommation_gwh_pcs']])

    # Annual variation
    data_sorted = data.sort_values(by=['region', 'annee'])
    data_sorted['variation'] = data_sorted.groupby(
        'region')['consommation_gwh_pcs'].pct_change() * 100
    df_variation = data_sorted[data_sorted['annee'] == year2]

    variation_chart = alt.Chart(df_variation).mark_bar().encode(
        x='region:N',
        y=alt.Y('variation:Q', title="Variation annuelle (%)"),
        color=alt.condition(
            alt.datum.variation > 0,
            alt.value('green'),
            alt.value('red')
        ),
        tooltip=['region', 'variation']
    ).properties(
        title=f"Variation annuelle de la consommation de GNC entre {year1} et {year2}",
        width=700,
        height=400
    )
    st.altair_chart(variation_chart, use_container_width=True)

    # 3D Map plotting
    df_map = data[data['annee'] == year1]
    layer = pdk.Layer(
        'ColumnLayer',
        data=df_map,
        get_position=['longitude', 'latitude'],
        get_elevation='consommation_gwh_pcs*10',
        elevation_scale=100,
        radius=5000,
        get_fill_color=[255, 140, 0, 150],
        pickable=True,
        opacity=0.6
    )
    view_state = pdk.ViewState(
        latitude=df_map['latitude'].mean(),
        longitude=df_map['longitude'].mean(),
        zoom=5,
        min_zoom=5,
        max_zoom=15,
        pitch=40.5,
        bearing=-27.36
    )
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    # Heatmap of consumption by year and region
    heatmap = alt.Chart(data).mark_rect().encode(
        x='region:N',
        y='annee:O',
        color=alt.Color('consommation_gwh_pcs:Q', 
                        scale=alt.Scale(scheme="blueorange"),
                        title='Consommation (GWh PCS)'),
        tooltip=['region', 'annee', 'consommation_gwh_pcs']
    ).properties(
        title="Carte de chaleur des consommations par année et par région",
        width=700,
        height=400
    )
    st.altair_chart(heatmap, use_container_width=True)

    # Choropleth map for GNC consumption by region
    regions = gpd.read_file(shapefile_path)
    regions['code_insee'] = regions['code_insee'].astype(str)
    data['code_insee_region'] = data['code_insee_region'].astype(str)
    merged_data = regions.merge(data, left_on='code_insee', right_on='code_insee_region')
    regions_to_remove = ['Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte']
    merged_data_metro = merged_data[~merged_data['nom'].isin(regions_to_remove)]
    fig, ax = plt.subplots(figsize=(15, 15))
    vmin = data['consommation_gwh_pcs'].min()
    vmax = data['consommation_gwh_pcs'].max()
    merged_data_metro.plot(column='consommation_gwh_pcs', 
                           cmap='coolwarm', 
                           linewidth=0.8, 
                           edgecolor='black', 
                           ax=ax, 
                           legend=True,
                           vmin=vmin,
                           vmax=vmax)
    ax.set_title(f'Consommation de GNC par région en France métropolitaine ({year1})', fontsize=15)
    st.pyplot(fig)

    # Bar chart race (Ensure you have the data for this and that bar_chart_race is imported)
    df_race = data.pivot(index='annee', columns='region', values='consommation_gwh_pcs')
    bcr.bar_chart_race(df=df_race, title='Consommation de GNC par région et par année', filename='bcr_race.gif')
    st.image('bcr_race.gif', caption='Consommation de GNC par région et par année', use_column_width=True)

    # Final message
    st.write("""
Merci d'avoir utilisé ce tableau de bord pour explorer la consommation de GNC par région en France.
N'hésitez pas à utiliser les filtres pour obtenir des informations plus détaillées.
""")


if __name__ == '__main__':
    data_filepath = "C:\\Users\\RAOBELINA Faniry\\Desktop\\Efrei\\M1\\Data Visualisation\\Project\\consommation-regionale-gnc.csv"
    shapefile_path = "C:\\Users\\RAOBELINA Faniry\\Desktop\\Efrei\\M1\\Data Visualisation\\Project\\regions-20180101.shp"
main(data_filepath, shapefile_path)
