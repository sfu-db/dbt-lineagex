# dbt-LineageX

A Column Level Lineage Graph for dbt

Have you ever wondered what is the column level relationship between the dbt models? 
Worry not, this tool is intended to help you by creating an interactive graph on a webpage to 
explore the column level lineage among your models(Currently only supports Postgres, 
other connection types are under development)!

## Requirements
`dbt version >= 1.0.0`

## Installation
New to dbt packages? Read more about them [here](https://docs.getdbt.com/docs/building-a-dbt-project/package-management/).
1. Include this package in your `packages.yml` file.
```
packages:
  - git: "https://github.com/zshandy/dbt-lineagex.git"
```

2. Run `dbt deps` to install the package.

## Quickstart
If you don't have your dbt already ran yet, change directory to your main folder and run:
`dbt run`

After you've finished running your dbt project, change directory to the "/dbt_packages/lineagex" folder and run:
> **Note** Recommended to have a virtual environment setup for running the Python scripts, as it could fight 
> with other dependencies(Currently it is more like a Python project, but will try to make changes to it so 
> that only changes to the dbt_project.yml needs to be made for running)
```
./run.sh 
```
Or if you want to run the commands separately, they are:
``` python
- pip install -r requirements.txt
- python main.py
```

This would create the index.html in the scripts folder, and just start a http server in the folder and you get to see the graph
sample command: `php -S localhost:8000`

## How to use

- Start by clicking the star on the right(search) and input a model name that you want to start with.
- It should show a table on the canvas with table names and its columns, by clicking the "explore" button on the top right, it will show all the downstream and upstream tables that are related to the columns.
- Hovering over a column will highlight its downstream and upstream columns as well.
- You can navigate through the canvas by clicking "explore" on other tables.

## FAQ
- `"not init data"` in the webpage:
Possibly due to the content of the JSON in the index.html, please check if it is in valid JSON format, and that all keys are in string format.
