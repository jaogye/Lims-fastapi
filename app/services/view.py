"""
View service module for master data management.

This module provides a flexible view-based system for managing master data tables
through Excel import/export. It defines table schemas, validation rules, foreign key
relationships, and handles complex denormalized columns. Migrated from MATLAB
master data management system with enhanced validation and error handling.

The view system supports:
- Dynamic table definitions with column metadata
- Foreign key validation and resolution
- Denormalized columns (computed from other tables)
- Custom validators for interval and enumeration fields
- Unique key constraint checking
- Insert, Update, and Delete operations via Excel
"""

import pandas as pd
from sqlalchemy import text
import math
import numpy as np
from datetime import datetime
import re

def convert_numpy_types(obj):
    """
    Convert numpy types to native Python types for JSON serialization.

    Handles numpy integers, floats, and other numpy scalars for proper
    JSON encoding when returning data via API endpoints.

    Args:
        obj: Object to convert (can be numpy type, dict, list, or native type).

    Returns:
        Converted object with native Python types.
    """
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    return obj


# This function build the query of the view_name based on the view definitions
def buildQuery(db, view_name):
    additional_cols = getDnormColumns(db, view_name)
    col_names = ['action']  # Start with 'action' column
    query = "SELECT ' ' Action "
    From = view[view_name]['table']
    where = ""
    #table_aliases = {}  # Track table aliases to handle multiple references to the same table
    #table_counts = {}   # Count occurrences of each table

    if 'filter' in view[view_name]:
       for col, value in view[view_name]['filter'].items():
            if type(value) is str:
               value = "'" + value + "'"
            where = where + col + "=" + value + " AND "

    for label, value in view[view_name]['cols'].items():
        column = label
        col_names.append(column)
        if 'column' in value:
            column = value['column']
        if 'fk' in value: # if the column is FK
            table = value['fk']
            colFk = value['column']
            # Create alias based on the label to make it more meaningful
            alias = f"{table}_{label}"
            #table_aliases[colFk] = alias
            From =  From + "," + table + " " + alias
            column = alias + ".name "
            where = where + view[view_name]['table'] + "." + colFk + " = " + alias + ".id AND "

        query = query + ", " + column + " " + label
    
    for label, value in additional_cols:
        column = value['column']
        if label.lower() in ['as', 'in']: # If label crashes with a reserved word in sql
           label = label + '1'
        col_names.append(label)
        query = query + ", " + column + " " + label
    
    if where != "":
       where = where[0:-4]
    query = query + ", "+ view[view_name]['table'] + ".id "
    col_names.append('id')  # Add 'id' to match the query
    query = query + " FROM " + From
    if where != "":
       query = query + " WHERE " + where
    return query, col_names



def isNull(value):
    if value is None:
       return True
    # Check if the value is exactly an empty string
    if isinstance(value, str) and value.strip() == "":
        return True
    # Check if the value is a number and is NaN
    elif isinstance(value, (int, float)) and math.isnan(float(value)):
        return True
    # In all other cases, return False
    return False



# Define the function to check foreign key constraint
def checkFK0(db, query, parameters):
    r = db.execute(text(query), params= parameters)
    T = list(r)
    if len(T)>0:
        return int(T[0][0])
    else:
        return 0

# Define the function to check foreign key constraint
def checkFK(db, query, **kwargs):
    r = db.execute(text(query), params= kwargs)
    T = list(r)
    if len(T)>0:
        return int(T[0][0])
    else:
        return 0


# This function updates the detail of specification in dspec table based on
# the intervals saved in spec for a given id (idspec)
def updatedSpec(db, id, row, cols):
    sql = "DELETE FROM dspec WHERE spec_id=:id"
    db.execute(text(sql), {'id':id} )
    db.commit()
    for col in cols:
        min_val = row['min_'+col[0].strip().lower()]
        if col[1]['typevar'] == 'I':
            max_val = row['max_'+col[0].strip().lower()]
        else:
            max_val = None
        idvariable = col[1]['id']  
        if not min_val is None or not max_val is None:                            
           sql = "INSERT INTO dSpec(spec_id, variable_id, min_value, max_value) VALUES( :p1, :p2, :p3, :p4) ; "
           db.execute(text(sql), {'p1':id, 'p2':idvariable, 'p3':min_val, 'p4':max_val}    )
    db.commit()



