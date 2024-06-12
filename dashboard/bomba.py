import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import folium
from streamlit_folium import folium_static
from streamlit_chat import message
import streamlit as st

# Database connection parameters
POSTGRES_ADDRESS = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'myuser'
POSTGRES_PASSWORD = 'mypassword'
POSTGRES_DBNAME = 'mydatabase'

# Function to create database connection
def create_connection():
    """Establish a connection to the database."""
    try:
        return psycopg2.connect(
            user=POSTGRES_USERNAME,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_ADDRESS,
            port=POSTGRES_PORT,
            database=POSTGRES_DBNAME
        )
    except psycopg2.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

# Function to fetch data from the database
def fetch_data(sql):
    """Fetch data from the database based on SQL query."""
    conn = create_connection()
    if conn is not None:
        try:
            df = pd.read_sql(sql, conn)
            conn.close()
            return df
        except psycopg2.Error as e:
            st.error(f"Failed to fetch data: {e}")
    return pd.DataFrame()

# Function to display the home page
def display_home_page():
    st.title("Welcome to Healthcare Resource Allocation")
    st.write("""
        This application is designed to facilitate healthcare resource allocation through data visualization and a chatbot interface.
        
        Use the sidebar to navigate through different sections:
        - Visualization Types: Select from Histogram, Pie Chart, Hospitals, or Chatbot.
        - Hide Sidebar: Toggle the visibility of the sidebar.
        
        Start exploring the available features to gain insights into healthcare resource allocation.
    """)
    # Add general plots or any other content you want to display on the home page
    st.markdown("### General Plots")
    # Example plot
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [10, 20, 30, 40, 50]
    })
    fig = px.line(df, x='x', y='y', title='Example Plot')
    st.plotly_chart(fig)


def display_hospitals():
    """Display hospitals on a map, as a pie chart, and in a table."""
    st.title("Hospitals")
    
    # Fetch hospital data from the database
    df = fetch_data('SELECT "Latitude", "Longitude", "Name", "Type", "Sector", "Open/Closed", "State" FROM hospital_mapping')
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

    hospital_map = folium.Map(location=[-25, 135], zoom_start=5)
    for _, row in df.iterrows():
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=row['Name']
        ).add_to(hospital_map)
    folium_static(hospital_map)

    state_sector_counts = df.groupby(['State', 'Sector']).size().reset_index(name='Number of Hospitals')

    private_hospitals = state_sector_counts[state_sector_counts['Sector'] == 'Private']
    public_hospitals = state_sector_counts[state_sector_counts['Sector'] == 'Public']

    state_counts = pd.merge(private_hospitals, public_hospitals, on='State', suffixes=('_private', '_public'), how='outer').fillna(0)

    # Display a pie chart for the total private and public hospitals in Australia
    total_private_hospitals = private_hospitals['Number of Hospitals'].sum() if not private_hospitals.empty else 0
    total_public_hospitals = public_hospitals['Number of Hospitals'].sum() if not public_hospitals.empty else 0

    fig_pie = px.pie(names=['Private', 'Public'], values=[total_private_hospitals, total_public_hospitals], 
                 title="Total Private and Public Hospitals in Australia")
    st.plotly_chart(fig_pie)

    # Display a histogram for the number of private and public hospitals per state
    fig_hist = px.bar(state_counts, x='State', y=['Number of Hospitals_private', 'Number of Hospitals_public'], barmode='group', 
                 title="Number of Private and Public Hospitals per State", labels={'value': 'Number of Hospitals', 'variable': 'Hospital Type'})
    fig_hist.update_layout(xaxis_title="State", yaxis_title="Count")
    st.plotly_chart(fig_hist)

    # Display hospitals based on selected state, open/closed status, and sector
    selected_state = st.selectbox("Select State", df['State'].unique())
    selected_status = st.selectbox("Select Open/Closed", df['Open/Closed'].unique())
    selected_sector = st.selectbox("Select Sector", df['Sector'].unique())
    
    st.markdown(f"### Hospitals in {selected_state} - {selected_status} - {selected_sector}")
    
    filtered_df = df[(df['State'] == selected_state) & (df['Open/Closed'] == selected_status) & (df['Sector'] == selected_sector)]
    
    if not filtered_df.empty:
        st.table(filtered_df)
    else:
        st.write("No hospitals found with the selected criteria.")

def display_chatbot():
    """Display a chatbot interface."""
    st.title("Chat with our Healthcare Bot")
    user_input = st.text_input("Message", key="chat_input")
    if st.button("Send"):
        process_user_message(user_input.strip().lower())

# Function to process and respond to the user's message based on predefined responses
def process_user_message(user_message):
    """Process and respond to the user's message based on predefined responses."""
    responses = {
        "hello": "Hello! How can I assist you today?",
        "how are you": "I'm a bot, so I don't have feelings, but thanks for asking!",
        "help": "Sure, I can help you! What do you need assistance with?",
        "goodbye": "Goodbye! Have a great day!",
    }

    response = responses.get(user_message, "I'm not sure how to respond to that. Can you try asking something else?")
    
    if 'past' not in st.session_state:
        st.session_state.past = []
    if 'generated' not in st.session_state:
        st.session_state.generated = []

    st.session_state.past.append(user_message)
    st.session_state.generated.append(response)

    for i in range(len(st.session_state.past)):
        st.write(st.session_state.past[i])
        st.write(st.session_state.generated[i])

