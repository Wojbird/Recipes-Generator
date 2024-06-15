import re
import json


class Field:
    def __init__(self, name, type, nullable, isUnique, default, autoIncrement, startWith, incrementBy, isPrimaryKey, FKReferences):
        self.name = name
        self.type = type
        self.nullable = nullable
        self.isUnique = isUnique
        self.default = default
        self.isPrimaryKey = isPrimaryKey
        self.FKReferences = FKReferences
        self.startWith = startWith
        self.incrementBy = incrementBy
        self.autoIncrement = autoIncrement

    def set_type(self, type):
        self.type = type
    def set_nullable(self, nullable):
        self.nullable = nullable
    def set_unique(self, isUnique):
        self.isUnique = isUnique
    def set_primary(self, isPrimaryKey):
        self.isPrimaryKey = isPrimaryKey
    def set_FK(self, FKReferences):
        self.FKReferences = FKReferences

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
                isUnique = False
                default = None
                autoIncrement = False
                startWith = None
                incrementBy = None
                isPrimaryKey = False
                FK = None
                fieldqparsed = [x.lower() for x in fieldqparsed] #make all strings in list lowercase
                #print(fieldqparsed)
                if len(fieldqparsed) > 2:
                    if "null" in fieldqparsed:
                        isNullable = False
                    if "primary" in fieldqparsed:
                        isPrimaryKey = True
                        isNullable = False
                        isUnique = True
                    if "unique" in fieldqparsed:
                        isUnique = True
                    if "identity" in fieldqparsed:
                        autoIncrement = True
                        fieldqparsed = [s.replace('(', '') for s in fieldqparsed] # remove (
                        for v in fieldqparsed:  # remove ) and split last value
                            if ')' in v:
                                nfqp = [s.replace(')', '') for s in fieldqparsed]
                                last = nfqp[-1].split(' ')
                                nfqp = nfqp[:-1]
                                nfqp = nfqp + last
                                fieldqparsed = nfqp
                                break
                        print(fieldqparsed)
                        #handle (starts with x increment by y) sytnax
                        if "start" in fieldqparsed or "increment" in fieldqparsed:
                            if "start" in fieldqparsed:
                                startWith = fieldqparsed[fieldqparsed.index("start") + 2]
                            if "increment" in fieldqparsed:
                                incrementBy = fieldqparsed[fieldqparsed.index("increment") + 2]
                        else:
                            #handle (x, y) syntax
                            if fieldqparsed[fieldqparsed.index("identity") + 2] is not None:
                                fieldqparsed = [s.replace(',', '') for s in fieldqparsed]
                                startWith = fieldqparsed[fieldqparsed.index("identity") + 1]
                                incrementBy = fieldqparsed[fieldqparsed.index("identity") + 2]
                            else: raise RuntimeError("SQL syntax error")
                    elif "default" in fieldqparsed:
                        default = fieldqparsed[fieldqparsed.index("default") + 1] #get value after default
                        if default[0] == '\'' and default[-1] == '\'':
                            default = default[1:-1]  # remove '' from strings
                        #print(default)
                    #handle identity(x, y) case (no whitespace between identity and '(' symbol)
                    for val in fieldqparsed:
                        autoIncrement = True
                        if "identity(" in val:
                            identity = fieldqparsed[-1]
                            identity = identity.split('(')
                            identity = identity[-1]
                            identity = identity.split(',')
                            identity = [s.replace(')', '') for s in identity]
                            startWith = identity[0].strip()
                            incrementBy = identity[1].strip()
                            print(identity)
                fields.append(Field(fieldname, fieldtype, isNullable, isUnique, default, autoIncrement, startWith, incrementBy, isPrimaryKey, FK))
            else:
                if "primary" in fieldqparsed[0].lower() and "key" in fieldqparsed[1].lower():
                    primaryKeysField = fieldqparsed[2]
                    if primaryKeysField[0] == '(' and primaryKeysField[-1] == ')':
                        primaryKeysField = primaryKeysField[1:-1] # remove ( and )
                    else: raise RuntimeError("SQL syntax error")
                    primaryKeys = primaryKeysField.split(',')
                    for pk in primaryKeys:  #find field and set it to primary key
                        pk = pk.lstrip()
                        for field in fields:
                            if field.name == pk:
                                field.set_primary(True)
                                field.set_nullable(False)
                                field.set_unique(True)
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
                if "unique" in parsed[1].lower():
                    #print(parsed)
                    fieldName = parsed[2]
                    if fieldName[0] == '(' and fieldName[-1] == ')':
                        fieldName = fieldName[1:-1]  # remove ( and )
                    else:
                        raise RuntimeError("SQL syntax error")
                    for table in tables:
                        if table.name == tableName:
                            for field in table.fields:
                                if field.name == fieldName:
                                    field.set_unique(True)
                                    break
                            break
                elif "default" in parsed[1].lower():
                    #print(parsed)
                    default = parsed[2]
                    if default[0] == '\'' and default[-1] == '\'':
                        default = default[1:-1]  # remove '' from strings
                    parsed = parsed[3]
                    parsed = parsed.split(' ')
                    if "for" not in parsed[0].lower(): raise RuntimeError("SQL syntax error")
                    fieldName = parsed[1]
                    for table in tables:
                        if table.name == tableName:
                            for field in table.fields:
                                if field.name == fieldName:
                                    field.default = default
                                    break
                            break
                elif "foreign" in parsed[1].lower() and "key" in parsed[2].lower():
                    parsed = parsed[3]
                    parsed = parsed.split(' ')
                    fieldName = parsed[0]
                    if fieldName[0] == '(' and fieldName[-1] == ')':
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
            elif "alter" in parsed[0].lower() and "column" in parsed[1].lower():
                parsed = parsed[2]
                parsed = parsed.split(' ', 3)
                #print(parsed)
                if "not" in parsed[2].lower() and "null" in parsed[3].lower():
                    fieldName = parsed[0]
                    datatype = parsed[1]
                    for table in tables:
                        if table.name == tableName:
                            for field in table.fields:
                                if field.name == fieldName:
                                    field.set_type(datatype)
                                    field.set_nullable(False)
                                    break
                            break


dbconfig = {
    "Recipes create number": 2,
    "Ingredients create number": 15,
    "Other tables create number": 10,
    "Tables":
        [
            {
                "Table name": table.name,
                "Fields":
                    [
                        {

                            "Field name": field.name,
                            "Type": field.type,
                            "Nullable": field.nullable,
                            "Unique": field.isUnique,
                            "Default": field.default,
                            "Auto increment": field.auto_increment,
                            "Start with": field.start_with,
                            "Increment by": field.increment_by,
                            "Is PK": field.isPrimaryKey,
                            "FK References": field.FKReferences,
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
        if field.FKReferences is not None:
            msg += " FK References " + field.FKReferences[0] + " in " + field.FKReferences[1]
        if field.isPrimaryKey:
            msg += " PK"
        else:
            if not field.nullable:
                msg += " not null"
            if field.isUnique:
                msg += " unique"
            if field.default is not None:
                msg += " default " + field.default
        if field.autoIncrement:
            msg += " Auto Increment"
        if field.startWith is not None:
            msg += " start with " + field.startWith
        if field.incrementBy is not None:
            msg += " increment by " + field.incrementBy
        print(msg)
    print()