# This function updates the detail of specification in dsamplematrix table based on
# the boolean selections saved in spec for a given id (idspec)
def updatedSampleMatrix(db, id, row, cols):
    sql = "DELETE FROM dsamplematrix WHERE samplematrix_id=:id"
    db.execute(text(sql), {'id':id} )
    db.commit()
    for col in cols:
        min_val = row[col[0].strip().lower()]
        idvariable = col[1]['id']  
        if not min_val is None:                            
           sql = "INSERT INTO dsamplematrix(samplematrix_id, variable_id) VALUES( :p1, :p2) ; "
           db.execute(text(sql), {'p1':id, 'p2':idvariable}    )
    db.commit()



#\d*-\d*|
# Validates the format of the interval for variables in CustomerList and GenSpec
def check_interval(label, ss):
    
    #print('label ', label, 'ss ', ss, 'type(ss) ', type(ss) )
    # Pattern to match the specified formats
    pattern = r'^(\d*\.?\d*-\d*\.?\d*|-\d*\.\d*|\d*\.\d*-)$' 
    global msg
    ss = ss.strip()
    msg = ""
    if ss is None or (type(ss) is str and len(ss) == 0 ):
        return msg
    # Using re.match to check if the string matches the pattern
    if not re.match(pattern, ss):
        msg = f"Column {label}. Interval {ss} of has no correct format"
        return msg    
    ll = ss.split('-') 
    if len(ll[0])>0 and len(ll[1])>0 and float(ll[0] ) > float(ll[1]):
        msg = f"Column {label}. The lower limit {ll[0]} is higher than the upper one {ll[1]}"
        return msg
    return msg, ll 


def check_customerparam(row):    
    coa = row['coa']    
    coc = row['coc']
    onedecimal = row['onedecimal']
    msg = ""
    # Testing the condition: isNull(COA) ==> COA == "X" or COA == "N" is not held
    if not isNull(coa) and not (coa == "X" or coa == "N"):
       msg = "The COA must be X, N or null."
       return msg
    
    # Testing the condition: isNull(OneDecimal) ==> OneDecimal == "Y" or OneDecimal == "" is not held
    if not isNull(onedecimal) and not (onedecimal in ["Y", ""]):
       mgs = "The OneDecimal must be Y or blank."
       return msg
    
    # Testing the condition: isNull(COC) ==> COC == "X" or COC == "N" is not held
    if not isNull(coc) and not (coc in [ "X" , "N"]):
       msg = "The COC must be X or null." 
       return mgs


view = {}
view['products'] = {'table':'product', 'order': 'id'}
view['products']['cols'] = {}
view['products']['cols']['name'] = {'p':(str, True)} # {'p':(datatype, IsNull, FKColum, FKTable), 'label':label}
view['products']['cols']['bruto'] = {'p':(str, True)}
view['products']['cols']['name_coa'] = {'p':(str, True) }

view['qualities'] = {'table':'quality', 'order':'id'}
view['qualities']['cols'] = {}
view['qualities']['cols']['name'] = {'p':(str, True)}  # {'p':(datatype, IsNull, FKColum, FKTable), 'label':label}
view['qualities']['cols']['long_name'] = {'p':(str, True) }

view['variables'] = {'table':'variable', 'order':'id'}
view['variables']['cols'] = {}
view['variables']['cols']['name'] = {'p':(str, True)}  # {'p':(datatype, IsNull, FKColum, FKTable), 'label':label}
view['variables']['cols']['test'] = {'p':(str, True) }
view['variables']['cols']['element'] = {'p':(str, False) }
view['variables']['cols']['unit'] = {'p':(str, False) }
view['variables']['cols']['ord'] = {'p':(int, True) }
view['variables']['cols']['typevar'] = {'p':(str, True) }

view['sample_points'] = {'table':'samplepoint', 'order':'name'}
view['sample_points']['cols'] = {}
view['sample_points']['cols']['name'] = {'p':(str, False)}  # {'p':(datatype, IsNull, FKColum, FKTable), 'label':label}

