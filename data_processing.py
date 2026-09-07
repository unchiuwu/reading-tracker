# DATA PROCESSING

import os

import gspread
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# LOAD DATA FROM GOOGLE SHEETS

def load_data():

    load_dotenv()

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scopes
    )

    client = gspread.authorize(creds)

    sheet_id = os.getenv("SHEET_ID")

    sheet = (
        client
        .open_by_key(sheet_id)
        .worksheet("Public")
    )

    data = sheet.get_all_records()

    df = pd.DataFrame(data)

    return df


# CLEAN AND PREPARE DATA

def prepare_data(df):

    df = df.copy()

        # Remove leading/trailing whitespace from all values.
    
    df = df.map(
        lambda x: x.strip()
        if isinstance(x, str)
        else x
    )

    # Convert blank cells into proper missing values.
    df = df.replace(
        r"^\s*$",
        np.nan,
        regex=True
    )

        # Convert numerical analytical columns.
    
    numeric_columns = [
        "Start_Day",
        "Start_Month",
        "Start_Year",
        "Finish_Day",
        "Finish_Month",
        "Finish_Year",
        "Publish_Year"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        # Standardise categorical columns.
    
    categorical_columns = [
        "Status",
        "Language",
        "Type",
        "Start_Precision",
        "Finish_Precision"
    ]

    for column in categorical_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # ANALYTICAL COMPLETION YEAR

    #
    # Known year:
    #     2025 → 2025
    #
    # Read + unknown year:
    #     NaN + Read → 0.0
    #
    # Unread:
    #     NaN → remains NaN
    #

    df["Reading_Year"] = df["Finish_Year"]

    df.loc[
        df["Status"].eq("Read")
        & df["Finish_Year"].isna(),
        "Reading_Year"
    ] = 0.0

    return df


# LOAD + PREPARE

def get_data():

    df = load_data()

    df = prepare_data(df)

    return df
