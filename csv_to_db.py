import sqlite3
import pandas as pd
    
def make_db():
    df1 = pd.read_csv('./working/Company.csv')
    df2 = pd.read_csv('./working/Political_Party.csv')

    df1.columns=df1.columns.str.strip()
    df2.columns=df2.columns.str.strip()

    connection = sqlite3.connect('./working/working.db')

    df1.to_sql('Company',connection,if_exists='replace',index=False)
    df2.to_sql('Political_Party',connection,if_exists='replace',index=False)
    
    query = """
            SELECT *
            FROM Company
            NATURAL JOIN Political_Party
            """
    joined_df = pd.read_sql(query, connection)

    # Optionally, you can save the joined result back to a new table in the database
    joined_df.to_sql('Joined_Table', connection, if_exists='replace', index=False)


    connection.close()
    
    