view['maps'] = {'table':'map', 'order':'product.name, quality.name'}
view['maps']['cols'] = {}
view['maps']['cols']['article_code'] = {'p':(int, True)}  # {'p':(datatype, IsNull, FKColum, FKTable), 'label':label}
view['maps']['cols']['product'] = {'p':(str, True), 'fk': 'product', 'column':'product_id' } 
view['maps']['cols']['logistic_info'] = {'p':(str, False) }
view['maps']['cols']['quality'] = {'p':(str, True), 'fk': 'quality', 'column': 'quality_id' }
view['maps']['keys'] = [ ('product', 'quality', 'logistic_info') ] # Unique keys 

view['holidays'] = {'table':'holidays', 'order':'date'}
view['holidays']['cols'] = {}
view['holidays']['cols']['Date'] = {'p':(str, False) }  # (datatype, IsNull, FKColum, FKTable)
view['holidays']['cols']['Description'] = {'p':(str, True) }
view['samplematrix'] = {'table':'samplematrix',  
                        'order':'product.name, quality.name, samplepoint.name',
                        'after': updatedSampleMatrix }
view['samplematrix']['dnorm'] = {}
view['samplematrix']['dnorm']['variable'] = {
    'query':"""SELECT id, 'str' datatype, 'False' not_null, name name, concat('has_', trim(name) ) col, 
    '[''X'',''XX'']' lv, '' validator, typevar, ord 
    FROM variable WHERE typevar='I' 
    UNION 
    SELECT id, 'str' datatype, 'False' not_null, name name, trim(name) col, 
    '[''X'',''XX'']' lv, '' validator, typevar, ord FROM variable WHERE typevar='L' 
    ORDER BY ord"""
}
view['samplematrix']['cols'] = {}
view['samplematrix']['cols']["product"] = {'p':(str, True), 'fk':'product', 'column':'product_id'}  # (datatype, IsNull, FKColum, FKTable)
view['samplematrix']['cols']["quality"] = {'p':(str, True), 'fk':'quality', 'column':'quality_id'}
view['samplematrix']['cols']["samplepoint"] = {'p':(str, True), 'fk':'samplepoint', 'column':'sample_point_id' }
view['samplematrix']['cols']["frequency"] = {'p':(str, True), 'lv':['1/2 year','Batch', 'Batch - loading','Day','Delivery','Month','Quarter','Week','Day - loading']  }
view['samplematrix']['cols']["visual"] = {'p':(str, False), 'lv':["X", "XX", ""]  }
view['samplematrix']['cols']["visueel"] = {'p':(str, False), 'lv':["X", "XX", ""]  }
view['samplematrix']['dcols'] = {}
view['samplematrix']['dcols']["spec_id"] = {'q': """select id from spec where type_spec='GEN' and product_id=:product_id and quality_id=:quality_id""",
                                            'p':('product','quality')    }
view['samplematrix']['keys'] = [ ('product', 'quality', 'samplepoint','frequency') ] # Unique keys 

view['spec-gen'] = {'table':'spec', 
                   'after': updatedSpec,
                    'order': 'product.name, quality.name' }
view['spec-gen']['dnorm'] = {}
view['spec-gen']['dnorm']['variable'] = {
    'query':"""SELECT id, 'str' datatype, 'False' not_null, name name, trim(name) col, '' lv, 'check_interval' validator, 
    typevar, ord FROM variable WHERE typevar='I' 
    UNION 
    SELECT id, 'str' datatype, 'False' not_null, name name, trim(name) col, '[''X'',''Y'']' lv, '' validator, 
    typevar, ord FROM variable WHERE typevar='L' 
    ORDER BY ord """
}
view['spec-gen']['filter'] = {'type_spec':'GEN'}
view['spec-gen']['cols'] = {}
view['spec-gen']['cols']["tds"] = {'p':(str, False) }
view['spec-gen']['cols']["product"] = {'p':(str, True), 'fk':'product' , 'column':'product_id' }
view['spec-gen']['cols']["quality"] = {'p':(str, True), 'fk':'quality', 'column':'quality_id' }
view['spec-gen']['cols']["variable1"] = {'p':(str, False), 'fk':'variable', 'column':'variable1_id' }
view['spec-gen']['cols']["variable2"] = {'p':(str, False), 'fk':'variable', 'column':'variable2_id' }
view['spec-gen']['cols']["variable3"] = {'p':(str, False), 'fk':'variable', 'column':'variable3_id' }
view['spec-gen']['cols']["visual"] = {'p':(str, False) }
view['spec-gen']['keys'] = [ ( 'product', 'quality') ] # Unique keys 


