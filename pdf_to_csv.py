from tabula import read_pdf
import pandas as pd
from csv_to_db import make_db


def convert_to_csv(pdf_docs):

    pdfs = []

    for pdf in pdf_docs:
        df = read_pdf(pdf, pages="all", multiple_tables=True)
        full_df = pd.concat(df, ignore_index=True)
        pdfs.append(full_df)

    parse_company(pdfs[0])
    parse_party(pdfs[1])
    make_db()


def parse_company(full_df1):
    columns_to_drop = [
        "Sr No.",
        "Reference No  (URN)",
        "Journal Date",
        "Date of Expiry",
        "Issue Branch Code",
        "Issue Teller",
    ]
    full_df1 = full_df1.drop(columns=columns_to_drop, axis=1)
    full_df1.columns = full_df1.columns.str.replace("\r", " ")
    full_df1.columns = full_df1.columns.str.replace(" ", "_")
    full_df1["Denominations"] = pd.to_numeric(
        full_df1["Denominations"].str.replace(",", "")
    )
    full_df1 = full_df1.rename(columns={"Date_of_Purchase": "purchase_date"})
    full_df1 = full_df1.rename(columns={"Name_of_the_Purchaser": "company"})
    full_df1 = full_df1.rename(columns={"Bond_Number": "bond_id"})
    full_df1 = full_df1.rename(columns={"Denominations": "bond_amount"})
    full_df1 = full_df1.rename(columns={"Prefix": "prefix"})
    full_df1 = full_df1.rename(columns={"Status": "status"})
    full_df1.to_csv("./working/Company.csv", index=False)


def parse_party(full_df2):
    columns_to_drop = [
        "Sr No.",
        "Account no. of\rPolitical Party",
        "Pay Branch\rCode",
        "Pay Teller",
    ]
    full_df2 = full_df2.drop(columns=columns_to_drop, axis=1)
    full_df2.columns = full_df2.columns.str.replace("\r", " ")
    full_df2.columns = full_df2.columns.str.replace(" ", "_")
    full_df2["Denominations"] = pd.to_numeric(
        full_df2["Denominations"].str.replace(",", "")
    )
    full_df2 = full_df2.rename(columns={"Date_of_Encashment": "cashout_date"})
    full_df2 = full_df2.rename(
        columns={"Name_of_the_Political_Party": "political_party"}
    )
    full_df2 = full_df2.rename(columns={"Bond_Number": "bond_id"})
    full_df2 = full_df2.rename(columns={"Denominations": "bond_amount"})
    full_df2 = full_df2.rename(columns={"Prefix": "prefix"})
    full_df2.to_csv("./working/Political_Party.csv", index=False)
