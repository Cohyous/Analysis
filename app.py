import altair as alt
import streamlit as st
from streamlit_navigation_bar import st_navbar
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
#from st_files_connection import FilesConnection
#import geopandas as gpd
import gc
import json
from datetime import datetime

current_year = datetime.now().year
st.set_page_config(layout="wide")

@st.cache_data
def get_file(name):
  for i in st.session_state.uploaded_files:
    if i.name==name:
      return i





@st.cache_data
def data_loader(year,typ):
  if typ=="ter":
    #path="./ter/TER-FY"+str(year%100)+".xlsx"
    path=get_file("TER-FY"+str(year%100)+".xlsx")
    df=pd.read_excel(path,usecols=["QR Code","Part Number","Part Desc.","State Name","District Name","Month"])
    df[df.select_dtypes("object").columns] = df[df.select_dtypes("object").columns].apply(lambda x: x.str.upper())
    df["State Name"]=df["State Name"].replace({"UP1":"UTTAR PRADESH","UP2":"UTTAR PRADESH","UP":"UTTAR PRADESH"})
    oils=["SBU0019","SBU0020","SBU0021","SBU0032","SBU0056D","SBU0033","SBU0033","TGOP9001","SBU0055","SBU0039"]
    df["Category"]=df["Part Number"].map(lambda x:"Oil" if x in oils else "Part")
  elif typ=="sec":
    #path="./sec/SEC-FY"+str(year%100)+".xlsx"
    path=get_file("SEC-FY"+str(year%100)+".xlsx")

    key=['Sale Qty','Item Code','Item Description','State','Voucher Date']
    df=pd.read_excel(path,sheet_name=0,usecols=key)
    df['Voucher Date'] = df['Voucher Date'].dt.strftime('%B')
    df['Item Description']=df['Item Description'].apply(lambda x : str(x).split("-")[0])
    val=["QR Code","Part Number","Part Desc.","State Name","Month"]
    df.rename(columns=dict(zip(key,val)), inplace=True)
    df[df.select_dtypes("object").columns] = df[df.select_dtypes("object").columns].apply(lambda x: x.str.upper())
    df["State Name"]=df["State Name"].replace({"UP1":"UTTAR PRADESH","UP2":"UTTAR PRADESH","UP":"UTTAR PRADESH"})
    oils=["SBU0019","SBU0020","SBU0021","SBU0032","SBU0056D","SBU0033","SBU0033","TGOP9001","SBU0055","SBU0039"]
    df["Category"]=df["Part Number"].map(lambda x:"Oil" if x in oils else "Part")
  elif typ=="pri":
    #path="./pri/PRI-FY"+str(year%100)+".xlsx"
    path=get_file("PRI-FY"+str(year%100)+".xlsx")

    key=['Qty','Part No.','Part Desc','State','Month']
    df=pd.read_excel(path,sheet_name=0,usecols=key)
    df['Month'] = df['Month'].dt.strftime('%B')
    df[df.select_dtypes("object").columns] = df[df.select_dtypes("object").columns].apply(lambda x: x.str.upper())
    replace={"AP":"ANDHRA PRADESH","AS":"ASSAM","BH":"BIHAR","CHH":"CHHATTISGARH","GJ":"GUJARAT",
         "HP":"HIMACHAL PRADESH","HR":"HARYANA","JH":"JHARKHAND","KA":"KARNATAKA","MH":"MAHARASHTRA",
         "MP":"MADHYA PRADESH","OD":"ODISHA","PB":"PUNJAB","RJ":"RAJASTHAN","RJ1":"RAJASTHAN",
         "RJ2":"RAJASTHAN","TN":"TAMIL NADU","TS":"TELANGANA","WB":"WEST BENGAL","UP1":"UTTAR PRADESH","UP2":"UTTAR PRADESH","UP":"UTTAR PRADESH"}
    df["State"]=df["State"].replace(replace)

    val=["QR Code","Part Number","Part Desc.","State Name","Month"]
    df.rename(columns=dict(zip(key,val)), inplace=True)
    oils=["SBU0019","SBU0020","SBU0021","SBU0032","SBU0056D","SBU0033","SBU0033","TGOP9001","SBU0055","SBU0039"]
    df["Category"]=df["Part Number"].map(lambda x:"Oil" if x in oils else "Part")
  return df

