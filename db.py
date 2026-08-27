import yaml

# Custom Decorator
def run_once(func):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

@run_once
def initialize_schema(cursor):
    with open('schema.sql', 'r', encoding='utf-8') as file:
        sql_script = file.read()

    cursor.execute(sql_script)

def load_class(cursor, yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    classNames = data['names']

    if isinstance(classNames, dict):
        classNames = classNames.values()

    for classID, className in enumerate(classNames):
        cursor.execute(
            "{CALL dbo.InsertClass(?,?)}",
            (classID, className)
        )

def insert_dataset(cursor):
    print("")