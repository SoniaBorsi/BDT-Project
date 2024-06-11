import requests
import dask.dataframe as dd

def get_hospitals_selected_id(MeasureCode, ReportedMeasureCode=None, ReportingStartDate=None):
    url = "https://myhospitalsapi.aihw.gov.au/api/v1/datasets/"
    headers = {
        'Authorization': 'Bearer YOUR_ACCESS_TOKEN',  
        'User-Agent': 'MyApp/1.0',
        'accept': 'text/csv'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open('selected_datasets.csv', 'w') as f:
            f.write(response.text)
        
        datasets = dd.read_csv("selected_datasets.csv")
        if ReportingStartDate is not None and ReportedMeasureCode is not None:
            filtered_datasets = datasets[
                (datasets['ReportedMeasureCode'] == ReportedMeasureCode) &
                (datasets['MeasureCode'] == MeasureCode) &
                (datasets['ReportingStartDate'] == ReportingStartDate)
            ]
        elif ReportedMeasureCode is not None:
            filtered_datasets = datasets[
                (datasets['ReportedMeasureCode'] == ReportedMeasureCode) &
                (datasets['MeasureCode'] == MeasureCode)
            ]
        else:
            filtered_datasets = datasets[
                (datasets["MeasureCode"] == MeasureCode)
            ]
        result = filtered_datasets.compute()
        dataset_ids = result['DataSetId']
        
        return dataset_ids
    else:
        print("Failed to fetch data. Status code:", response.status_code)
        return None