def create_line_chart(df1, df2, year1, year2):
    # Concatenate the DataFrames and add a year column
    df_combined = pd.concat([
        df1.assign(year=str(year1)),
        df2.assign(year=str(year2))
    ])

    # Display the line chart in Streamlit
    st.line_chart(df_combined, x='Month', y='QR Code', color='year')


@st.cache_data
def grouper(df,g,sort_month,ag):
  k=df.groupby(g).agg(ag).reset_index()
  if sort_month:
    month_order = ['APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER', 'JANUARY', 'FEBRUARY', 'MARCH']
    # Convert the 'Months' column to a categorical type with the custom order
    k['Month'] = pd.Categorical(k['Month'], categories=month_order, ordered=True)

    # Sort the DataFrame by the 'Months' column
    #k = k.sort_values('Month').reset_index(drop=True)
  return k

#@st.cache_data
def line(df1,df2,x,y,xlabel,ylabel,leg):
  cat=pd.concat([df1.assign(Type=str(leg[0])),df2.assign(Type=str(leg[1]))]) # Change year to numeric
  order= ['APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER', 'JANUARY', 'FEBRUARY', 'MARCH']
  alt.themes.enable("dark")

  line_chart = alt.Chart(cat).mark_line(point=True).encode(
        alt.X(x, sort=order, title=xlabel),
        alt.Y(y, title=ylabel),
        color=alt.Color('Type', title='Type'),
        tooltip=[y, 'Type']
    ).properties(
        width=650
    )

    # Add annotations
  text_chart = line_chart.mark_text(
        align='left',
        baseline='middle',
        dx=5,  # Adjust the position of the text label
    ).encode(
        text=y,  # Display the value of 'y' on the line
    )

    # Combine the line chart and text chart
  combined_chart = line_chart + text_chart

  return combined_chart.interactive()






# Example usage:
# Replace df with your actual data and provide yearx and yeary if needed
# fig = map(df, y="YourColumn", change=True, yearx=2020, yeary=2021)
# fig.show()