view['spec-client'] = {'table':'spec', 
                        'order':'Customer, product.name, quality.name', 
                        'after': updatedSpec, 'global_check': check_customerparam}
view['spec-client']['dnorm'] = {}
view['spec-client']['dnorm']['variable'] = {
    'query':"""SELECT id, 'str' datatype, 'False' not_null, name name, trim(name) col, '' lv, 'check_interval' validator, 
    typevar, ord FROM variable WHERE typevar='I' 
    UNION 
    SELECT id, 'str' datatype, 'False' not_null, name name, trim(name) col, '[''X'',''Y'']' lv, '' validator, 
    typevar, ord FROM variable WHERE typevar='L' 
    ORDER BY ord"""
}
view['spec-client']['filter'] = {'type_spec':'CLI'}
view['spec-client']['cols'] = {}
view['spec-client']['cols']["customer"] = {'p':(str, True) } # {'p':(datatype, IsNull, FKColum, FKTable), 'label':label}
view['spec-client']['cols']["product"] = {'p':(str, True), 'fk':'product', 'column':'product_id'} 
view['spec-client']['cols']["quality"] = {'p':(str, True), 'fk':'quality' , 'column':'quality_id' }
view['spec-client']['cols']["status"] = {'p':(str, False) }
view['spec-client']['cols']["certificate"] = {'p':(str, False), 'lv':["Y", "N", "M", "Q"] } 
view['spec-client']['cols']["opm"] = {'p':(str, False) }
view['spec-client']['cols']["coa"] = {'p':(str, False), 'lv':['X', 'N']} 
view['spec-client']['cols']["day_coa"] = {'p':(str, False), 'lv':['X', 'N'] }
view['spec-client']['cols']["coc"] = {'p':(str, False), 'lv':['X', 'N'] }
view['spec-client']['cols']["visual"] = {'p':(str, False), 'lv':['Y', 'N'], 'c':'' }
view['spec-client']['cols']["onedecimal"] = {'p':(str, False), 'lv':['X', 'Y'] }
view['spec-client']['keys'] = [ ( 'customer','product', 'quality') ] # Unique keys 

# This function validates the order of the columns from the excel table sheets
def preProcData( db, data, view_name ):
    additional_cols = getDnormColumns(db, view_name) 
    colNames = ['action']
    for col, value in view[view_name]['cols'].items():
        if 'label' in value:
          colNames.append( value['label'] )  
        else:    
          colNames.append( col )
    
    data.columns = list ( map( str.lower, list(data.columns) ) )  
    data.action = data.action.str.upper()
    #print(list(data.columns))
    msgerror = []
    # Validation of the column names    
    ok, msg = checkDataCols(data, colNames, additional_cols)
    if not ok:
        msgerror.append(msg)
        return msgerror, data
        
    # Validation of Action column
    idx = ~(data['action'].isin(["I", "D", "U"])) & ~(data['action'].isna()) & ~(data['action'].str.strip() == '')
    dd = data[idx]
    if len(dd) > 0:
        msgerror.append(f"There are {len(dd)} rows with wrong values in column Action")
        return msgerror, data
    
    data.action = data.action.str.upper()
    idx = data.action.isin(["I", "D", "U"])
    data = data[idx].copy()
    
    # Set nan values to zero for all columns
    for col in data.columns:
        df = data[ data[col].isna() ]
        if col in view[view_name]['cols']:
            if view[view_name]['cols'][col]['p'][0] == str:
              data[col] = data[col].astype(str)        
              for index, row in df.iterrows():
                 data.loc[index, col] = None
    
            if type(data[col].values[0]) is float:
              for index, row in df.iterrows():
                 data.loc[index, col] = None
    
    df = data[ data['id'].isna() ]
    for index, row in df.iterrows():
        data.loc[index, col] = 0
    data.id = data.id.astype(int)
    
    return msgerror, data


