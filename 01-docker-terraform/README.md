# Data Engineering Zoomcamp Module 1 Homework: Docker & SQL

## Question 1. Understanding docker first run
Run docker with the python:3.12.8 image in an interactive mode, use the entrypoint bash.

What's the version of pip in the image?

**Answer -> 24.3.1**
```
docker run -it --entrypoint=bash python:3.12.8
pip --version
```

![Question 1 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/01-docker-terraform/Images/Question%201.jpg)


## Question 2. Understanding Docker networking and docker-compose
Given the following docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database?

```
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

**Answer -> db:5432**

![Question 2 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/01-docker-terraform/Images/Question%202.jpg)


## Question 3. Trip Segmentation Count

During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, respectively, happened:

1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles

**Answer -> 104,838; 199,013; 109,645; 27,688; 35,202**

```
SELECT 
	COUNT(CASE WHEN trip_distance <= 1 THEN "PULocationID" ELSE NULL END) AS "Up to 1 mile",
	COUNT(CASE WHEN trip_distance > 1 AND trip_distance <= 3 THEN "PULocationID" ELSE NULL END) AS "1 to 3 miles",
	COUNT(CASE WHEN trip_distance > 3 AND trip_distance <= 7 THEN "PULocationID" ELSE NULL END) AS "3 to 7 miles",
	COUNT(CASE WHEN trip_distance > 7 AND trip_distance <= 10 THEN "PULocationID" ELSE NULL END) AS "7 to 10 miles",
	COUNT(CASE WHEN trip_distance > 10 THEN "PULocationID" ELSE NULL END) AS "Over 10 miles"
FROM green_taxi_trips
```

![Question 3 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/01-docker-terraform/Images/Question%203%20updated.jpg)


## Question 4. Longest trip for each day
Which was the pick up day with the longest trip distance? Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance.

**Answer -> 2019-10-31**

```
SELECT 
	CAST(lpep_pickup_datetime AS DATE) AS pickup_day, 
	trip_distance
FROM green_taxi_trips
WHERE trip_distance = (
	SELECT MAX(trip_distance)
	FROM green_taxi_trips
)
```

![Question 4 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/01-docker-terraform/Images/Question%204.jpg)


## Question 5. Three biggest pickup zones
Which were the top pickup locations with over 13,000 in total_amount (across all trips) for 2019-10-18?

Consider only lpep_pickup_datetime when filtering by date.

**Answer -> East Harlem North, East Harlem South, Morningside Heights**

```
SELECT z."Zone", SUM(total_amount) AS "Total Amount By Zone"
FROM green_taxi_trips t
JOIN zones z
ON t."PULocationID" = z."LocationID"
WHERE CAST(lpep_pickup_datetime AS DATE) = '2019-10-18'
GROUP BY z."Zone"
HAVING SUM(total_amount) > 13000
ORDER BY SUM(total_amount) DESC
```

![Question 5 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/01-docker-terraform/Images/Question%205.jpg)


## Question 6. Largest tip
For the passengers picked up in Ocrober 2019 in the zone name "East Harlem North" which was the drop off zone that had the largest tip?

Note: it's tip , not trip

We need the name of the zone, not the ID.

**Answer -> JFK Airport**

```
SELECT
	TO_CHAR(lpep_pickup_datetime, 'YYYY-MM') AS "Year_Month",
	z."Zone" AS "Pickup_Zone",
	zn."Zone" AS "Dropoff_Zone",
	tip_amount
FROM green_taxi_trips t
JOIN zones z
ON t."PULocationID" = z."LocationID"
JOIN zones zn
ON t."DOLocationID" = zn."LocationID"
WHERE TO_CHAR(lpep_pickup_datetime, 'YYYY-MM') = '2019-10'
AND z."Zone" = 'East Harlem North'
ORDER BY tip_amount DESC
LIMIT 1
```

![Question 6 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/01-docker-terraform/Images/Question%206.jpg)


## Question 7. Terraform Workflow
Which of the following sequences, respectively, describes the workflow for:

- Downloading the provider plugins and setting up backend,
- Generating proposed changes and auto-executing the plan
- Remove all resources managed by terraform

**Answer -> terraform init, terraform apply -auto-approve, terraform destroy**

```
# Download the provider plugins and setting up backend
terraform init

# Generate proposed changes and auto-executing the plan
terraform apply -auto-approve

# Remove all resources managed by terraform
terraform destroy
```