#@st.cache_data
def map(df,y="QR Code",change=None,loc="State Name"):
  if loc=="State Name":
    gj="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    fkid= 'properties.ST_NM'
    df[df.select_dtypes("object").columns] = df[df.select_dtypes("object").columns].apply(lambda x: x.str.title())

  elif loc=="District Name":
    gj = json.load(open("india_district (1).geojson", 'r'))
    #gj="/content/drive/MyDrive/Colab Notebooks/data/india_district.geojson"
    fkid= 'properties.NAME_2'
    #gdf=gpd.read_file("/content/output.geojson")
    #mdf=gdf["dtname"]
    #df[loc]=fuzzy_string_matching(df[loc],mdf)
    df[df.select_dtypes("object").columns] = df[df.select_dtypes("object").columns].apply(lambda x: x.str.title())

    li3=['Kasganj','Sri Potti Sriramulu Nellore','Thoothukkudi','Khargone (West Nimar)',
    'Bangalore','Ramanagara','Chikkaballapura','Tirunelveli','Janjgir - Champa','Anugul','Krishnagiri','Paschim Medinipur','Yamunanagar',
    'Yadgir','Sant Ravidas Nagar (Bhadohi)','Khandwa (East Nimar)','Ahmadnagar','Rajnandgaon','Visakhapatnam',
    'Rangareddy','Kanpur Nagar','Mahrajganj','Dohad','Gadchiroli','Kendujhar','Alirajpur','Kaimur (Bhabua)','Jajapur',
    'Shrawasti','Aurangabad Bh','Narsimhapur','Kamrup Metropolitan','Y.S.R.','Uttar Bastar Kanker','Kabeerdham','Jagatsinghapur',
    'Tiruppur','Kodarma','Tiruchirappalli','Siddharthnagar','Arwal','Kheri','Nabarangapur', 'Viluppuram','Palwal',
    'Andamans','Udalguri','Bargarh','Subarnapur','Morigaon','Sonipat', 'Hazaribagh','Dakshin Bastar Dantewada','Imphal East','Vijayanagara', 'Hardwar','Tarn Taran']
    li4=["Etah","Nellore","Thoothukudi","West Nimar","Bangalore Urban","Bangalore Rural","Chikkaballapura","Tirunelveli Kattabo",
    "Janjgir-Champa","Angul","Krishnagiri","West Midnapore","Yamuna Nagar","Yadgir","Sant Ravi Das Nagar","East Nimar","Ahmednagar",
    "Raj Nandgaon","Vishakhapatnam","Rangareddi","Kanpur","Maharajganj","Dahod","Garhchiroli","Keonjhar",
    "Alirajpur","Bhabua","Jajpur","Shravasti","Aurangabad","Narsinghpur","Kamrup","Cuddapah","Kanker","Kawardha",
    "Jagatsinghapur","Tiruppur","Koderma","Tiruchchirappalli","Siddharth Nagar","Arwal","Lakhimpur Kheri","Nabarangpur"
    ,"Villupuram","Palwal","Andaman and Nicobar","Udalguri","Garhwa","Sonepur","Marigaon","Sonepat","Hazaribag","Dantewada",
    "East Imphal","Vijayanagara","Haridwar","Tarn Taran"]
    df[loc]=df[loc].replace(dict(zip(li3,li4)))

  if change ==1:
    cd=[loc,"QR Code"+str(yearx),"QR Code"+str(yeary), y]
    ht=f"{loc}: %{{customdata[0]}}<br>{yearx} Value: %{{customdata[1]:.2f}}<br>{yeary} Value: %{{customdata[2]:.2f}}<br>% change: %{{customdata[3]:.2f}}"

    colors = px.colors.diverging.BrBG
    mp=0
  elif change ==2:
    cd=[loc,"QR Codepart","QR Codeoil", y]
    ht=f"{loc}: %{{customdata[0]}}<br> Parts: %{{customdata[1]:.2f}}<br>Oil: %{{customdata[2]:.2f}}<br> Ratio: %{{customdata[3]:.2f}}"
    colors = px.colors.diverging.BrBG
    mp=1

  else:
    cd=[loc, y]
    ht=loc+": %{customdata[0]}<br>Value: %{customdata[1]:.2f}"
    colors="blues"
    mp=None


  fig = px.choropleth(
    df,
    geojson=gj,
    featureidkey=fkid,
    locations=loc,
    color=y,
    color_continuous_scale=colors,
    color_continuous_midpoint=mp,
    custom_data=cd
  )
  fig.update_layout(
    width=1000,  # Set width to 800 pixels
    height=600 # Set height to 600 pixels

  )

  fig.update_geos(bgcolor='black',fitbounds="locations", visible=False,
  projection_type="mercator",projection_scale=4,showcoastlines=True)
  fig.update_traces(
    hovertemplate=ht,
    selector=dict(type='choropleth')

  )
  #st.write(df)
  st.plotly_chart(fig)
@st.cache_data
def heat(g,res,v="QR Code"): #g=grouper(test,["Part Number","State Name"],False,"count")

  g = g.fillna(0)
  g=g[g["Part Number"].isin(res["Part Number"].iloc[:15].tolist())]
  #st.write(g,g['Part Number'].unique(),res["Part Number"].iloc[:15])
  fig = px.imshow(g.pivot(index='Part Number', columns='State Name', values=v).fillna(0),
                  color_continuous_scale="blues",
                  labels=dict(x="State", y="Product Name", color="Value"),
                  text_auto=True
                  )



  fig.update_layout(
    width=1500,  # Set width to 800 pixels
    height=600 # Set height to 700 pixels
  )
  fig.update_yaxes(scaleanchor="x",scaleratio=1,constrain="domain",range=[0, len(g['Part Number'].unique())])  # Set x-axis range
  fig.update_xaxes(scaleanchor="y",scaleratio=2,constrain="domain",range=[0, len(g['State Name'].unique())])   # Set y-axis range
  st.plotly_chart(fig)
