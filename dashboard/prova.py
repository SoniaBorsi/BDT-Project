# import plotly.express as px
# import pandas as pd
# from sqlalchemy import create_engine
# import plotly.graph_objects as go

# # PostgreSQL connection parameters
# POSTGRES_ADDRESS = 'localhost' 
# POSTGRES_PORT = '5432' 
# POSTGRES_USERNAME = 'myuser' 
# POSTGRES_PASSWORD = 'mypassword' 
# POSTGRES_DBNAME = 'mydatabase' 

# import plotly.graph_objects as go

# # Create connection string
# postgres_str = f'postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_ADDRESS}:{POSTGRES_PORT}/{POSTGRES_DBNAME}'

# engine = create_engine(postgres_str)

# # SQL query to retrieve hospital data
# query = "SELECT \"Latitude\", \"Longitude\", \"Name\", \"Type\", \"Sector\", \"Open/Closed\", \"State\" FROM hospital_mapping"

# # Execute query and fetch data into pandas DataFrame
# df = pd.read_sql(query, engine)

# # Define the map layout
# layout = go.Layout(
#     title="Hospitals in Australia",
#     geo=dict(
#         projection_scale=6,
#         center=dict(lat=-25, lon=135),
#     )
# )

# # Define custom JavaScript to handle map click events
# javascript = """
#     function(plotly_click) {
#         var hospitalInfo = plotly_click.points[0].customdata;
#         var tableContent = '<table border="1"><tr><th>Name</th><th>Type</th><th>Sector</th><th>Open/Closed</th><th>State</th></tr>';
#         tableContent += '<tr><td>' + hospitalInfo[0] + '</td><td>' + hospitalInfo[1] + '</td><td>' + hospitalInfo[2] + '</td><td>' + hospitalInfo[3] + '</td><td>' + hospitalInfo[4] + '</td></tr>';
#         tableContent += '</table>';
#         document.getElementById('hospital-info').innerHTML = tableContent;
#     }
# """

# # Plot data on map using Plotly
# fig = go.Figure(data=go.Scattergeo(
#         lon = df['Longitude'],
#         lat = df['Latitude'],
#         mode = 'markers',
#         marker_color = 'blue',
#         text = df['Name'],
#         customdata = df[['Name', 'Type', 'Sector', 'Open/Closed', 'State']].values,
#     ),
#     layout=layout
# )

# # Update figure with JavaScript
# fig.update_layout(
#     updatemenus=[dict(type="buttons", buttons=[dict(label="Reset", method="relayout", args=["mapbox", {"center": {"lat": -25, "lon": 135}}])])],
#     annotations=[dict(text='<div id="hospital-info"></div>', x=1.05, y=1, yanchor='top', xanchor='left', showarrow=False)],
#     )
# fig.update_geos(projection_scale=6, center=dict(lat=-25, lon=135))

# # Add custom JavaScript
# fig.add_layout_image(
#     dict(
#         source="",
#         xref="paper", yref="paper",
#         x=0, y=1, sizex=1, sizey=1,
#         sizing="stretch", opacity=0,
#         layer="above"
#     )
# )
# fig.add_layout_image(
#     dict(
#         source="https://codepen.io/plotly/pen/EQZeaW.js",
#         xref="paper", yref="paper",
#         x=0, y=1, sizex=1, sizey=1,
#         sizing="stretch", opacity=0,
#         layer="above"
#     )
# )
# fig.update_layout(
#     mapbox=dict(
#         style="white-bg",
#         layers=[],
#     ),
#     annotations=[
#         dict(
#             text="",
#             x=0,
#             y=1,
#             yref="paper",
#             xref="paper",
#             align="left",
#             showarrow=False
#         )
#     ]
# )
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import json
import requests

# # PostgreSQL connection parameters
# POSTGRES_ADDRESS = 'localhost'
# POSTGRES_PORT = '5432'
# POSTGRES_USERNAME = 'myuser'
# POSTGRES_PASSWORD = 'mypassword'
# POSTGRES_DBNAME = 'mydatabase'

