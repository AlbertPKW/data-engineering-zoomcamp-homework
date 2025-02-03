# Data Engineering Zoomcamp Module 2 Homework: Workflow Orchestration

## Question 1
Within the execution for Yellow Taxi data for the year 2020 and month 12: what is the uncompressed file size (i.e. the output file yellow_tripdata_2020-12.csv of the extract task)?

**Answer -> 128.3 MB**

```
id: 08_gcp_taxi_check
namespace: zoomcamp
description: |
  The CSV Data used in the course: https://github.com/DataTalksClub/nyc-tlc-data/releases

inputs:
  - id: taxi
    type: SELECT
    displayName: Select taxi type
    values: [yellow, green]
    defaults: green

  - id: year
    type: SELECT
    displayName: Select year
    values: ["2019", "2020"]
    defaults: "2019"
    allowCustomValue: true 

  - id: month
    type: SELECT
    displayName: Select month
    values: ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    defaults: "01"

variables:
  file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"
  gcs_file: "gs://{{kv('GCP_BUCKET_NAME')}}/{{vars.file}}"
  table: "{{kv('GCP_DATASET')}}.{{inputs.taxi}}_tripdata_{{inputs.year}}_{{inputs.month}}"
  data: "{{outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ inputs.year ~ '-' ~ inputs.month ~ '.csv']}}"

tasks:
  - id: set_label
    type: io.kestra.plugin.core.execution.Labels
    labels:
      file: "{{render(vars.file)}}"
      taxi: "{{inputs.taxi}}"

  - id: extract
    type: io.kestra.plugin.scripts.shell.Commands
    outputFiles:
      - "*.csv"
    taskRunner:
      type: io.kestra.plugin.core.runner.Process
    commands:
      - wget -qO- https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{{inputs.taxi}}/{{render(vars.file)}}.gz | gunzip > {{render(vars.file)}}

pluginDefaults:
  - type: io.kestra.plugin.gcp
    values:
      serviceAccount: "{{kv('GCP_CREDS')}}"
      projectId: "{{kv('GCP_PROJECT_ID')}}"
      location: "{{kv('GCP_LOCATION')}}"
      bucket: "{{kv('GCP_BUCKET_NAME')}}"
```

![Question 1 Workings](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/02-workflow-orchestration/images/Qns%201.jpg)

## Question 2
What is the rendered value of the variable file when the inputs taxi is set to green, year is set to 2020, and month is set to 04 during execution?

**Answer -> green_tripdata_2020-04.csv**

![Question 2 Workings 1](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/02-workflow-orchestration/images/Qns%202a.jpg)

![Question 2 Workings 2](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/02-workflow-orchestration/images/Qns%202b.jpg)

## Question 3
How many rows are there for the Yellow Taxi data for all CSV files in the year 2020?

**Answer -> 24,648,499**

![Question 3](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/02-workflow-orchestration/images/Qns%203.jpg)

## Question 4
How many rows are there for the Green Taxi data for all CSV files in the year 2020?

**Answer -> 1,734,051**

![Question 4](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/02-workflow-orchestration/images/Qns%204.jpg)

## Question 5
How many rows are there for the Yellow Taxi data for the March 2021 CSV file?

**Answer -> 1,925,152**

![Question 5](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/02-workflow-orchestration/images/Qns%205.jpg)

## Question 6
How would you configure the timezone to New York in a Schedule trigger?

**Answer -> Add a timezone property set to America/New_York in the Schedule trigger configuration**

![Question 6](https://github.com/AlbertPKW/data-engineering-zoomcamp-homework/blob/main/02-workflow-orchestration/images/Qns%206.jpg)