@st.cache_data
def get(g1,g2,value_column="QR Code",thr=None):#g1-this year grouper on parts alone
  if thr:
    g1=g1[g1[value_column]>thr]
    g2=g2[g2[value_column]>thr]
  top_g1=g1[["Part Number","QR Code"]].nlargest(15,columns="QR Code")
  bot_g1=g1[["Part Number","QR Code"]].nsmallest(15,columns="QR Code")

  merged_df = pd.merge(g1,g2, on='Part Number', suffixes=('_this', '_prev'))

  # Calculate percentage change
  merged_df['% Change'] = (merged_df[f'{value_column}_this'] - merged_df[f'{value_column}_prev']) / merged_df[f'{value_column}_prev'] * 100

  # Sort by percentage change
  merged_df.sort_values('% Change', inplace=True)

  # Select and rename relevant columns
  result_df = merged_df[['Part Number', f'{value_column}_prev', f'{value_column}_this', '% Change']]
  result_df.rename(columns={f'{value_column}_prev': f'{value_column} (Prev Year)',
                              f'{value_column}_this': f'{value_column} (This Year)'}, inplace=True)

  return top_g1,bot_g1,result_df[result_df["% Change"]>0].iloc[::-1] ,result_df[result_df["% Change"]<=0]
@st.cache_data
def rt(g,x,y):#x-statename partnumber y-qr code
  g[y] = g[y].astype(int)  # Convert to standard Python integer
  #st.write(g)
  st.dataframe(g.sort_values(y,ascending=False),
              column_order=(x,y),
              hide_index=True,
              width=800,
              height=630,
              column_config={
                x: st.column_config.TextColumn(
                    x,
                ),
                y: st.column_config.ProgressColumn(
                    y,
                    format="%f",
                    min_value=0,
                    max_value=max(g[y]),

                  )}
              )

####################################################################################################
page = st_navbar(["Tertiary", "Secondary", "Primary", "Search", "About"],options={"use_padding":False,
"hide_nav":False})
alt.themes.enable("dark")
if 'yearx'  in st.session_state:
    yearx=st.session_state['yearx']
if 'yeary'  in st.session_state:
    yeary=st.session_state['yeary']
with st.sidebar:
  st.header("Configure")
  with st.form("entry_form"):
      # Select box
      #conn = st.connection('local', type=FilesConnection)
      #file_contents = conn.read("/content/hello.txt.txt", input_format='text')
      #st.write(file_contents)
      uploaded_files = st.file_uploader("Choose Excel files", accept_multiple_files=True)

      options = [i for i in range(current_year,current_year-11,-1)]
      yearx = st.selectbox("Select a year", options,key="box1")
      yeary = st.selectbox("Select a year", options,key="box2")

      submit = st.form_submit_button("Submit")
if submit:
  st.session_state['yearx'] = yearx
  st.session_state['yeary'] = yeary
  st.session_state['uploaded_files'] = uploaded_files

