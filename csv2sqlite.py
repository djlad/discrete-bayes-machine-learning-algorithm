import sqlite3
import pandas as pd

if __name__ == "__main__":
    file_name = 'pr_data'
    con = sqlite3.connect("observations.db")
    column_names = ["f1","f2","f3","f4","f5","class"]
    data = pd.read_csv(file_name, names=column_names, delimiter='\s+')#, nrows=1000)
    data.to_sql("observations", con)
    con.close()