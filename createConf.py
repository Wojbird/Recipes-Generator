import re
import json


class Field:
    def __init__(self, name, type, nullable, isPrimaryKey, FKRefrences):
        self.name = name
        self.type = type
        self.nullable = nullable
        self.isPrimaryKey = isPrimaryKey
        self.FKRefrences = FKRefrences

    def set_primary(self, isPrimaryKey):
        self.isPrimaryKey = isPrimaryKey

    def set_FK(self, FKRefrences):
        self.FKRefrences = FKRefrences

class Table:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


with open('input.txt', 'r') as file:
    lines = file.readlines()

tables = []

for line in lines:
    parsed = line.split(' ', 3)  #get first two words of query
    #print(parsed)
    if "table" not in parsed[1].lower() or parsed[2].lower() in ["as", "if", "using"]:
        raise RuntimeError("Wrong input file syntax, generator accepts only \"CREATE TABLE name (...\" or \"ALTER TABLE name ...\"")
    if "create" in parsed[0].lower():
        TableName = parsed[2]
        parsed = parsed[3]  # get the rest of query without "create table tableName"
        #print(TableName)
        if parsed[0] == '(' or parsed[-3:] == ");\n":
            parsed = parsed[1:-3]  # remove ( and );\n
        elif parsed[0] == '(' or parsed[-2:] == ");":
            parsed = parsed[1:-2]  # remove ( and );
        else: raise RuntimeError("SQL syntax error")
        fields = []
        fieldquery = re.split(r',(?! [0-9a-zA-Z]+[),])', parsed)  # split by comma, except when it's in brackets
        #print(fieldquery)
        for f in fieldquery:
            f = f.lstrip()
            #print(f)
            fieldqparsed = re.split(r' (?! ?[0-9a-zA-Z]+[),])', f)  # split by whitespace except when it's in brackets
            #print(fieldqparsed)
            if "primary" not in fieldqparsed[0].lower():
                fieldname = fieldqparsed[0]
                fieldtype = fieldqparsed[1]
                isNullable = True
                isPrimaryKey = False
                FK = None
                if len(fieldqparsed) > 2:
                    if "not" in fieldqparsed[2].lower() and "null" in fieldqparsed[3].lower():
                        isNullable = False
                    elif "primary" in fieldqparsed[2].lower() and "key" in fieldqparsed[3].lower():
                        isPrimaryKey = True
                fields.append(Field(fieldname, fieldtype, isNullable, isPrimaryKey, FK))
            else:
                if "primary" in fieldqparsed[0].lower() and "key" in fieldqparsed[1].lower():
                    primaryKeysField = fieldqparsed[2]
                    if primaryKeysField[0] == '(' and primaryKeysField[-1:] == ')':
                        primaryKeysField = primaryKeysField[1:-1] # remove ( and )
                    else: raise RuntimeError("SQL syntax error")
                    primaryKeys = primaryKeysField.split(',')
                    for pk in primaryKeys:
                        pk = pk.lstrip()
                        for field in fields:
                            if field.name == pk:
                                field.set_primary(True)
                                break
        tables.append(Table(TableName, fields))
    else:
        if "alter" in parsed[0].lower():
            tableName = parsed[2]
            parsed = parsed[3]
            parsed = parsed.split(' ', 2)
            if "add" in parsed[0].lower() and "constraint" in parsed[1].lower():
                parsed = parsed[2]
                parsed = parsed.split(' ', 3)
                if "foreign" in parsed[1].lower() and "key" in parsed[2].lower():
                    parsed = parsed[3]
                    parsed = parsed.split(' ')
                    fieldName = parsed[0]
                    if fieldName[0] == '(' and fieldName[-1:] == ')':
                        fieldName = fieldName[1:-1]  # remove ( and )
                    else: raise RuntimeError("SQL syntax error")
                    if "references" not in parsed[1].lower():
                        raise RuntimeError("SQL syntax error")
                    ReferenceTableName = parsed[2]
                    ReferenceFieldName = parsed[3]
                    if ReferenceFieldName[0] == '(' and ReferenceFieldName[-3:] == ");\n":
                        ReferenceFieldName = ReferenceFieldName[1:-3]
                    elif ReferenceFieldName[0] == '(' and ReferenceFieldName[-2:] == ");":
                        ReferenceFieldName = ReferenceFieldName[1:-2]
                    else: raise RuntimeError("SQL syntax error")
                    ReferenceField = None
                    for table in tables:
                        if table.name == ReferenceTableName:
                            for field in table.fields:
                                if field.name == ReferenceFieldName:
                                    ReferenceField = field
                                    break
                            break
                    if ReferenceField is None:
                        continue
                    for table in tables:
                        if table.name == tableName:
                            for field in table.fields:
                                if field.name == fieldName:
                                    field.set_FK([ReferenceFieldName, ReferenceTableName])
                                    field.set_primary(False)
                                    break
                            break


dbconfig = {
    "Tables":
        [
            {
                "Table name": table.name,
                "Fields":
                    [
                        {

                            "Field name": field.name,
                            "Data type":
                                field.type + " PK" if field.isPrimaryKey else
                                field.type + " FK References " + field.FKRefrences[0] + " in " + field.FKRefrences[1] if field.isPrimaryKey else
                                field.type + " not null" if not field.nullable else
                                field.type,
                            "Validation (regex/code)": "None",
                            "Max length": "None",
                            "Min length": "None",
                            "Excluded": "None",
                            "Must have": "None"

                        } for field in table.fields
                    ]
            } for table in tables
        ]
}

json_string = json.dumps(dbconfig)
with open('dbconfig.json', 'w') as f:
    json.dump(dbconfig, f)

for table in tables:
    print(table.name)
    for field in table.fields:
        msg = field.name + ": " + field.type
        if field.isPrimaryKey:
            msg += " PK"
        elif field.FKRefrences is not None:
            msg += " FK References " + field.FKRefrences[0] + " in " + field.FKRefrences[1]
        elif not field.nullable:
            msg += " not null"
        print(msg)
    print()
