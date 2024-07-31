import pandas as pd

def make_clickable(val):
    return f'<a href={val}>{val}</a>'

def make_list_clickable(val):
    return [make_clickable(i) for i in val]

def make_hrefs_in_dataframe(df, columns, list_columns):
    style_map = {i: make_clickable for i in columns}
    style_map.update({i: make_list_clickable for i in list_columns})
    df_styled = df.style.format(style_map)
    return df_styled
    