if page in ["Tertiary","Secondary", "Primary"] and 'yearx'  in st.session_state and 'yeary'  in st.session_state:
  if page=="Tertiary":
    sel="ter"
    ag="count"
  elif page=="Secondary":
    sel="sec"
    ag="sum"
  elif page=="Primary":
    sel="pri"
    ag="sum"
  col = st.columns((2,1), gap='medium')
  with col[0]:
    st.markdown('#### Total Sales')
    tab1, tab2, tab3 = st.tabs(["FY-"+str(yearx%100), "Avg %Change", "Parts/Oil"])

    with tab1:
      st.header("FY-"+str(yearx%100))
      df=grouper(data_loader(yearx,sel),"State Name",False,ag)
      #st.write(df)
      map(df)
    with tab2:
      st.header("Avg %Change")
      df=grouper(test:=data_loader(yeary,sel),"State Name",False,ag)
      d2=grouper(test2:=data_loader(yearx,sel),"State Name",False,ag)
      k=pd.merge(d2,df, on='State Name', suffixes=(yearx,yeary))
      k["QR Code"+str(yearx)] = k["QR Code"+str(yearx)]/test2["Month"].nunique()
      k["QR Code"+str(yeary)] = k["QR Code"+str(yeary)]/(test["Month"].nunique())
      #st.write(k,k.columns)
      k["% change"]=((k["QR Code"+str(yearx)]-k["QR Code"+str(yeary)])/k["QR Code"+str(yeary)])*100
      #st.write(df)
      #st.write(d2)
      map(k,"% change",1)
    with tab3:
      st.header("Ratio")
      d=data_loader(yearx,sel)
      d=d[d["Category"]=="Part"]
      g=grouper(d,"State Name",False,ag)
      d2=data_loader(yearx,sel)
      d2=d2[d2["Category"]=="Oil"]
      g2=grouper(d2,"State Name",False,ag)
      k=pd.merge(g,g2, on='State Name', suffixes=("part","oil"))
      k["QR Code"]=k["QR Codepart"]/k["QR Codeoil"]

      map(k,change=2)
  


    del df,d2,k,d,g2
    gc.collect()
    df1=grouper(data_loader(yearx,sel),"Month",True,ag)
    df2=grouper(data_loader(yeary,sel),"Month",True,ag)

    st.markdown("#### Month Wise Sales")
    #st.write(df2)s
    tabs=st.tabs(["Combined","Parts/Oil"])
    with tabs[0]:
      st.write(line(df1,df2,"Month","QR Code","Month","Scan",[yearx,yeary]))
    with tabs[1]:
      df1=data_loader(yearx,sel)
      df1=df1[df1["Category"]=="Part"]
      g=grouper(df1,"Month",True,ag)
      df2=data_loader(yearx,sel)
      df2=df2[df2["Category"]=="Oil"]
      g2=grouper(df2,"Month",True,ag)
      st.write(line(g,g2,"Month","QR Code","Month","Scan",["Part","Oil"]))
    #fig = px.pie(df, values='tip', names='day')
    del df1,g,df2,g2
    gc.collect()
    df=grouper(data_loader(yearx,sel),"Category",False,ag)
    colors = ['mediumturquoise', 'darkorange'][::-1]
    st.markdown("#### Part-Oil Distribution")
    fig = go.Figure(data=[go.Pie(
        labels=df['Category'],
        values=df['QR Code'],
        marker=dict(colors=colors, line=dict(color='#000000', width=2)),
        hoverinfo='label+percent',
        textinfo='value',
        textfont_size=20
    )])

    #fig = px.pie(df, values='QR Code', names='Category', title='Category')
    st.plotly_chart(fig)
    del df

    #fig = px.pie(df, values='oil', names='part', title='Oil Distribution')

  with col[1]:
    st.markdown('#### Top States')


    g=grouper(data_loader(yearx,sel),"State Name",False,ag)[["State Name","QR Code"]]
    rt(g,"State Name","QR Code")


    st.markdown('#### Top Parts')
    rtabs=st.tabs(["Combined","Parts", "Oil"])
    with rtabs[0]:
      g=grouper(data_loader(yearx,sel),"Part Number",False,ag)[["Part Number","QR Code"]]
      rt(g,"Part Number","QR Code")
    with rtabs[1]:
      df1=data_loader(yearx,sel)
      df1=df1[df1["Category"]=="Part"]
      g=grouper(df1,"Part Number",False,ag)[["Part Number","QR Code"]]
      rt(g,"Part Number","QR Code") if len(g)>0 else st.write("No Part")
    with rtabs[2]:
      df1=data_loader(yearx,sel)
      df1=df1[df1["Category"]=="Oil"]
      g=grouper(df1,"Part Number",False,ag)[["Part Number","QR Code"]]
      rt(g,"Part Number","QR Code") if len(g)>0 else st.write("No Oil")

  del df1,g
  gc.collect()

  res=get(grouper(data_loader(yearx,sel),["Part Number"],False,ag),
  grouper(data_loader(yeary,sel),["Part Number"],False,ag),thr=30)
  #st.write(res)
  st.markdown("#### Heat Map")
  heat_tab1, heat_tab2 = st.tabs(["Best Performing", "Poor Performing"])
  with heat_tab1:
    heat(grouper(data_loader(yearx,"ter"),["Part Number","State Name"],False,"count"),res[0])
  with heat_tab2:
    heat(grouper(data_loader(yearx,"ter"),["Part Number","State Name"],False,"count"),res[1])


  #st.write("Selected Option:",yearx,yeary)