# This function validates the column names of data table
def checkDataCols(data, colNames, additional_cols):
    ok = True
    cols = colNames.copy()
    for label, _ in additional_cols:
        cols.append(label)
    msg = ""    
    for i in range(len(cols)):
        col1 = str(data.columns[i]).lower().strip()
        col2 = str(cols[i]).lower().strip()
        if col1 != col2:
            msg = f"Incorrect order of columns. Expected column: {cols[i]}, but received: {data.columns[i]}"
            ok = False
            return ok, msg
        
    return ok, msg


# Addition of the denormalized columns to view
def getDnormColumns(db, view_name, typesql='query'):
    additional_cols = []
    if 'dnorm' in view[view_name]:
        for _, value in view[view_name]['dnorm'].items():
            query = value['query']
            vars = db.execute(text(query))   
            for tt in vars:
                id, datatype, not_null, label, column, lv, validator, typevar, ord = tt 
                validator_name = validator.strip()
                exec( "p=" + datatype, None, locals() ) 
                datatype = locals()['p']
                exec( "p=" + not_null , None, locals() )
                null = locals()['p']
                lv_description = lv.strip()
                validator_name = validator.strip()
                col_info = {'id':id, 'p':(datatype, null), 'column': column, 'typevar':typevar }
                if validator_name:
                    col_info['validator'] = validator_name
                if  lv_description:
                    exec( "p ="+ lv , None, locals()  )
                    lv = locals()['p'] # Extraction of the validator function
                    col_info['lv'] = lv # List of values 
                
                # Handle reserved keywords for all cases
                if label.lower() in ['as', 'in']:
                    label = label + '1'

                # Correction of the column
                if validator_name == 'check_interval' and typesql == 'query':
                    col_info['column'] = f"CONCAT(CAST(min_{column} AS FLOAT), '-', CAST(max_{column} AS FLOAT))"
                    additional_cols.append((label, col_info))
                elif validator_name == 'check_interval' and typesql != 'query':
                    col_info['column'] = f"min_{column}"
                    additional_cols.append(("min_"+label, col_info))
                    col_info2 = col_info.copy()
                    col_info2['column'] = f"max_{column}"
                    additional_cols.append(("max_"+label, col_info2))
                else:
                    additional_cols.append((label, col_info))
                
    return additional_cols


def saveView(view_name, db, data):
    pendingdata = pd.DataFrame()
    ndeleted = 0
    nupdated = 0
    ninserted = 0
    x=0
    stat = pd.DataFrame({'ndeleted': [ndeleted], 'nupdated': [nupdated], 'ninserted': [ninserted]}) 
    # Addition of denormalized columns 
    msgerror, data = preProcData(db, data, view_name)
    if msgerror:
        # Convert stat DataFrame to dict with native Python types
        stat_dict = convert_numpy_types(stat.to_dict('records')[0])
        return msgerror, stat_dict, pendingdata
    
    data.columns = [col.strip() for col in data.columns] # Elimination of blanks in column names
    additional_cols_dml = getDnormColumns(db, view_name, '*') # additional columns for DML 
    additional_cols_query = getDnormColumns(db, view_name) # additional columns for query 
    for i, row in data.iterrows():        
        Action = row['action']
        id = int( row['id'] )        
        if Action == "D":
            if not pd.isna(row['id']):
                sql = text("DELETE FROM " + view[view_name]['table'] +"  WHERE id = :id")
                db.execute(sql, {'id': int(row['id']) })
                db.commit()
                ndeleted += 1
            else:
                msgerror.append(f"Action={Action}, row {i}, id:{id}.  The row can not be deleted.")
                data.loc[i,'action'] =  "*" + Action
    
        elif Action == "U": 
            row2, msg = validateView(view_name, i, db, row, additional_cols_query)            
            if msg:
                msgerror.extend(msg)
                data.loc[i,'action'] =  "*" + Action
            else:
                if 'global_check' in view[view_name]:
                    msg = view[view_name]['global_check'](row2)
                if msg:
                    msgerror.extend(msg)
                    data.loc[i,'action'] =  "*" + Action
                else:    
                    id = checkFK(db, f"SELECT id FROM " + view[view_name]['table'] +" WHERE id=:id", id=id)
                    if id > 0:
                        update = buildUpdateSimple( view_name, additional_cols_dml )
                        row3 = setAdditionalParameters(db, view_name, row2, action='update')
                        db.execute(text(update), row3 )
                        if 'after' in view[view_name]:
                            new_id = result.scalar()
                            view[view_name]['after'](db, id, row3, additional_cols_query)
                        db.commit()
                        nupdated += 1
                    else:
                        msgerror.append(f"Action {Action}, row {i}, Invalid id. Upload this file with the latest version. The row is not updated.")
                        data.loc[i,'action'] =  "*" + Action
        elif Action == "I":  
            row2, msg = validateView(view_name, i, db, row, additional_cols_query)
            if msg:
                msgerror.extend(msg)
                data.loc[i,'action'] =  "*" + Action
            else:
                if 'global_check' in view[view_name]:
                    msg = view[view_name]['global_check'](row2)
                if msg:
                    msgerror.extend(msg)
                    data.loc[i,'action'] =  "*" + Action
                else:    
                    insert = buildInsertSimple(view_name, additional_cols_dml)
                    row3 = setAdditionalParameters(db, view_name, row2, action='insert')
                    result = db.execute(text(insert), row3)
                    if 'after' in view[view_name]:
                        new_id = result.scalar()
                        view[view_name]['after'](db, new_id, row3, additional_cols_query)
                    ninserted += 1
                    db.commit()
    
    for i in range(len(msgerror)):
        msgerror[i] = str(i + 1) + ")" + msgerror[i]

    stat = pd.DataFrame({'ndeleted': [ndeleted], 'nupdated': [nupdated], 'ninserted': [ninserted]})
    # Convert stat DataFrame to a dict with native Python types
    stat_dict = convert_numpy_types(stat.to_dict('records')[0])

    idx = (data['action'] == "*I") | (data['action'] == "*D") | (data['action'] == "*U")
    pendingdata = data[idx]

    return msgerror, stat_dict, pendingdata