# # Create connection string and engine
# postgres_str = f'postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_ADDRESS}:{POSTGRES_PORT}/{POSTGRES_DBNAME}'
# engine = create_engine(postgres_str)

# # SQL query to retrieve hospital data
# query = "SELECT \"Latitude\", \"Longitude\", \"Name\", \"Type\", \"Sector\", \"Open/Closed\", \"State\" FROM hospital_mapping"
# df = pd.read_sql(query, engine)

# # Load GeoJSON file
# geojson_url = 'https://raw.githubusercontent.com/tonywr71/GeoJson-Data/e33126bb38ede356f79737a160aa16f8addfd8b3/australian-states.json'
# response = requests.get(geojson_url)
# geojson_data = response.json()

# # Initialize the Dash application
# app = dash.Dash(__name__)

# # Define the layout of the app
# app.layout = html.Div([
#     html.H1("Australian Healthcare Resource Allocation", style={'text-align': 'center'}),
#     dcc.Graph(
#         id='hospital-map',
#         figure={
#             'data': [
#                 go.Scattergeo(
#                     lon=df['Longitude'],
#                     lat=df['Latitude'],
#                     text=df['Name'],
#                     mode='markers',
#                     marker=dict(color='blue', size=5, opacity=0.5),
#                     customdata=df[['Name', 'Type', 'Sector', 'Open/Closed', 'State']]
#                 )
#             ],
#             'layout': go.Layout(
#                 title='Map of Hospitals',
#                 geo=dict(
#                     scope='world',
#                     projection_scale=5,  # Scale for Australia
#                     center=dict(lat=-25, lon=135),  # Center on Australia
#                     showcountries=True,
#                     countrycolor='rgb(204, 204, 204)',
#                     showocean=True,
#                     oceancolor='rgb(0, 255, 255)',
#                     showlakes=True,
#                     lakecolor='rgb(0, 255, 255)',
#                     showcoastlines=True,
#                     coastlinewidth=2,
#                     coastlinecolor='rgb(0, 0, 255)',
#                     showframe=False,
#                     projection_type='equirectangular',
#                     showrivers=True,
#                     rivercolor='rgb(0, 0, 255)',
#                     showsubunits=True,
#                     # Remove geojson property
#                 )
#             )
#         }
#     ),
#     html.Div(id='hospital-info', style={'margin-top': '20px'})
# ])

# # Define callback to update hospital-info div
# @app.callback(
#     Output('hospital-info', 'children'),
#     [Input('hospital-map', 'clickData')]
# )
# def display_click_data(clickData):
#     if clickData is None:
#         return 'Click on a hospital to see details'
#     else:
#         info = clickData['points'][0]['customdata']
#         return html.Div([
#             html.Table(
#                 [html.Tr([html.Th(col, style={'padding': '8px', 'background-color': '#007BFF', 'color': 'white'}) for col in
#                           ['Name', 'Type', 'Sector', 'Open/Closed', 'State']])] +
#                 [html.Tr([
#                     html.Td(info[i], style={'padding': '8px', 'border': '1px solid #ddd'}) for i in range(len(info))
#                 ])],
#                 style={'width': '100%', 'margin-top': '20px', 'border-collapse': 'collapse'}
#             )
#         ])

# if __name__ == '__main__':
#     app.run_server(debug=True)

import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import requests

# PostgreSQL connection parameters
POSTGRES_ADDRESS = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'myuser'
POSTGRES_PASSWORD = 'mypassword'
POSTGRES_DBNAME = 'mydatabase'

# Create connection string and engine
postgres_str = f'postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_ADDRESS}:{POSTGRES_PORT}/{POSTGRES_DBNAME}'
engine = create_engine(postgres_str)

