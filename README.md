# dbt-LineageX

A Column Level Lineage Graph for dbt

Have you ever wondered what is the column level relationship between the dbt models? 
Worry not, this tool is intended to help you by creating an interactive graph on a webpage to 
explore the column level lineage among your models(Currently only supports Postgres, 
other connection types are under development)! This library uses the same core as the [LineageX](https://github.com/sfu-db/lineagex).

Here is a [live demo](https://zshandy.github.io/lineagex-demo/) with the [mimic-iv concepts_postgres](https://github.com/MIT-LCP/mimic-code/tree/main/mimic-iv/concepts_postgres) files([navigation instructions](https://sfu-db.github.io/lineagex/output.html#how-to-navigate-the-webpage))

## Requirements
`dbt version >= 1.0.0`

## Installation
New to dbt packages? Read more about them [here](https://docs.getdbt.com/docs/building-a-dbt-project/package-management/).
1. Include this package in your `packages.yml` file.
```
packages:
  - git: "https://github.com/sfu-db/dbt-lineagex.git"
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

## What does it output
The output would be a output.json and a index.html file in the folder. Start a local http server, and you would be able to see the interactive graph. Sample command: `php -S localhost:8000`
<img src="https://raw.githubusercontent.com/sfu-db/lineagex/main/docs/example.gif"/>
Check out more detailed navigation instructions [here](https://sfu-db.github.io/lineagex/output.html#how-to-navigate-the-webpage).

## FAQ
- `"not init data"` in the webpage:
Possibly due to the content of the JSON in the index.html, please check if it is in valid JSON format, and that all keys are in string format.
- `ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt\r' while running run.sh`:
It is due to the file format, run this in command line
``` bash
sudo apt-get update
sudo apt-get install dos2unix
dos2unix run.sh
```