# This function sets parameters of derivated columns and filters of the view_name
def setAdditionalParameters(db, view_name, row2, action='insert'):
    if 'filter' in view[view_name]:
        for col, value in view[view_name]['filter'].items():
                row2[col] = value

    # Add timestamp handling
    current_time = datetime.now()
    if action == 'insert':
        row2['created_at'] = current_time
        row2['updated_at'] = current_time
    elif action == 'update':
        row2['updated_at'] = current_time

    return row2


# This function computes the sql udpate for a simple view
def buildUpdateSimple( view_name, additional_cols ):
    update = "UPDATE " + view[view_name]['table'] + " SET "
    for label, value in view[view_name]['cols'].items():
        if label.lower() in ['as','in']:
           label = label + '1'
        column = label
        if 'column' in value:
            column = value['column']
    
        if 'fk' in value:
           colFk = value['column']
           update = update + colFk + "=:" + colFk.lower() + ","
        else:
           update = update + column + "=:"+label.lower() + ","
    
    for label, col_info in additional_cols:
        # Handle reserved keywords by using the label as-is (it already has '1' suffix if needed)
        param_name = label.lower()
        update = update + col_info['column'] + "=:" + param_name + ","

    # Add denormalized columns (dcols)
    if 'dcols' in view[view_name]:
        for dcol_name, dcol_def in view[view_name]['dcols'].items():
            update = update + dcol_name + "=:" + dcol_name.lower() + ","

    if 'filter' in view[view_name]:
        for col, value in view[view_name]['filter'].items():
            update = update + col + "=:"+col.lower() +","

    # Add updated_at timestamp
    update = update + "updated_at=:updated_at,"

    update = update[0:-1] + " WHERE id=:id"
    return update