# SQL query to retrieve hospital data
query = "SELECT \"Latitude\", \"Longitude\", \"Name\", \"Type\", \"Sector\", \"Open/Closed\", \"State\" FROM hospital_mapping"
df = pd.read_sql(query, engine)

# Initialize the Dash application
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Australian Healthcare Resource Allocation", style={'text-align': 'center'}),
    dcc.Graph(
        id='hospital-map',
        figure={
            'data': [
                go.Scattergeo(
                    lon=df['Longitude'],
                    lat=df['Latitude'],
                    text=df['Name'],
                    mode='markers',
                    marker=dict(color='blue', size=5, opacity=0.5),
                    customdata=df[['Name', 'Type', 'Sector', 'Open/Closed', 'State']]
                )
            ],
            'layout': go.Layout(
                title='Map of Hospitals',
                geo=dict(
                    scope='world',
                    projection_scale=5,  # Scale for Australia
                    center=dict(lat=-25, lon=135),  # Center on Australia
                    showcountries=True,
                    countrycolor='rgb(204, 204, 204)',
                    showocean=True,
                    showlakes=True,
                    lakecolor='rgb(0, 255, 255)',
                    showcoastlines=True,
                    coastlinewidth=2,
                    coastlinecolor='rgb(0, 0, 255)',
                    showframe=False,
                    projection_type='equirectangular',
                    showrivers=True,
                    rivercolor='rgb(0, 0, 255)',
                    showsubunits=True,
                )
            )
        }
    ),
    html.Div(id='hospital-info', style={'margin-top': '20px'}),
    dcc.Slider(
        id="years-slider",
        min=2000,
        max=2015,
        value=2000,
        marks={str(year): {"label": str(year), "style": {"color": "#7fafdf"}} for year in range(2000, 2016)}
    ),
    html.Div(
        id="graph-container",
        children=[
            html.P(id="chart-selector", children="Select chart to display Malaysia Life Expectancy:"),
            dcc.Dropdown(
                options=[
                    {"label": "Life Expectancy Distribution Histogram", "value": "Life Expectancy Distribution Histogram"},
                    {"label": "Average Life Expectancy from 2010 to 2015", "value": "Average Life Expectancy from 2010 to 2015"},
                    {"label": "Life Expectancy Based on Sex", "value": "Life Expectancy Based on Sex"},
                    {"label": "Life Expectancy Based on Ethnicity", "value": "Life Expectancy Based on Ethnicity"},
                    {"label": "Life Expectancy over Years in Malaysia", "value": "Life Expectancy over Years in Malaysia"},
                    {"label": "Average Life Expectancy by Ethnic and Sex in Malaysia", "value": "Average Life Expectancy by Ethnic and Sex in Malaysia"},
                ],
                value="Life Expectancy Distribution Histogram",
                id="chart-dropdown",
            ),    
            dcc.Graph(
                id="selected-world-data",
                figure=dict(
                    data=[dict(x=0, y=0)],
                    layout=dict(
                        paper_bgcolor="#F4F4F8",
                        plot_bgdate="#F4F4F8",
                        autofill=True,
                        margin=dict(t=75, r=50, b=100, l=50),
                    ),
                ),
            ),
        ]
    )
])

@app.callback(
    Output('hospital-info', 'children'),
    [Input('hospital-map', 'clickData')]
)
def display_click_data(clickData):
    if clickData is None:
        return 'Click on a hospital to see details'
    else:
        info = clickData['points'][0]['customdata']
        return html.Div([
            html.Table(
                [html.Tr([html.Th(col, style={'padding': '8px', 'background-color': '#007BFF', 'color': 'white'}) for col in ['Name', 'Type', 'Sector', 'Open/Closed', 'State']])] +
                [html.Tr([html.Td(info[i], style={'padding': '8px', 'border': '1px solid #ddd'}) for i in range(len(info))])],
                style={'width': '100%', 'margin-top': '20px', 'border-collapse': 'collapse'}
            )
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
