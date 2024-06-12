import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import psycopg2

# Database connection parameters
POSTGRES_ADDRESS = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'myuser'
POSTGRES_PASSWORD = 'mypassword'
POSTGRES_DBNAME = 'mydatabase'

# Function to create database connection
def create_connection():
    try:
        # Create connection with PostgreSQL
        conn = psycopg2.connect(
            user=POSTGRES_USERNAME,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_ADDRESS,
            port=POSTGRES_PORT,
            database=POSTGRES_DBNAME
        )
        return conn
    except psycopg2.Error as e:
        print(e)

# Function to fetch master dataframe
def fetch_master_df(conn): 
    try:
        # Create cursor to get data
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute('''
        SELECT "Latitude", "Longitude", "Name", "Type", "Sector", "Open/Closed", "State" FROM hospital_mapping
        ''')

        # Convert query results into a pandas DataFrame
        return pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
    except psycopg2.Error as e:
        print(e)

# Function to fetch values dataframe
def fetch_values_df(conn): 
    try:
        # Create cursor to get data
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute('''
        SELECT v."DataSetId", v."ReportingUnitCode", v."Value", h."Latitude", h."Longitude", h."Name", h."Type", h."Sector", h."Open/Closed", h."State"
        FROM values v
        JOIN hospital_mapping h ON v."ReportingUnitCode" = h."Code"
        ''')

        # Convert query results into a pandas DataFrame
        return pd.DataFrame(cursor.fetchall(), columns=['DataSetId', 'ReportingUnitCode', 'Value', 'Latitude', 'Longitude', 'Name', 'Type', 'Sector', 'Open/Closed', 'State'])
    except psycopg2.Error as e:
        print(e)

# Create connection
conn = create_connection()

# Get full data frame
master_df = fetch_master_df(conn)

# Fetch values data
values_df = fetch_values_df(conn)

# Ensure 'Sector' is numeric (if necessary, convert or use another numeric column)
if not pd.api.types.is_numeric_dtype(master_df['Sector']):
    master_df['Sector'] = pd.to_numeric(master_df['Sector'], errors='coerce')

# Mapbox Access Token
mapbox_access_token = 'pk.eyJ1IjoiY2hha3JpdHRob25nZWsiLCJhIjoiY2tkdTAzd2hwMDBkZzJycWluMnFicXFhdCJ9.JjJhMoek5126u1B_kwYNiA'
px.set_mapbox_access_token(mapbox_access_token)

# Create the map using Plotly Express
map_data = px.scatter_mapbox(
    master_df,
    lat="Latitude",
    lon="Longitude",
    color="Type", # Assuming 'Sector' can somehow quantify to adjust size
    color_continuous_scale=px.colors.cyclical.Edge,
    size_max=20,
    zoom=3,
    center={"lon": 135, "lat": -25},  # Centered on Australia
    hover_data={'Name': True, 'Type': True, 'Sector': True, 'Open/Closed': True, 'State': True},
    title='Map of Hospitals',
    template="seaborn"
)

