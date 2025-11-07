# Spring-Configurator-Editor
This python project is going to replace the specific Spring config with provided one 

## Steps that Spring Configurator do before changing all config and boostrap yml files

    - Create folders for all Java services group [this one is handled in some Pandas or Array]
    - Checkout all Java services ( all java services name list will be provided into a separate list ), there will be two Array variables one with the Java services names and another simple variable will handle the branch name. We need to separate and checkout all of the Java services into the specific folders from step 1.
    - Create a new branch
    - First replace in the Config Java services group boostrap and the configuration settings (azure/oracle/postgres/snowflake connections settings), and after that the Config client server group
    - Compare pom.xml with the specific branch, add necessary changes
    - Log everything
    - Run GitHub pipe and express all logs into a separate file
    - Create Menu and try to assemble all steps to work the Spring Configurator


## How to run the Project

### Install with Virtual Environment

python -m venv venv

### On windows
```bash
venv\Scripts\activate
```
### On Mac
```bash
source venv/bin/activate
```


### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the main program
```bash
python src/main.py
```

### Run tests
```bash
pytest
```