#$$$$$$$$
elif page =="Search" and "yearx"  in st.session_state and "yeary"  in st.session_state:
  text_search = st.text_input("Search Parts or States", value="").upper()
  #st.write(text_search)
  d_ter_x=data_loader(yearx,"ter")
  d_ter_y=data_loader(yeary,"ter")
  d_sec_x=data_loader(yearx,"sec")
  d_sec_y=data_loader(yeary,"sec")
  d_pri_x=data_loader(yearx,"pri")
  d_pri_y=data_loader(yeary,"pri")
  if text_search in d_ter_x["Part Number"].unique():

    dtx=d_ter_x[d_ter_x["Part Number"]==text_search]
    dsx=d_sec_x[d_sec_x["Part Number"]==text_search]
    dpx=d_pri_x[d_pri_x["Part Number"]==text_search]
    dty=d_ter_y[d_ter_y["Part Number"]==text_search]
    dsy=d_sec_y[d_sec_y["Part Number"]==text_search]
    dpy=d_pri_y[d_pri_y["Part Number"]==text_search]
    st.title(text_search+" - "+d_ter_x[d_ter_x["Part Number"]==text_search]["Part Desc."].iloc[0])
    del d_pri_x,d_sec_x,d_ter_x,d_pri_y,d_ter_y,d_sec_y
    gc.collect()
    col = st.columns((1,1), gap='medium')
    with col[0]:
      st.markdown("#### State Wise Sales")
      mtabs=st.tabs(["Tertiary","Secondary","Primary"])

      with mtabs[0]:
        df=grouper(dtx,"State Name",False,"count")
        map(df)
      with mtabs[1]:
        df=grouper(dsx,"State Name",False,"sum")
        map(df)
      with mtabs[2]:
        df=grouper(dpx,"State Name",False,"sum")
        map(df)
    with col[1]:
      st.markdown("#### Month Wise Sales")
      ltabs=st.tabs(["Tertiary","Secondary","Primary"])
      with ltabs[0]:
        ag="count"
        df1=grouper(dtx,"Month",True,ag)
        df2=grouper(dty,"Month",True,ag)
        st.write(line(df1,df2,"Month","QR Code","Month","Scan",[yearx,yeary]))

      with ltabs[1]:
        ag="sum"
        df1=grouper(dsx,"Month",True,ag)
        df2=grouper(dsy,"Month",True,ag)
        st.write(line(df1,df2,"Month","QR Code","Month","Scan",[yearx,yeary]))
      with ltabs[2]:
        ag="sum"
        df1=grouper(dpx,"Month",True,ag)
        df2=grouper(dpy,"Month",True,ag)
        st.write(line(df1,df2,"Month","QR Code","Month","Scan",[yearx,yeary]))



  elif text_search in d_ter_x["State Name"].unique():
    dtx=d_ter_x[d_ter_x["State Name"]==text_search]
    dsx=d_sec_x[d_sec_x["State Name"]==text_search]
    dpx=d_pri_x[d_pri_x["State Name"]==text_search]
    dty=d_ter_y[d_ter_y["State Name"]==text_search]
    dsy=d_sec_y[d_sec_y["State Name"]==text_search]
    dpy=d_pri_y[d_pri_y["State Name"]==text_search]
    cols=st.columns([2,1])
    with cols[0]:


      del d_pri_x,d_sec_x,d_ter_x,d_pri_y,d_ter_y,d_sec_y
      gc.collect()
      st.markdown("#### District Wise Sales")##################
      spart=st.text_input("select Part", value="").upper()
      if spart in dtx["Part Number"].unique():
        st.write(spart+" - "+dtx[dtx["Part Number"]==spart]["Part Desc."].iloc[0])
        dtx2=dtx[dtx["Part Number"]==spart]
        dsx2=dsx[dsx["Part Number"]==spart]
        dpx2=dpx[dpx["Part Number"]==spart]
        dty2=dty[dty["Part Number"]==spart]
        dsy2=dsy[dsy["Part Number"]==spart]
        dpy2=dpy[dpy["Part Number"]==spart]
      else:
        st.write("No match found")
        dtx2=dtx
        dsx2=dsx
        dpx2=dpx
        dty2=dty
        dsy2=dsy
        dpy2=dpy
      
      mtabs3=st.tabs(["Tertiary","Secondary","Primary"])
      with mtabs3[0]:
        mtabs4=st.tabs(["FY-"+str(yearx%100), "Avg %Change", "Parts/Oil"])
        with mtabs4[0]:
          map(grouper(dtx2,"District Name",False,"count"),loc="District Name")########
        with mtabs4[1]:
          df=grouper(dty2,"District Name",False,"count")
          d2=grouper(dtx2,"District Name",False,"count")
          k=pd.merge(d2,df, on='District Name', suffixes=(yearx,yeary))
          k["QR Code"+str(yearx)] = k["QR Code"+str(yearx)]/dtx2["Month"].nunique()
          k["QR Code"+str(yeary)] = k["QR Code"+str(yeary)]/(dty2["Month"].nunique())
          #st.write(k,k.columns)
          k["% change"]=((k["QR Code"+str(yearx)]-k["QR Code"+str(yeary)])/k["QR Code"+str(yeary)])*100
          #st.write(df)
          #st.write(d2)
          map(k,"% change",1,loc="District Name")
        with mtabs4[2]:

          g=grouper(dtx[dtx["Category"]=="Part"],"District Name",False,"count")

          g2=grouper(dtx[dtx["Category"]=="Oil"],"District Name",False,"count")
          k=pd.merge(g,g2, on='District Name', suffixes=("part","oil"))
          k["QR Code"]=k["QR Codepart"]/k["QR Codeoil"]
          #st.write(mtabs4[2])
          map(k,change=2,loc="District Name")


      with mtabs3[1]:
        """mtabs4=st.tabs(["FY-"+str(yearx%100), "Avg %Change", "Parts/Oil"])
        with mtabs4[0]:
          map(grouper(dsx2,"District Name",False,"sum"),loc="District Name")########
        with mtabs4[1]:
          df=grouper(dsy2,"District Name",False,"sum")
          d2=grouper(dsx2,"District Name",False,"sum")
          k=pd.merge(d2,df, on='District Name', suffixes=(yearx,yeary))
          k["QR Code"+str(yearx)] = k["QR Code"+str(yearx)]/dsx2["Month"].nunique()
          k["QR Code"+str(yeary)] = k["QR Code"+str(yeary)]/(dsy2["Month"].nunique())
          #st.write(k,k.columns)
          k["% change"]=((k["QR Code"+str(yearx)]-k["QR Code"+str(yeary)])/k["QR Code"+str(yeary)])*100
          #st.write(df)
          #st.write(d2)
          map(k,"% change",1,loc="District Name")
        with mtabs4[2]:

          g=grouper(dsx[dsx["Category"]=="Part"],"District Name",False,"sum")

          g2=grouper(dsx[dsx["Category"]=="Oil"],"District Name",False,"sum")
          k=pd.merge(g,g2, on='District Name', suffixes=("part","oil"))
          k["QR Code"]=k["QR Codepart"]/k["QR Codeoil"]
          #st.write(mtabs4[2])
          map(k,change=2,loc="District Name")"""

      with mtabs3[2]:
        """mtabs4=st.tabs(["FY-"+str(yearx%100), "Avg %Change", "Parts/Oil"])
        with mtabs4[0]:
          map(grouper(dpx2,"District Name",False,"sum"),loc="District Name")########
        with mtabs4[1]:
          df=grouper(dpy2,"District Name",False,"sum")
          d2=grouper(dpx2,"District Name",False,"sum")
          k=pd.merge(d2,df, on='District Name', suffixes=(yearx,yeary))
          k["QR Code"+str(yearx)] = k["QR Code"+str(yearx)]/dpx2["Month"].nunique()
          k["QR Code"+str(yeary)] = k["QR Code"+str(yeary)]/(dpy2["Month"].nunique())
          #st.write(k,k.columns)
          k["% change"]=((k["QR Code"+str(yearx)]-k["QR Code"+str(yeary)])/k["QR Code"+str(yeary)])*100
          #st.write(df)
          #st.write(d2)
          map(k,"% change",1,loc="District Name")
        with mtabs4[2]:

          g=grouper(dpx[dpx["Category"]=="Part"],"District Name",False,"sum")

          g2=grouper(dpx[dpx["Category"]=="Oil"],"District Name",False,"sum")
          k=pd.merge(g,g2, on='District Name', suffixes=("part","oil"))
          k["QR Code"]=k["QR Codepart"]/k["QR Codeoil"]
          #st.write(mtabs4[2])
          map(k,change=2,loc="District Name")"""
      
