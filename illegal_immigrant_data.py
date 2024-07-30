import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="Illegal encounters in US 2021-2024",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

df_illegals = pd.read_csv("immigration encounters 2024.csv")
df_illegals = df_illegals.fillna(0)
df_illegals = df_illegals.replace(",", "", regex=True)
df_illegals
df_illegals["totalencounters"] = df_illegals["totalencounters"].astype(int)
df_illegals["year"] = pd.to_numeric(df_illegals["year"], downcast='integer', errors='coerce')

with st.sidebar:
    st.title('🏂 Illegal Encounters Dashboard')
    
    year_list = list(df_illegals["year"].unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list, index=len(year_list)-1)
    df_selected_year = df_illegals[df_illegals["year"] == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="totalencounters", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
   	heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
           	x=alt.X(f'{input_x}:O', axis=alt.Axis(title="Total Encounters", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                              legend=None,
                              scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
return heatmap

def calculate_totalencounters_difference(input_df, input_year):
  	selected_year_data = input_df[input_df['year'] == input_year].reset_index()
  	previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
  	selected_year_data['totalencounters_difference'] = selected_year_data.totalencounters.sub(previous_year_data.totalencounters, fill_value=0)
  	return pd.concat([selected_year_data.month, selected_year_data.totalencounters, selected_year_data.totalencounters_difference], axis=1).sort_values(by="totalencounters_difference", ascending=False)


def make_donut(input_response, input_text, input_color):
  	if input_color == 'blue':
            chart_color = ['#29b5e8', '#155F7A']
  	if input_color == 'green':
            chart_color = ['#27AE60', '#12783D']
  	if input_color == 'orange':
            chart_color = ['#F39C12', '#875A12']
  	if input_color == 'red':
            chart_color = ['#E74C3C', '#781F16']
    
  	source = pd.DataFrame({
            "Topic": ['', input_text],
            "% value": [100-input_response, input_response]
  	})
        source_bg = pd.DataFrame({
            "Topic": ['', input_text],
            "% value": [100, 0]
  	})
    
  	plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      	    theta="% value",
      	    color= alt.Color("Topic:N",
                      	    scale=alt.Scale(
                                 #domain=['A', 'B'],
                                 domain=[input_text, ''],
                                 # range=['#29b5e8', '#155F7A']),  # 31333F
                                 range=chart_color),
                            legend=None),
  	).properties(width=130, height=130)
    
  	text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
        plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
            theta="% value",
            color= alt.Color("Topic:N",
                            scale=alt.Scale(
                                  # domain=['A', 'B'],
                                  domain=[input_text, ''],
                                  range=chart_color),  # 31333F
                            legend=None),
  	).properties(width=130, height=130)
  	return plot_bg + plot + text

  	col = st.columns((1.5, 4.5, 2), gap='medium')


with col[0]:
    st.markdown('#### Gains/Losses')

    df_totalencounters_difference_sorted = calculate_totalencounters_difference(df_illegals, selected_year)

    if selected_year > 2021:
        first_month_name = df_totalencounters_difference_sorted.months.iloc[0]
        first_month_totalencounters = format_number(df_totalencounters_difference_sorted.totalencounters.iloc[0])
        first_month_delta = format_number(df_totalencounters_difference_sorted.totalencounters_difference.iloc[0])
    else:
        first_month_name = '-'
        first_month_totalencounters = '-'
        first_month_delta = ''
    st.metric(label=first_month_name, value=first_month_totalencounters, delta=first_month_delta)

    if selected_year > 2021:
        last_month_name = df_totalencounters_difference_sorted.months.iloc[-1]
        last_month_totalencounters = format_number(df_totalencounters_difference_sorted.totalencounters.iloc[-1])   
        last_state_delta = format_number(df_totalencounters_difference_sorted.totalencounters_difference.iloc[-1])   
    else:
        last_month_name = '-'
        last_month_totalencounters = '-'
        last_month_delta = ''
    st.metric(label=last_month_name, value=last_month_totalencounters, delta=last_month_delta)

    
    st.markdown('#### month Encounters')

    if selected_year > 2021:
        # Filter states with population difference > 500000
        # df_greater_500000 = df_encounters_difference_sorted[df_encounters_difference_sorted.encounters_difference_absolute > 5000]
        df_greater_500000 = df_totalencounters_difference_sorted[df_totalencounters_difference_sorted.totalencounters_difference > 500000]
        df_less_500000 = df_totalencounters_difference_sorted[df_totalencounters_difference_sorted.totalencounters_difference < -500000]
        
        # % of months with encounter difference > 500000
        months_totalencounters_greater = round((len(df_greater_500000)/df_totalencounters_difference_sorted.months.nunique())*100)
        months_totalencounters_less = round((len(df_less_500000)/df_totalencounters_difference_sorted.months.nunique())*100)
        donut_chart_greater = make_donut(months_totalencounters_greater, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(months_totalencounters_less, 'Outbound Migration', 'red')
    else:
        months_totalencounters_greater = 0
        months_totalencounters_less = 0
        donut_chart_greater = make_donut(months_totalencounters_greater, 'positive encounter amount', 'green')
        donut_chart_less = make_donut(months_totalencounters_less, 'negative encounter amount', 'red')

    totalencounters_col = st.columns((0.2, 1, 0.2))
    with totalencounters_col[1]:
        st.write('positive')
        st.altair_chart(donut_chart_greater)
        st.write('negative')
        st.altair_chart(donut_chart_less)

with col[1]:
    st.markdown('#### Total Encounters') 
    heatmap = make_heatmap(df_illegals, 'year', 'month', 'totalencounters', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

with col[2]:
    st.markdown('#### Top months')

    st.dataframe(df_selected_year_sorted,
                 column_order=("month", "Total Encounters"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "month": st.column_config.TextColumn(
                        "month",
                    ),
                    "Total Encounters": st.column_config.ProgressColumn(
                        "Total Encounters",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.totalencounters),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [US Customs and Border Protection](<https://www.cbp.gov/newsroom/national-media-release/cbp-releases-january-2024-monthly-update>).
            - :orange[**Gains/Losses**]: states with high illegal crossing encounters/ negative illegal crossing encounters for selected year
            - :orange[**Month Encounters**]: percentage of months with annual high/ low encounters > 500,000
            ''')


