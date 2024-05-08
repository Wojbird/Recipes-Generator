import re
import json


class Field:
    def __init__(self, name, type):
        self.name = name
        self.type = type


class Table:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


with open('input.txt', 'r') as file:
    lines = file.readlines()

tables = []

for line in lines:
    parsed = line.split(' ', 2)  #get first two words of query
    if "create" in parsed[0].lower():
        parsed = parsed[2]  #get the rest of query without "create table"
        parsed = parsed.split(' ', 1)  #split off table name
        TableName = parsed[0]
        #print(TableName)
        parsed = parsed[1]  #get rest of query without table name
        parsed = parsed[1:-1]  #remove ( and )
        #print(parsed)
        fields = []
        fieldquery = re.split(r',(?! [0-9a-zA-Z]+[\),])', parsed)  #split by comma, except when it's in brackets
        for f in fieldquery:
            f = f.lstrip()
            #print(f)
            fieldqparsed = re.split(r' (?! ?[0-9a-zA-Z]+[\),])', f)  #split by whitespace except when it's in brackets
            #print(fieldqparsed)
            if "primary" not in fieldqparsed[
                0].lower():  #primary key part of query is not a field so do nothing when encountered
                fieldname = fieldqparsed[0]
                fieldtype = fieldqparsed[1]
                fields.append(Field(fieldname, fieldtype))

        #print(fieldquery)
        tables.append(Table(TableName, fields))

dbconfig = [
    {
        table.name:
            [
                {
                    field.name:
                        {
                            "Field type": field.type,
                            "Data type": "None",
                            "Max length": "None",
                            "Min length": "None",
                            "Excluded": "None",
                            "Must have": "None"
                        }
                } for field in table.fields
            ]
    } for table in tables
]
json_string = json.dumps(dbconfig)
with open('dbconfig.json', 'w') as f:
    json.dump(dbconfig, f)

for table in tables:
    print(table.name)
    for field in table.fields:
        print(field.name + ": " + field.type)
    print()
