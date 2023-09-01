import pandas as pd 
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime 

#define function

def style_negative(v,v_compare,props=''):
    """Style positive Values in dataframe"""
    try:
        return props if v <= v_compare else None
    except:
        pass

def style_positve(v,v_compare,props=''):
    """Style negative Values in dataframe"""
    try:
        return props if v > v_compare else None
    except:
        pass

#Extract/Load data
@st.cache_data #You can load data one time
def load_data():
    df_Rg_month = pd.read_csv("RG_Month_Steam.csv")
    df_Rg_year = pd.read_csv("RG_Year_Steam.csv")
    df_Tags_Steam =pd.read_csv("Tags_Steam.csv")
    
    #Concanate similar files to a sinlge Df
    year_list = [2018,2019,2020,2021,2022,2023]
    dfs = []
    for year in year_list:
        df = pd.read_csv("Top_RG_{}.csv".format(year))
        dfs.append(df)
    df_Toprelease = pd.concat(dfs, ignore_index = True)
    #Transform Data
    df_Toprelease['Release'] = pd.to_datetime(df_Toprelease['Release'])
    df_Rg_month['DateTime'] = pd.to_datetime(df_Rg_month['DateTime'])
    df_Rg_year['DateTime'] = pd.to_datetime(df_Rg_year['DateTime'])

    Startime_df_Rg_month = pd.to_datetime(df_Rg_month["DateTime"][0])

    return df_Rg_month,df_Rg_year, df_Tags_Steam,df_Toprelease,Startime_df_Rg_month


#Crate Datasets from function
df_Rg_month,df_Rg_year, df_Tags_Steam,df_Toprelease,Startime_df_Rg_month = load_data()

#Build Dashboard
#sidebar
if 'my_button' not in st.session_state:
    st.session_state.my_button = True
option = st.sidebar.write("Select the option")
option = st.sidebar.radio(
        "",
        ["Release", "Tags", "DataFrame"],
    )


#Total layout
if option == "Release":
    #For Histogram init value
    x_month = []
    x_topmont = []
    Mont_Order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    add_sidebar_release_Month=st.selectbox("Realese Games",("For month","For Year"))
    
    
    if add_sidebar_release_Month == "For month":
        st.header("Release Game for Month *(2006-2023)*",divider=True)
        try:
            appointment = st.slider("Select Range of Year",value=(datetime(2006, 1, 1, 0, 0), datetime(2024, 1, 1, 0, 0)))
            df_Range = df_Rg_month[(df_Rg_month['DateTime'] >= appointment[0]) & (df_Rg_month['DateTime'] <= appointment[1])]
            df_Range = df_Range.groupby(df_Range['DateTime'].dt.month_name())['Games'].sum()
        #Convert the series index to a categorical type with the order of months
            df_Range.index = pd.Categorical(df_Range.index, categories=Mont_Order, ordered=True)
        #Order by Index 
            df_Range = df_Range.sort_index()
        #calculate de AVG,Min,Max Value
            Month_MinRelease = df_Range.idxmin()
            avg_games = df_Range.mean()
            
        #Divide the layout in columns
            col1,col2,col3,col4,col5,col6 =st.columns(6)
            colums = [col1,col2,col3,col4,col5,col6]
            count=0
            
            for i in df_Range.index:
                with colums[count]:
                    delta = ((df_Range[i]- avg_games)/avg_games)*100
                    st.metric(label=i, value=round(df_Range[i],1), delta="{:0.2f}%".format(delta))
                    count+=1
                    x_month.append(df_Range[i])
                    if count == 6:
                        count=0
            
        except:
            st.write("We don have data")
        finally:
            pass
        
    #Header for the top
        st.header("Games :orange[Top 250] for Month *(2018-2023)*",divider=True)
        Top_range = st.radio("Set the Top 👇",[10,20,50,100,150,250],horizontal=True,)
        try:
        #Radio for the top
            
            
            df_TopRange_Release = df_Toprelease[df_Toprelease["#"]<=Top_range]
            df_TopRange_Release = df_TopRange_Release.groupby(df_TopRange_Release['Release'].dt.month_name()).size()

        #Convert the series index to a categorical type with the order of months
            df_TopRange_Release.index = pd.Categorical(df_TopRange_Release.index, categories=Mont_Order, ordered=True)
            #Order by Index for month
            df_TopRange_Release = df_TopRange_Release.sort_index()

        #calculate de AVG,Min,Max Value
            MonthTop_MinRelease = df_TopRange_Release.idxmin()
            avgTop_games = df_TopRange_Release.mean()

            #Divide the layout in columns
            col1_top,col2_top,col3_top,col4_top,col5_top,col6_top =st.columns(6)
            colums2 = [col1_top,col2_top,col3_top,col4_top,col5_top,col6_top]
            count_Top=0
            for i in df_TopRange_Release.index:
                with colums2[count_Top]:
                    delta = ((df_TopRange_Release[i]- avgTop_games)/avgTop_games)*100
                    st.metric(label=i, value=round(df_TopRange_Release[i],1), delta="{:0.2f}%".format(delta))
                    x_topmont.append(df_TopRange_Release[i])
                    count_Top+=1
                    if count_Top == 6:
                        count_Top=0
                    
            
        except:
            st.write("We don have data")
        
        fig2 = px.bar(df_TopRange_Release, x=df_TopRange_Release.index, y=df_TopRange_Release, text_auto=True)
        fig2 = go.Figure(data=[
            go.Bar(name='Top Month', x=df_TopRange_Release.index, y=df_TopRange_Release),
            go.Bar(name='Total Month', x=df_TopRange_Release.index, y=df_Range)
            ])
        # Change the bar mode
        fig2.update_layout(barmode='group')
        st.plotly_chart(fig2)

    if add_sidebar_release_Month == "For Year":
        df_Rg_year_ind = df_Rg_year.set_index("DateTime")
        df_Rg_year_ind["Year"] = df_Rg_year_ind.index.year
        fig = px.line(df_Rg_year_ind, x="Year", y="Games", title='Games For Year',markers=True)
        st.plotly_chart(fig)


