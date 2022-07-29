import streamlit as st
import pandas as pd
import base64 #used to download csv file, and converts ASCII
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Naming the webapp
st.title('NBA Players Stats Explorer \nby KeeObom')

st.markdown("""
This app performs simple webscraping of NBA player stats data!
* **Python Libraries:** base64, pandas, streamlit
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com)"""
)

# Sidebar Year selection
st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950,2022))))

# Web Scraping of NBA player stats
@st.cache # Used to cache loaded data so it won't have to load again
def load_data(year):
	url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
	html = pd.read_html(url, header = 0)
	df = html[0]
	raw = df.drop(df[df.Age == 'Age'].index) # Deletes age with age value of string age
	raw = raw.fillna(0)
	playerstats = raw.drop(['Rk'], axis=1)
	return playerstats
playerstats = load_data(selected_year)

# Sidebar - Team selection
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['C', 'PF', 'SF', 'PG', 'SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)
# sorted unique_pos is written twice so the full list is shown then we can deselect; 
# otherwise if written once, we will have to use the down menu and select one at a time

# Filtering the data to match the selected information
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team))&(playerstats.Pos.isin(selected_pos))]

# Displaying header, dimension and dataframe
st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns')
test = df_selected_team.astype(str) # Streamlit does not support numpy conversion system so we change the dataframe to a string 
#st.dataframe(df_selected_team)
st.dataframe(test)

# Download NBA player stats data
# https://discuss.streamlit.io/how-to-download-file-in-streamlit/1806
def filedownload(df):
	csv = df.to_csv(index=False)
	b64 = base64.b64encode(csv.encode()).decode() # strings
	href = f'<a href="data:file/csv;base64,{b64}" download="playstats.csv">Download CSV File'

	return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
# Using a button to show or hide heatmap
if st.button('Intercorrelation Heatmap'):
	st.header('Intercorrelation Matrix Heatmap')
	df_selected_team.to_csv('output.csv', index=False)
	df = pd.read_csv('output.csv')

	corr = df.corr()
	mask = np.zeros_like(corr)
	mask[np.triu_indices_from(mask)] = True
	with sns.axes_style('white'):
		f, ax = plt.subplots(figsize=(7, 5))
		ax  = sns.heatmap(corr, mask=mask, vmax=1, square=True)
	st.pyplot()