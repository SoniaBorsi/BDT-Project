import logging
import pandas as pd
import pika
import time
import requests
from sqlalchemy import create_engine, text

def map_hospitals():
    print('Fetching Hospitals data...')
    
    url = "https://myhospitalsapi.aihw.gov.au/api/v1/reporting-units-downloads/mappings"
    headers = {
        'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
        'User-Agent': 'MyApp/1.0',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    filename = 'hospital_mapping.xlsx'

    with open(filename, 'wb') as file:
        file.write(response.content)

    df = pd.read_excel(filename, engine='openpyxl', skiprows=3)
    
    engine = create_engine('postgresql+psycopg2://user:password@postgres:5432/mydatabase')
    
    with engine.connect() as conn:
        try:
            trans = conn.begin()
            df.to_sql('hospitals', engine, if_exists='replace', index=False)
            print("Hospital mapping inserted successfully into the PostgreSQL database")
            print("Enabling PostGIS extension...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.execute(text("ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);"))
            conn.execute(text("""
                UPDATE hospitals
                SET geom = ST_SetSRID(ST_MakePoint("Longitude", "Latitude"), 4326);
            """))
            trans.commit()
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'hospitals';
            """))
        except Exception as e:
            print(f"An error occurred: {e}")
            trans.rollback()


def get_ids(file_path):
    datasets = pd.read_csv(file_path)
    hospitals_series_id = datasets['DataSetId'].tolist()
    return hospitals_series_id

def insert_into_postgresql(data_frame, table_name):
    url = "jdbc:postgresql://postgres:5432/mydatabase"
    properties = {
        "user": "user",
        "password": "password",
        "driver": "org.postgresql.Driver"
    }

    try:
        data_frame.write.jdbc(url=url, table=table_name, mode="append", properties=properties)
    except Exception as e:
        logging.error(f"Failed to insert data into PostgreSQL: {e}")

def send_to_rabbitmq(csv_files):
    connection_attempts = 0
    max_attempts = 5
    while connection_attempts < max_attempts:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            channel = connection.channel()
            if len(csv_files) > 1:
                channel.queue_declare(queue='values_queue')
                for csv_file in csv_files:
                    with open(csv_file, 'r') as file:
                        csv_data = file.read()
                        channel.basic_publish(exchange='', routing_key='values_queue', body=csv_data)
        
            else:
                channel.queue_declare(queue='datasets_measurements_reportedmeasurements_queue')
                for csv_file in csv_files:
                    with open(csv_file, 'r') as file:
                        csv_data = file.read()
                        channel.basic_publish(exchange='', routing_key='datasets_measurements_reportedmeasurements_queue', body=csv_data)

                logging.info("CSV files sent to RabbitMQ.")
            connection.close()
            return
        except Exception as e:
            logging.error(f"Failed to send CSV files to RabbitMQ: {e}")
            connection_attempts += 1
            time.sleep(5)
    logging.error("Exceeded maximum attempts to connect to RabbitMQ.")

def consume_from_rabbitmq(spark_session, queue_name, callback_function):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=lambda ch, method, properties, body: callback_function(spark_session, ch, method, properties, body))
        logging.info(f' [*] Waiting for messages on queue "{queue_name}". To exit press CTRL+C')
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info('Interrupted by user, shutting down...')
    except Exception as e:
        logging.error(f"Failed to consume messages from RabbitMQ: {e}")