# This function computes the sql insert for a simple view
def buildInsertSimple( view_name, additional_cols ):
    insert = "INSERT into " + view[view_name]['table'] + "("
    for label, value in view[view_name]['cols'].items():
        label = label.strip()
        if label.lower() in ['as','in']:
           label = label + '1'
        column = label
        if 'column' in value:
           column = value['column']

        if 'fk' in value:
            colFk = value['column']
            insert = insert + colFk + ","
        else:
            insert = insert + column + ","

    for label, col_info in additional_cols:
        # Use the actual database column name (not the label)
        insert = insert + col_info['column'] + ","

    # Add denormalized columns (dcols)
    if 'dcols' in view[view_name]:
        for dcol_name, dcol_def in view[view_name]['dcols'].items():
            insert = insert + dcol_name + ","

    if 'filter' in view[view_name]:
        for col, value in view[view_name]['filter'].items():
            insert = insert + col + ","

    # Add created_at and updated_at columns
    insert = insert + "created_at,updated_at,"

    insert = insert[0:-1] + ") "

    # Add OUTPUT clause for SQL Server to return the inserted ID when 'after' callback is present
    if 'after' in view[view_name]:
        insert = insert + "OUTPUT inserted.id "

    insert = insert + "VALUES( "
    for label, value in view[view_name]['cols'].items():
        label = label.strip()
        if label.lower() in ['as','in']:
           label = label + '1'

        if 'fk' in value:
            colFk = value['column']
            insert = insert + ":" + colFk.lower() + ","
        else:
            insert = insert + ":" + label.lower() + ","

    for label, col_info in additional_cols:
        # Use the label (which may have '1' suffix for reserved keywords) for bind parameter
        param_name = label.lower()
        insert = insert + ":" + param_name + ","

    # Add denormalized columns (dcols) values
    if 'dcols' in view[view_name]:
        for dcol_name, dcol_def in view[view_name]['dcols'].items():
            insert = insert + ":" + dcol_name.lower() + ","

    if 'filter' in view[view_name]:
        for col, value in view[view_name]['filter'].items():
            insert = insert + ":" + col.lower() + ","

    # Add created_at and updated_at values
    insert = insert + ":created_at,:updated_at,"

    insert = insert[0:-1] + ")"
    return insert


