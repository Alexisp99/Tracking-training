import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit_nested_layout

#create the page of the web app
st.set_page_config(page_title = "Training",
                   layout = "wide", 
                   )

all_exercise = pd.read_csv("exercise.csv")
df_tracking = pd.read_csv("tracking.csv")


def input_form(col1,col2):  
    dates = col1.date_input("Date").strftime("%y/%m/%d")
    training = col2.selectbox("Training",("Push", "Pull", "Legs"))
    exo = col1.selectbox("Exercise",(all_exercise[training]))
    series = col2.number_input("Series", value=3)     
    
    return dates,training,exo,series

def form(dates,training,exo,series,col11,col22,col33):
            
    col11.subheader("Weight")
    col22.subheader("Repetition")
    col33.subheader("Rest")    
    
    def change():
        #Initialize session state for data
        if "datas" not in st.session_state:
            st.session_state["datas"] = datas
        
        st.session_state["datas"] = datas["Weight"].append(weights)
        st.session_state["datas"] = datas["Repetitions"].append(repetitions)
        st.session_state["datas"] = datas["Rest"].append(rest)
        
    datas =  {"Workout":[],"Exercise": [], "Weight": [], "Repetitions":[], "Rest": [],"Date":[]}
    
    
    #Create the form input
    keys = []
    for i in range(int(series)):
        
        weights = col11.number_input("", min_value=1, key=keys, on_change=change)
        datas["Weight"].append(round(weights))
        keys.append(1)
        repetitions = col22.number_input("", min_value=1, key=keys,on_change= change)
        datas["Repetitions"].append(repetitions)
        keys.append(1)
        rest = col33.number_input("", value=60,step=30, key=keys, on_change=change)
        datas["Rest"].append(rest)
        keys.append(1)
        datas["Exercise"].append(exo)
        datas["Date"].append(dates)
        datas["Workout"].append(training)
    

    df = pd.DataFrame.from_dict(datas, orient = "index").transpose()
    return df

def button_form(df_form):
    #create a default dataframe 
    d = {"Workout": [],"Exercise" : [], "Weight": [], "Repetitions":[], "Rest": [], "Date" : []}
    df = pd.DataFrame(d)

    #Initialize session state for df_result

    if "df_result" not in st.session_state:
        st.session_state["df_result"] = df

    def concat():
        st.session_state["df_result"] = st.session_state["df_result"].append(df_form)
    
    def reset():
        st.session_state["df_result"] = df
        
    def remove():
        st.session_state["df_result"] = st.session_state["df_result"][:-1]
        
    def save():
        with open("tracking.csv", "a") as file :
            st.session_state.df_result.to_csv(file, mode="a", header=False)
            reset()
            
    
    col1,col2,col3,col4 = st.columns([1,1,1,10])
    col1.button("Next", on_click = concat)
    col2.button("Save", on_click= save)
    col3.button("Reset", on_click=reset)
    col4.button("Remove",on_click=remove)
    
def result_form():
    st.subheader("Data before sending")
    st.dataframe(st.session_state["df_result"])

def training_chart(option):
        
        scatter_chart = go.Figure()
        for exercise in all_exercise[option]:
            scatter_chart.add_trace(go.Scatter(
                x = df_tracking.query(f"Exercise == '{exercise}'")["Date"],
                y = df_tracking.query(f"Exercise == '{exercise}'")["Weight"],
                mode = "lines",
                name = exercise,
                
                showlegend=True
            ))
        
        st.write(scatter_chart) 
        
        
def daily_chart(pos,df_date):
        fig = go.Figure(data=[go.Table(
            columnwidth =[12,23,12,12,12,12],
            header=dict(values=list(df_date.columns),
                        fill_color='grey',
                        line_color = "darkslategray",
                        font = dict(color = "white", size =15),
                        align='center',
                        ),
            cells=dict(values=df_date.T.values,
                        fill_color='lightgrey',
                        line_color = "darkslategray",
                        font = dict(color = "darkslategray", size = 15),
                        height = 35,
                        align='center'))
        ])
        pos.write(fig)

def track_chart(pos):
    exercises = pos.multiselect("Exercise", all_exercise)
   
    scatter_chart = go.Figure()
    for exercise in exercises:
        scatter_chart.add_trace(go.Scatter(
            x = df_tracking.query(f"Exercise == '{exercise}'")["Date"],
            y = df_tracking.query(f"Exercise == '{exercise}'")["Weight"] ,
            mode = "lines",
            name = exercise,
            legendgroup=1,
            showlegend=True
        ))
    
    pos.write(scatter_chart)

#Create a dataframe who change dynamically with the date input
def date(col1):
    
    last_training = df_tracking["Date"][-1:]
    last_training = last_training.iloc[0]
        
    date_format = pd.to_datetime(last_training, format ="%y/%m/%d")
    
    date = col1.date_input("Choose day",value= pd.to_datetime(date_format, format="%y/%m/%d")).strftime("%y/%m/%d")
    df_date = df_tracking.loc[df_tracking["Date"]== date]
    
    return df_date




header = st.container()
dataset = st.container()

with header:
    st.title("Progress tracking")
    col10,col20 = st.columns([1,1])
    
    with col10:
        col1,col2,col3 = st.columns([1,1,2])
        col11,col22,col33,col44 = st.columns([1,1,1,1])
        
        dates,training,exo,series= input_form(col1,col2)
        df_form = form(dates,training,exo,series,col11,col22,col33)
        button_form(df_form)
        result_form()


    with col20:
        push,pull,legs = st.tabs(["Push","Pull","Legs"])
        
        with push:
            training_chart("Push")
            
        with pull:
            training_chart("Pull")
            
        with legs:
            training_chart("Legs")
    


with dataset:
    st.title("Chart")
    tab1,tab2,tab3 = st.tabs(["📈 Last training","Progress", "🗃 Data"])
    
    with tab1:
        col1,col2 = st.columns([1,6])
        dates = date(col1)
        daily_chart(col1,dates)
    
    with tab2:
        col1,col2 = st.columns(2)
        track_chart(col1)
    
    with tab3:
        col1,col2 = st.columns(2)
        col1.header("All Data")
        col1.dataframe(df_tracking)
        col2.header("Data of the day")
        col2.dataframe(dates)
        
    
  