##########

      st.markdown("#### Month Wise Sales")
      ltabs2=st.tabs(["Tertiary","Secondary","Primary"])

      with ltabs2[0]:
        ag="count"
        df1=grouper(dtx,"Month",True,ag)
        df2=grouper(dty,"Month",True,ag)
        st.write(line(df1,df2,"Month","QR Code","Month","Scan",[yearx,yeary]))
      with ltabs2[1]:
        ag="sum"
        df1=grouper(dsx,"Month",True,ag)
        df2=grouper(dsy,"Month",True,ag)
        st.write(line(df1,df2,"Month","QR Code","Month","Scan",[yearx,yeary]))
      with ltabs2[2]:
        ag="sum"
        df1=grouper(dpx,"Month",True,ag)
        df2=grouper(dpy,"Month",True,ag)
        st.write(line(df1,df2,"Month","QR Code","Month","Scan",[yearx,yeary]))
      colors = ['mediumturquoise', 'darkorange'][::-1]
      df=grouper(dtx,"Category",False,"count")
      st.markdown("#### Part-Oil Distribution")
      fig = go.Figure(data=[go.Pie(
          labels=df['Category'],
          values=df['QR Code'],
          marker=dict(colors=colors, line=dict(color='#000000', width=2)),
          hoverinfo='label+percent',
          textinfo='value',
          textfont_size=20
      )])

      #fig = px.pie(df, values='QR Code', names='Category', title='Category')
      st.plotly_chart(fig)
    with cols[1]:
      st.markdown("#### Top Parts")
      rtabs=st.tabs(["Combined","Parts", "Oil"])
      with rtabs[0]:
        ag="count"
        g=grouper(dtx,"Part Number",False,ag)[["Part Number","QR Code"]]
        rt(g,"Part Number","QR Code")
      with rtabs[1]:
        df1=dtx
        df1=df1[df1["Category"]=="Part"]
        g=grouper(df1,"Part Number",False,ag)[["Part Number","QR Code"]]
        rt(g,"Part Number","QR Code") if len(g)>0 else st.write("No Part")
      with rtabs[2]:
        df1=dtx
        df1=df1[df1["Category"]=="Oil"]
        g=grouper(df1,"Part Number",False,ag)[["Part Number","QR Code"]]
        rt(g,"Part Number","QR Code") if len(g)>0 else st.write("No Oil")
      del dtx,dpx,dsx,dsy,dpy,dty
      gc.collect()



  else:
    st.write("No match found")




elif page=="About":
  st.markdown("#### Made by Koushik for Tafe")
else:
  st.title("<= Please upload the files")





      #df1=grouper(data_loader(2025,"ter"),"Month",True,"count")
      #df2=grouper(data_loader(2024,"ter"),"Month",True,"count")

      #st.write(df1)
      #st.write(df2)
      #st.write(line(df1,df2,"Month","QR Code","Month","Scans"))


  