if __name__ == '__main__':
    st.sidebar.title("Healthcare Resource Allocation")
    menu = ['Home', 'Hospitals', 'Chat']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Home':
        st.subheader("Home")
        st.write("Welcome to the Healthcare Resource Allocation Dashboard.")
        display_home_page()
    elif choice == 'Hospitals':
        display_hospitals()
    elif choice == 'Chat':
        display_chatbot()


# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import psycopg2
# import folium
# from streamlit_folium import folium_static

# # Database connection parameters
# POSTGRES_ADDRESS = 'localhost'
# POSTGRES_PORT = '5432'
# POSTGRES_USERNAME = 'myuser'
# POSTGRES_PASSWORD = 'mypassword'
# POSTGRES_DBNAME = 'mydatabase'

# # Function to create database connection
# def create_connection():
#     try:
#         conn = psycopg2.connect(
#             user=POSTGRES_USERNAME,
#             password=POSTGRES_PASSWORD,
#             host=POSTGRES_ADDRESS,
#             port=POSTGRES_PORT,
#             database=POSTGRES_DBNAME
#         )
#         return conn
#     except psycopg2.Error as e:
#         print(e)

# # Function to fetch master dataframe
# def fetch_master_df(conn): 
#     try:
#         cursor = conn.cursor()
#         cursor.execute('''
#         SELECT "Latitude", "Longitude", "Name", "Type", "Sector", "Open/Closed", "State" FROM hospital_mapping
#         ''')
#         return pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
#     except psycopg2.Error as e:
#         print(e)

# # Function to fetch values dataframe
# def fetch_hospital_values_df(conn): 
#     try:
#         cursor = conn.cursor()
#         cursor.execute('''
#         SELECT v."DataSetId", v."ReportingUnitCode", v."Value", h."Latitude", h."Longitude", h."Name", h."Type", h."Sector", h."Open/Closed", h."State"
#         FROM values v
#         JOIN hospital_mapping h ON v."ReportingUnitCode" = h."Code"
#         ''')
#         return pd.DataFrame(cursor.fetchall(), columns=['DataSetId', 'ReportingUnitCode', 'Value', 'Latitude', 'Longitude', 'Name', 'Type', 'Sector', 'Open/Closed', 'State'])
#     except psycopg2.Error as e:
#         print(e)

# # Create connection and fetch data
# conn = create_connection()
# master_df = fetch_master_df(conn)

# # Convert data types and drop NaN values
# master_df['Latitude'] = pd.to_numeric(master_df['Latitude'], errors='coerce')
# master_df['Longitude'] = pd.to_numeric(master_df['Longitude'], errors='coerce')
# master_df = master_df.dropna(subset=['Latitude', 'Longitude'])

# # Sidebar setup
# st.sidebar.markdown("### Select Visualization Type")
# select = st.sidebar.selectbox('Visualization type', ['Histogram', 'Pie Chart', 'Hospitals'], key='1')

# if not st.sidebar.checkbox('Hide', True, key='2'):
#     if select == 'Hospitals':
#         st.markdown("### Hospitals Data")
        
#         # Create Folium map at the center of Australia
#         hospital_map = folium.Map(location=[-25, 135], zoom_start=5)
        
#         # Add hospitals to the map
#         for index, row in master_df.iterrows():
#             folium.Marker(
#                 [row['Latitude'], row['Longitude']],
#                 popup=row['Name']
#             ).add_to(hospital_map)
        
#         # Display the map in Streamlit
#         folium_static(hospital_map)
        
#         # Histogram of Hospitals per State (assuming state_hospital_counts is calculated properly)
#         state_hospital_counts = master_df.groupby('State').size().reset_index(name='Number of Hospitals')
#         fig = px.bar(state_hospital_counts, x='State', y='Number of Hospitals', color='Number of Hospitals', height=500)
#         fig.update_layout(
#             xaxis_title='State',
#             yaxis_title='Number of Hospitals',
#             height=600, 
#             width=700,
#             title={'text': 'Number of Hospitals per State', 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yancyhor': 'top'},
#             font=dict(size=16, color="#000000"),
#             paper_bgcolor="#f8f9fa",
#             plot_bgcolor="#f8f9fa",
#             margin=dict(r=20, t=50, l=20, b=20)
#         )
#         st.plotly_chart(fig)
        
#     else:
#         st.markdown("### tbd")
#         # Assuming you have feedback_count DataFrame ready
#         # fig = px.pie(feedback_count, values='Feedbacks', names='Sentiment')
#         # st.plotly_chart(fig)
#         st.write("Pie chart placeholder")