map_data.update_layout(
    mapbox_style="light",  # You can also use "dark", "outdoors", "satellite", etc.
    mapbox_accesstoken=mapbox_access_token,
    hoverlabel=dict(
        bgcolor="white", 
        font_size=16, 
        font_family="Open Sans"
    ),
    height=600,
    width=700,
    title={
        'text': 'Map of Hospitals',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    font=dict(
        size=16,
        color="#4a4a4a"
    ),
    paper_bgcolor="#f8f9fa",
    plot_bgcolor="#f8f9fa",
    margin=dict(r=20, t=50, l=20, b=20)
)

# Bar chart for sum of values by hospital type
bar_chart = px.bar(
    values_df,
    x='Type',
    y='Value',
    color='Type',
    title='Sum of Values by Hospital Type',
    template="seaborn"
)

bar_chart.update_layout(
    hoverlabel=dict(
        bgcolor="white", 
        font_size=16, 
        font_family="Open Sans"
    ),
    height=600,
    width=700,
    title={
        'text': 'Sum of Values by Hospital Type',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    font=dict(
        size=16,
        color="#4a4a4a"
    ),
    paper_bgcolor="#f8f9fa",
    plot_bgcolor="#f8f9fa",
    margin=dict(r=20, t=50, l=20, b=20)
)

state_hospital_counts = master_df.groupby('State').size().reset_index(name='Number of Hospitals')

histogram = px.bar(state_hospital_counts, x='State', y='Number of Hospitals', title='Number of Hospitals per State')

# Adjusting layout if needed
histogram.update_layout(
    xaxis_title='State',
    yaxis_title='Number of Hospitals',
    height=600, 
    width=700,
    title={'text': 'Number of Hospitals per State', 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
    font=dict(size=16, color="#4a4a4a"),
    paper_bgcolor="#f8f9fa",
    plot_bgcolor="#f8f9fa",
    margin=dict(r=20, t=50, l=20, b=20)
)


app = dash.Dash(__name__)

# Define home page layout
home_layout = html.Div([
    html.H1("Welcome to Australian Healthcare Resource Allocation Dashboard", style={'text-align': 'center', 'color': '#4a4a4a'}),
    html.Div([
        html.P("This is the home page of the dashboard. Use the navigation bar to explore more."),
        html.P("You can navigate to the main dashboard by clicking on 'Dashboard' in the navigation bar above."),
    ], style={'margin': '20px auto', 'max-width': '600px', 'text-align': 'center'})
])

# Define main dashboard layout
dashboard_layout = html.Div([
    html.H1("Australian Healthcare Resource Allocation", style={'text-align': 'center', 'color': '#4a4a4a', 'margin-top': '20px'}),
    
    html.Div([
        # Map on the left
        html.Div([
            dcc.Graph(id='hospital-map', figure=map_data),
            html.Div(id='hospital-info', style={'margin-top': '20px'}),
        ], className='six columns'),  # Using 6 columns out of 12 grid columns
        
        # Histogram on the right
        html.Div([
            dcc.Graph(id='hospital-histogram', figure=histogram),  # Add histogram here
        ], className='six columns'),  # Using 6 columns out of 12 grid columns
    ], className='row'),  # Each row contains two columns
    
    # Add other components as needed
    dcc.Slider(
        id="years-slider",
        min=2000,
        max=2015,
        value=2000,
        marks={str(year): {"label": str(year), "style": {"color": "#7fafdf"}} for year in range(2000, 2016)},
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    
    html.Div(
        id="graph-container",
        children=[
            html.P(id="chart-selector", children="Select chart to display Malaysia Life Expectancy:", style={'font-weight': 'bold'}),
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
                style={'width': '50%', 'margin': '20px auto'}
            ),    
            dcc.Graph(
                id="selected-world-data",
                figure=dict(
                    data=[dict(x=0, y=0)],
                    layout=dict(
                        paper_bgcolor="#F4F4F8",
                        plot_bgcolor="#F4F4F8",
                        autofill=True,
                        margin=dict(t=75, r=50, b=100, l=50),
                    ),
                ),
            ),
        ],
        style={'margin-top': '20px'}
    ),
    
    html.H2("Sum of Values by Hospital Type", style={'text-align': 'center', 'color': '#4a4a4a', 'margin-top': '20px'}),
    dcc.Graph(id='value-bar-chart', figure=bar_chart),
])



# Define callback to switch between home page and main dashboard
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def display_page(pathname):
    if pathname == '/dashboard':
        return dashboard_layout
    else:
        return home_layout

# Define navigation bar
navbar = html.Div([
    dcc.Link('Home', href='/'),
    html.Span(' | '),
    dcc.Link('Dashboard', href='/dashboard')
], style={'text-align': 'center', 'margin-top': '10px'})

# Define app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

if __name__ == '__main__':
    app.run_server(debug=True)
