import pandas as pd

def csv_to_text(csvfile):
    df = pd.read_csv(csvfile)
    text = df.to_string(index=False, header=False)
    with open('./working/output.txt', 'a') as file:
        file.write(text)
        file.write('\n') 
        