def validateView(view_name, i, db, row, additional_cols):
    msgerror = []
    id = int(row['id'] )
    Action = row['action'].strip()
    id2 = 0
    row2={}
    if Action == "U" and id ==0:
       msgerror.append(f"Action={Action}, id {id} row {i}. id must be not null")
       return row2, id2, msgerror
    
    if Action == "U" and not type(id) is int:
        msgerror.append(f"Action={Action}, id {id} row {i}. id must be Integer.")
        return row2, id2, msgerror
    
    cols = list(view[view_name]['cols'].items()).copy()
    cols.extend(additional_cols)
    
    # Pre-initialize all expected keys with None for interval validators
    # This ensures that even if a column is empty, the key exists in row2
    for col, value in additional_cols:
        if 'validator' in value and value['validator'] == 'check_interval':
            # For interval validators, we need both min and max keys
            label = col
            row2['min_'+label.lower()] = None
            row2['max_'+label.lower()] = None
    
    # First we validate for not null column, FK and Enum
    for col, value in cols:
        colinfo = value['p']
        label = col 
        key = label.lower()
        if key in ['as', 'in']: # If label crashes with a reserved word in sql
           label = label + '1'
    
        if  colinfo[1]: # if the column is not null
            if isNull(row[key]): 
              msgerror.append(f"Action={Action}, row {i}. {label} must not be null.")
              return row2, msgerror
    
        if 'validator' in value:
            validator = value['validator']
            # Get the actual database column name from col_info (already has min_/max_ prefix)
            db_column = value['column']
            if isinstance(row[key], str):
                ss = row[key].replace(' ','')
                exec( "msg = " + validator + "(label, ss)" ,  globals(), locals() )
                msg = globals()['msg']
                if msg:
                    msgerror.append(msg)
                    return row2, msgerror
                ll = ss.split('-')
                # db_column already has min_ prefix from getDnormColumns, use it directly
                # But we need both min and max, so construct them based on label
                row2['min_'+label.lower()] = None
                row2['max_'+label.lower()] = None
                if len(ll)>0 and ll[0] != '':
                  row2['min_'+label.lower()] = float(ll[0])
                if len(ll)>1 and ll[1] != '':
                   row2['max_'+label.lower()] = float(ll[1])
        
            if isinstance(row[key], float) and math.isnan(row[key]):
               row2['min_'+label.lower()] = None
               row2['max_'+label.lower()] = None
                         
        else:
            # Convert nan to None to avoid SQL Server ODBC errors
            row2[key] = None if (isinstance(row[key], float) and math.isnan(row[key])) else row[key]
            if isinstance(row[key], str) and row[key] is not None:
                row2[key] = row[key].strip()
        
        if 'lv' in value:
            lv = value['lv']
            if not isNull(row2[key]) and  not row2[key].strip() in lv:
                msgerror.append(f"Action={Action}. Value {row[key]}  and {key} must be {lv}.")
                return row2, msgerror
        
            # Convert nan to None to avoid SQL Server ODBC errors
            row2[key] = None if (isinstance(row[key], float) and math.isnan(row[key])) else row[key]
            if type(row[key]) is str:
               row2[key] = row[key].strip()
         
        elif 'fk' in value:
            table =  value['fk']
            colFk = value['column']
            # Check if the value is null/empty
            if isNull(row[key]):
                # For nullable FK columns, set to None
                if not colinfo[1]:  # if column is nullable
                    row2[colFk] = None
                else:  # if column is not null but value is null, it's an error
                    msgerror.append(f"Action={Action}, row {i}. {label} must not be null.")
                    return row2, msgerror
            else:
                row2[colFk] = checkFK(db, "Select id From "+ table +" Where name=:p1", p1=row[key])
                if row2[colFk] == 0: # If the FK value does not exist
                    msgerror.append(f"Action={Action}, row {i}, id:{id}. {col}:{row[key]} does not exist.")
                    return row2, msgerror
    
    # Process denormalized columns (dcols) - computed columns based on queries
    if 'dcols' in view[view_name]:
        for dcol_name, dcol_def in view[view_name]['dcols'].items():
            query = dcol_def['q']
            param_names = dcol_def['p']

            # Build parameters dictionary from row2 using the parameter mapping
            query_params = {}
            param_values_display = []  # For error message display
            for param_name in param_names:
                # Get the column name from the view definition
                if param_name in view[view_name]['cols']:
                    col_def = view[view_name]['cols'][param_name]
                    if 'column' in col_def:
                        # Use the actual database column name
                        db_col_name = col_def['column']
                        # Get the value from row2 (which already has FK ids resolved)
                        if db_col_name in row2:
                            query_params[db_col_name] = row2[db_col_name]
                            # Store the display value (original input) for error message
                            param_values_display.append(f"{param_name}='{row[param_name.lower()]}'")

            # Execute the query to get the denormalized column value
            dcol_value = checkFK(db, query, **query_params)

            # Validate: check if the denormalized column value is NULL/None
            if dcol_value == 0 or dcol_value is None:
                # Build descriptive error message
                param_info = ", ".join(param_values_display)
                msgerror.append(
                    f"Action={Action}, row {i}. Denormalized column '{dcol_name}' is NULL or None. "
                    f"No matching record found for parameters: {param_info}."
                )
                return row2, msgerror
            else:
                # Store the valid value in row2
                row2[dcol_name] = dcol_value

    # Checking uniqueness of keys   
    if 'keys' in view[view_name] and Action =='I':
        for key in view[view_name]['keys']:
            sql = "SELECT id FROM "+ view[view_name]['table'] +" WHERE "
            if 'filter' in view[view_name]:
                for col, value in view[view_name]['filter'].items():            
                    if type(value) is str:
                        value = "'" + value + "'"
                    sql = sql + col + "=" + value + " AND "
    
            parameters = {}
            for col in key:                
                colinfo = view[view_name]['cols'][col]['p']
                if 'fk' in view[view_name]['cols'][col]:
                    column = view[view_name]['cols'][col]['column']
                else:
                    column = col
    
                sql = sql + column + f"=:{column} AND " 
                parameters[column] = row2[column] 
        sql = sql[0:-4]
        id2 = checkFK0(db, sql, parameters )
        if  id2 > 0:
            msg =f"Action {Action}, row {i}, The combination " 
            for col in key:
                msg = msg + col  + ","
            msg = msg[0:-1] + ":("
            for col in key:
                msg = msg + row[col] + ","
    
            msg = msg[0:-1] + ")  already exists."
            msgerror.append(msg)
            return row2, msgerror 
    
    if Action == "U":
       row2['id']=id
          
    return row2, msgerror 


def getView(db, view_name):
    query, col_names = buildQuery(db, view_name)
    tts = db.execute(text(query)) # List of tuples
    dict_list = [convert_numpy_types(dict(zip(col_names, t))) for t in tts]
    if len(dict_list) == 0:
        dict_list.append( dict.fromkeys(col_names) )
    return dict_list    
