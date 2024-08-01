import pandas as pd


def make_clickable(val):
    if pd.isna(val) or val is None:
        return ""
    return f"<a href={val}>{val}</a>"


def make_list_clickable(val):
    return "<br><br>".join([make_clickable(i) for i in val])


def make_hrefs_in_dataframe(df, columns, list_columns):
    style_map = {i: make_clickable for i in columns}
    style_map.update({i: make_list_clickable for i in list_columns})
    df_styled = df.style.format(style_map).hide()
    df_styled = df_styled.set_table_styles(
        [
            {
                "selector": "th, td",
                "props": [("border", "1px solid black"), ("padding", "8px")],
            },
            {
                "selector": "table",
                "props": [("border-collapse", "collapse"), ("width", "100%")],
            },
            {
                "selector": "th",
                "props": [("background-color", "#f2f2f2"), ("font-weight", "bold")],
            },
            {
                "selector": "tr:nth-child(even)",
                "props": [("background-color", "#f9f9f9")],
            },
        ]
    )
    return df_styled