if option=="Tags":
    st.title('All :rainbow[Tags] in Steam')
    st.dataframe(df_Tags_Steam,use_container_width=True,hide_index=True,
                 column_config=
                 {
                     "Number_Games": st.column_config.NumberColumn("Count",help="Number of Games",format="%d 🎮",)
                 })
    TopTag_range = st.radio("Set the Top 👇",[10,20,50,100,150],horizontal=True,)
    df_Tags_Steam = df_Tags_Steam.loc[:TopTag_range]
    fig3 = px.pie(df_Tags_Steam, values='Number_Games', names='Tag', title='Tags in Steam')

    st.plotly_chart(fig3)

if option=="DataFrame":
    #Header
    add_sidebar_release_Month = None
    st.title('Dataframe with the :orange[top 250] for year \n (Jan.2018-August.2023)')
    # Datafrmae Styles
    #Select the comlumns for style
    #Apply style for the Df in applymap(), you can select columns with Subset=
    #Positve and Negative Col style
  
    avg_positive = df_Toprelease["Positive"].mean()  
    avg_Negative = df_Toprelease["Negative"].mean()       
    df_Format = df_Toprelease.style.hide().applymap(style_negative,v_compare=avg_positive,props='color:red;',subset="Positive")
    df_Format = df_Format.applymap(style_positve,v_compare=avg_positive,props='color:green;',subset="Positive")
    df_Format = df_Format.applymap(style_negative,v_compare=avg_Negative,props='color:red;',subset="Negative")
    df_Format = df_Format.applymap(style_positve,v_compare=avg_Negative,props='color:green;',subset="Negative")
    #Peak Users
    final_format = {
                    "#":st.column_config.DateColumn("🏆",help="Top in the year",format="%s"),
                    "Release":st.column_config.DateColumn("📆",help="Game Release",format="%s"),
                    "Peak Users":st.column_config.NumberColumn("🏅",help="Peak Users online"),
                    "Positive":st.column_config.NumberColumn("🥰",help="Positive Comments"),
                    "Negative":st.column_config.NumberColumn("😴",help="Negative Comments"),}
    
    st.subheader('The :green[green value] is greater than average value of the column')
    st.subheader('The :red[red value] is smaller than average value of the column', divider="rainbow")
    st.dataframe(df_Format,column_config=final_format)
    with st.expander("Formula in which the Rating was created:"):
        #Lates
        st.latex("""TotalReviews =  PositiveReviews + NegativeReviews""")
        st.latex('''ReviewScore = {PositiveReviews \over NegativeReviews}''')
        st.latex('''Rating = ReviewScore - (ReviewScore-0.5)*2^-log_10 (TotalReviews + 1)''')