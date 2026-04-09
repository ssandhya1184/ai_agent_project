import pandas as pd
import streamlit as st
import os
import json

#----------------------
# MCP CONFIG LOADER
#----------------------
def load_mcp_config(*server_names):
    config_path = os.path.join(os.path.dirname(__file__),'mcp_config.json')
    with open(config_path,'r') as f:
        all_config =json.load(f)

    if len(server_names) == 0:
        return all_configs
    
    selected_configs = {}
    for name in server_names:
        if name in all_config:
            selected_configs[name] = all_config[name]
            
    return selected_configs




@st.cache_data
def load_data():
    return pd.read_csv("docs/HR-Employee-Attrition.csv")


def filter_data(df, departments, age_range):
    return df[
        (df["Department"].isin(departments)) &
        (df["Age"].between(age_range[0], age_range[1]))
    ]


def compute_kpis(df):
    total_emp = len(df)
    attrition_rate = (df["Attrition"] == "Yes").mean() * 100
    avg_salary = df["MonthlyIncome"].mean()

    return total_emp, attrition_rate, avg_salary