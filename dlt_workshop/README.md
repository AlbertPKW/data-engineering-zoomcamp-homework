# Workshop "Data Ingestion with dlt": Homework

## Question 1
Provide the version you see in the output.

**Answer -> 1.6.1**

![Question 1 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/dlt_workshop/images/Qns%201.jpg)

## Question 2
How many tables were created?

**Answer -> 4**

```
import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator

# your code is here
@dlt.resource(name="rides")
def ny_taxi():
    client = RESTClient(
        base_url="https://us-central1-dlthub-analytics.cloudfunctions.net",
        paginator=PageNumberPaginator(
            base_page=1,
            total_path=None
        )
    )

    for page in client.paginate("data_engineering_zoomcamp_api"):    # <--- API endpoint for retrieving taxi ride data
        yield page   # <--- yield data to manage memory


pipeline = dlt.pipeline(
    pipeline_name="ny_taxi_pipeline",
    destination="duckdb",
    dataset_name="ny_taxi_data"
)
```

![Question 2 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/dlt_workshop/images/Qns%202B.jpg)

## Question 3
What is the total number of records extracted?

**Answer -> 10000**

![Question 3 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/dlt_workshop/images/Qns%203.jpg)

## Question 3
What is the average trip duration?

**Answer -> 12.3049**

![Question 4 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/dlt_workshop/images/Qns%204.jpg)



