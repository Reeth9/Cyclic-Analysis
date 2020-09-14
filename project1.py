import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#%matplotlib inline
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import cufflinks as cf
init_notebook_mode(connected=True)
cf.go_offline()
import seaborn as sns; sns.set()

def matfunc(path1,path2,dlabels):
    """
    1. path1 is the path of 'materials.csv'. This dataset comprises of the list of all materials with their corresponding codes.
    
    2. path2 is the path of 'matpost.csv'. This dataset comprises of all the transactions done on all the materials.
    
    3. dlabels is the dictionary that contains all the columns used for processing of this dataframe.
        Here are the column names that MUST be entered for the corresponding field.
            dlabels={'code': column containing materials code ,
                     'name': column containing materials names,
                     'mat_code':column containg the matpost code,
                     'names':column containg the matpost names,
                     'tran_date':column containing transaction date,
                     'purchase':newly added column containing purchase value,
                     'issue':newly added column containing issue value,
                     'qty':column containing the quantity,
                     'compunit_id':column containing the company unit ID,
                     'qty_nos':column containing the quantity numbers,
                     'mat_qty':column containing matpost quantity,
                     'mat_rate':column containing matpost rate,
                     'mat_value':column containing matpost value}
    
    This function does the following:
        1. It compares the code and the mat_code columns of materials and matpost dataframe respectively. It then creates another
           column called 'Names' which consists of all the names of the materials which correspond to their material code.
        2. It converts the transcation date into timestamp format.
        3. It creates two new columns called purchase and issue based on the quatity column. 
        4. Finally, a new dataframe is created with the mentioned columns. 
    """
    #Reads csv files
    materials = pd.read_csv(path1) 
    matpost = pd.read_csv(path2)
    
    #Takes the codes and names column from the dataframe and converts it into a dictionary
    d=materials.set_index(dlabels.get('code'))[dlabels.get('name')].to_dict()
    
    #It replaces NaN values with 0
    matpost[dlabels.get('mat_code')] = matpost[dlabels.get('mat_code')].replace(np.nan, 0)
    
    #It changes the datatype of the 'mat_code' column
    matpost[dlabels.get('mat_code')].astype(int)
    
    #This function compares codes from two dataframes and returns a new column with the corresponding name.
    def names(s):
        for k,v in d.items():
            if k == s:
                return v
        
    matpost[dlabels.get('names')] = matpost[dlabels.get('mat_code')].astype(int).apply(names)
    
    #This function compares code and material type from two dataframes and returns a new column with corresponding material type
    b=materials.set_index(dlabels.get('code'))[dlabels.get('mat_type')].to_dict()
    def mattype(s):
        for k,v in b.items():
            if k == s:
                return v    
    matpost[dlabels.get('mat_type')] = matpost[dlabels.get('mat_code')].astype(int).apply(mattype)
    
    #It converts the transcation date into timestamp format
    matpost[dlabels.get('tran_date')]= pd.to_datetime(matpost[dlabels.get('tran_date')], format="%Y%m%d")
    
    #It creates two new columns called purchase and issue based on the quatity column
    matpost[dlabels.get('purchase')]=None
    matpost[dlabels.get('issue')]=None
    matpost[dlabels.get('issue')] = matpost[dlabels.get('qty')].apply(lambda x:x if x < 0 else 0)
    matpost[dlabels.get('purchase')] = matpost[dlabels.get('qty')].apply(lambda x:x if x > 0 else 0)
    
    #It converts all the values to positive.
    matpost[dlabels.get('issue')] = matpost['Issue'].abs()
    
    #A new dataframe is created with the mentioned columns
    mat1 = matpost.filter([dlabels.get('tran_date'),dlabels.get('names'),dlabels.get('compunit_id'),dlabels.get('qty'),dlabels.get('qty_nos'),dlabels.get('mat_qty'),dlabels.get('mat_rate'),dlabels.get('mat_value'),dlabels.get('purchase'),dlabels.get('issue')], axis=1)
    mat1 = mat1.set_index(dlabels.get('tran_date'))
    return mat1

    
def get_most(mat,n):
    """
    It gives the list of most recurrning n materials of the given data frame.
    mat is the dataframe.
    n is the number of materials.
    """
    most_used = mat['Names'].value_counts()[:n].index.tolist()
    return print(most_used)

def mat_by_name(mat1,material):
    """
    1. It groups the dataframe according to month for a particular material only.
    2. It performs respective opertions on each column.
        a. Adds all the values in the column for each month.
           QTY_NOS, MAT_QTY, Purchase, Issue
        b. Finds the average of all the values in the column for each month.
           MAT_RATE, MAT_VALUE
    """
    temp = mat1[mat1['Names'] == material]
    temp = temp.resample('M').agg({'QTY_NOS':sum,'MAT_QTY':sum,'MAT_RATE':'mean','MAT_VALUE':'mean','Purchase':sum,'Issue':sum})
    return temp

def name_sort(mat, name):
    """
    This fuction filters the dataframe for a given word.
    mat is the dataframe.
    name is the name you want to enter
    """
    def soort(l):
        for i in l.split():
            if i.lower() == name:
                return 1

        return 0
    mat['temp'] = None
    mat['Names'] = mat['Names'].astype(str)
    mat['temp'] = mat['Names'].apply(soort)
    mat = mat[mat['temp'] == 1]
    mat = mat.drop('temp',axis=1)
    return mat

def data_sort(mat_,mat_type='104.0',sort_for_mat_type=False,max_values=5,mat_name='sand',sort_for_name=False):
    
    if sort_for_name == True:
        temp2 = name_sort(mat_,mat_name)
        mat = temp2
        most = get_most(temp2,max_values)
        return interact(mat_by_name, material = most , plot = True)
    
    elif sort_for_mat_type == True:
        temp1 = mat_[mat_['MATERIAL_TYPE'] == float(mat_type)]
        mat = temp1
        most = get_most(temp1,max_values)
        return interact(mat_by_name, material = most , plot = True)
    
    else:
        mat = mat_
        #return mat
        most = get_most(mat,max_values)
        return interact(mat_by_name, material = most , plot = True)
