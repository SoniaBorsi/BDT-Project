import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import folium
from streamlit_folium import folium_static
from streamlit_chat import message
import streamlit as st

POSTGRES_ADDRESS = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'myuser'
POSTGRES_PASSWORD = 'mypassword'
POSTGRES_DBNAME = 'mydatabase'

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


def fetch_values():
    """Fetch data from the database."""
    try:
        conn = create_connection()  # Establish database connection

        # SQL query to fetch data
        sql_query = '''
            SELECT 
                hm."Name" AS "HospitalName", 
                hm."Type" AS "HospitalType", 
                hm."State" AS "State", 
                v."DataSetId", 
                ds."DatasetName", 
                COUNT(v."Value") AS "Occurrences" 
            FROM 
                values v 
            JOIN 
                hospital_mapping hm ON v."ReportingUnitCode" = hm."Code" 
            JOIN 
                datasets ds ON v."DataSetId"::INTEGER = ds."DataSetId" 
            GROUP BY 
                hm."Name", 
                hm."Type", 
                hm."State", 
                v."DataSetId", 
                ds."DatasetName"

        '''

        # Execute SQL query and fetch data into a DataFrame
        df = pd.read_sql(sql_query, conn)

        # Close database connection
        conn.close()

        return df
    except psycopg2.Error as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()


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

# home page
def display_home_page():
    st.title("Welcome to Healthcare Resource Allocation")
    st.write("""
        This application is designed to facilitate healthcare resource allocation through data visualization and a chatbot interface.
        
        Use the buttons below to navigate to different sections:
    """)
    
    if st.button('Measures'):
        st.session_state['page'] = 'measures'
    if st.button('Hospitals'):
        st.session_state['page'] = 'hospitals'
    if st.button('Chat'):
        st.session_state['page'] = 'chat'
    if st.button('Predictions'):
        st.session_state['page'] = 'predictions'
    
    st.markdown("### General Plots")
    # Example plot
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [10, 20, 30, 40, 50]
    })
    fig = px.line(df, x='x', y='y', title='Example Plot')
    st.plotly_chart(fig)


#measurements 
    
def display_measures():
    """Display measures fetched from the database."""
    st.title("Measures")
    if st.button("Return to Home"):
        st.session_state['page'] = 'home'
    
    df = fetch_values()
    
    if not df.empty:
        fig1 = px.bar(df, x='Occurrences', y='HospitalName', orientation='h',
                     title='Occurrences by Hospital Name', labels={'HospitalName': 'Hospital Name'})
        st.plotly_chart(fig1)

        fig2 = px.bar(df, x='Occurrences', y='DatasetName', orientation='h',
                     title='Occurrences by Dataset Name', labels={'DatasetName': 'Dataset Name'})
        st.plotly_chart(fig2)

    else:
        st.write("No measures found.")

    

# hospitals 
        
def display_hospitals():
    """Display hospitals on a map, as a pie chart, and in a table."""
    st.title("Hospitals")

    if st.button("Return to Home"):
        st.session_state['page'] = 'home'
    
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

    #pie chart for the total private and public hospitals in Australia
    total_private_hospitals = private_hospitals['Number of Hospitals'].sum() if not private_hospitals.empty else 0
    total_public_hospitals = public_hospitals['Number of Hospitals'].sum() if not public_hospitals.empty else 0

    fig_pie = px.pie(names=['Private', 'Public'], values=[total_private_hospitals, total_public_hospitals], 
                 title="Total Private and Public Hospitals in Australia")
    st.plotly_chart(fig_pie)

    #histogram for the number of private and public hospitals per state
    fig_hist = px.bar(state_counts, x='State', y=['Number of Hospitals_private', 'Number of Hospitals_public'], barmode='group', 
                 title="Number of Private and Public Hospitals per State", labels={'value': 'Number of Hospitals', 'variable': 'Hospital Type'})
    fig_hist.update_layout(xaxis_title="State", yaxis_title="Count")
    st.plotly_chart(fig_hist)

    # hospitals based on selected state, open/closed status, and sector
    selected_state = st.selectbox("Select State", df['State'].unique())
    selected_status = st.selectbox("Select Open/Closed", df['Open/Closed'].unique())
    selected_sector = st.selectbox("Select Sector", df['Sector'].unique())
    
    st.markdown(f"### Hospitals in {selected_state} - {selected_status} - {selected_sector}")
    
    filtered_df = df[(df['State'] == selected_state) & (df['Open/Closed'] == selected_status) & (df['Sector'] == selected_sector)]
    
    if not filtered_df.empty:
        st.table(filtered_df)
    else:
        st.write("No hospitals found with the selected criteria.")
    

#predictions 

def display_predictions():
    if st.button("Return to Home"):
        st.session_state['page'] = 'home'     


#chat
def display_chatbot():
    """Display a chatbot interface."""
    st.title("Chat with our Healthcare Bot")
    user_input = st.text_input("Message", key="chat_input")
    if st.button("Send"):
        process_user_message(user_input.strip().lower())
    if st.button("Return to Home"):
        st.session_state['page'] = 'home'

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
    if st.button("Return to Home"):
        st.session_state['page'] = 'home'

# if __name__ == '__main__':
#     st.sidebar.title("Healthcare Resource Allocation")
#     menu = ['Home', 'Measures', 'Hospitals', 'Chat', 'Predictions']
#     choice = st.sidebar.selectbox("Menu", menu)

#     if choice == 'Home':
#         st.subheader("Home")
#         st.write("Welcome to the Healthcare Resource Allocation Dashboard.")
#         display_home_page()
#     elif choice == 'Measures':
#         display_measures()
#     elif choice == 'Hospitals':
#         display_hospitals()
#     elif choice == 'Predictions':
#         display_predictions()
#     elif choice == 'Chat':
#         display_chatbot()


def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'
        
    if st.session_state['page'] == 'home':
        display_home_page()
    elif st.session_state['page'] == 'measures':
        display_measures()
    elif st.session_state['page'] == 'hospitals':
        display_hospitals()
    elif st.session_state['page'] == 'predictions':
        display_predictions()
    elif st.session_state['page'] == 'chat':
        display_chatbot()

if __name__ == '__main__':
    main()