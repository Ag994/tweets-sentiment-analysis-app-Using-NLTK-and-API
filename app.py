import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
import streamlit as st
# import base64
# import streamlit.components.v1 as components
import altair as alt
import plotly.express as px
from plotly import io
from PIL import Image
from plotly.graph_objects import Layout

from htbuilder import div, big, h2, styles
from htbuilder.units import rem

import nltk
from nltk.corpus import stopwords
from textblob import Word, TextBlob
from nltk.stem import WordNetLemmatizer

nltk.download('omw-1.4')



# title_container = st.container()
# col1,col3 = st.columns([20,1])
# image = Image.open('twee.png')
# with title_container:
#     with col3:
#         st.image(image, width=64)
#     with col1:
#         st.title('tweets analysis app {}'.format(image))
#                 # st.markdown('<h1 style="color: purple;">Suzieq</h1>',
#                 #             unsafe_allow_html=True)

im = Image.open("twe.png")
st.set_page_config(
    page_title="tweets analysis",
    page_icon=im
)


col1, col2, col3 = st.columns([14,10,10])

with col1:
    st.write("")

with col2:
    st.image(im)

with col3:
    st.write("")

# st.image(im, width=100)

col1, col2, col3 = st.columns([3,10,3])

with col1:
    st.write("")

with col2:
    st.title('Tweets Analysis App')

with col3:
    st.write("")


# st.title('tweets analysis app')


# st.markdown("<h1 style='text-align: center; color: red;'>Sentiment analysis app</h1>", unsafe_allow_html=True)


col1,col2 = st.columns(2)
col3,col4= st.columns(2)


start_date= col1.date_input("Enter your start date")

end_date= col2.date_input("Enter your end date")

lang= col3.selectbox('Select Language:',('en', 'es', 'it', 'fr','ar'))

tweet= st.text_input('Enter your search tweet')

limit= col4.number_input('Select tweets limit',0)


def prompt_user():
  st.write("Please make sure to enter the date in the correct format when using our sentimental analysis tool.")
  st.write("Also, keep in mind that the polarity score is a value between -1 (very negative) and 1 (very positive), and the subjectivity score is a value between 0 (very objective) and 1 (very subjective).")
  st.write("Thank you for using our tool.")

prompt_user()
# query='elon musk lang:en until:2022-10-31 since:2021-04-17'

customized_button = st.markdown("""
    <style >
    div.stButton > button:first-child {
        background-color: #0099ff;
        color:#ffffff;
    }
    div.stButton > button:hover {
        background-color: #00ff00;
        color:#ffffff;
        }
    </style>""", unsafe_allow_html=True)


generate= st.button('Analyze')

query= '{} lang:{} until:{} since:{}'.format(tweet,lang, end_date,start_date)
tweets=[]

try:
    def analyze():
        for tweet in sntwitter.TwitterSearchScraper(query).get_items():
            if len(tweets) == limit:
                break
            else:
                tweets.append([tweet.date, tweet.user.username, tweet.content])

        df= pd.DataFrame(tweets, columns=['Date','Username','Content'])

        nltk.download('stopwords')
        nltk.download('wordnet')
        stop_words= set(stopwords.words('english')) | set(stopwords.words('french')) | set(stopwords.words('italian')) | \
                    set(stopwords.words('spanish'))
        custom_stop= ['RT',tweet]

        def preprocess(tweet, stopword):
            preprocess_tweet= tweet
            preprocess_tweet.replace('[^\w\s]','')
            preprocess_tweet= " ".join(word for word in preprocess_tweet.split() if word not in stop_words)
            preprocess_tweet= " ".join(word for word in preprocess_tweet.split() if word not in custom_stop)
            lemmatizer = WordNetLemmatizer()
            preprocess_tweet= " ".join(lemmatizer.lemmatize(word) for word in preprocess_tweet.split())
            return (preprocess_tweet)

        df['preprocess_tweet']= df['Content'].apply(lambda x: preprocess(x, custom_stop))

        df['Polarity']= df['Content'].apply(lambda x: TextBlob(x).sentiment[0])
        df['subjectivity']= df['Content'].apply(lambda x: TextBlob(x).sentiment[1])

        st.write("## Sentiment from the most recent ", len(df)," tweets")


        def display_dial(title, value, color):
            st.markdown(
                div(
                    style=styles(
                        text_align="center",
                        color=color,
                        padding=(rem(0.8), 0, rem(3), 0),
                    )
                )(
                    h2(style=styles(font_size=rem(0.8), font_weight=600, padding=0))(title),
                    big(style=styles(font_size=rem(3), font_weight=800, line_height=1))(
                        value
                    ),
                ),
                unsafe_allow_html=True,
            )

        # COLOR_RED = "#FF4B4B"
        COLOR_BLUE = "#1C83E1"
        COLOR_CYAN = "#00C0F2"

        polarity_color = COLOR_BLUE
        subjectivity_color = COLOR_CYAN

        a, b = st.columns(2)

        with a:
            display_dial("Avarage POLARITY", f"{df['Polarity'].mean():.2f}", polarity_color)
        with b:
            display_dial("Avarage SUBJECTIVITY", f"{df['subjectivity'].mean():.2f}", subjectivity_color
        )


        st.write(df.head())

        @st.cache
        def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')

        csv = convert_df(df)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='large_df.csv',
            mime='text/csv'
            )

        # fig, ax= plt.subplots(1,1, figsize=(20,7))
        # ax.plot(df['Date'], df['Polarity'])
        # ax.set_title('polarity over time from start date to the end date', fontsize= 20)
        # st.pyplot(fig)

        # layout = Layout(plot_bgcolor='rgba(0,0,0,0)')
        io.templates.default = 'seaborn'

        fig = px.line(
            df,
            x='Date',
            y="Polarity",
            title='polarity over time from start date to the end date',
            markers=True
            # width=600, 
            # height=400
        )
        # with col4:
        #     st.plotly_chart(fig, theme="streamlit")
        st.write(fig)


        fig1 = px.line(
            df,
            x='Date',
            y="subjectivity",
            title='subjectivity over time from start date to the end date',
            markers=True
            # width=600, 
            # height=400
        )       
        # with col6:  
        #     st.plotly_chart(fig1, use_container_width=True)
        st.write(fig1)


    if generate:
        with st.spinner("Executing..."):
            result= analyze()
        st.write(result)
        
except UnboundLocalError:
    st.error('Please enter a valid values')

    # fig.update_layout(margin={"t": 30, "b": 0})
    # fig1.update_layout(margin={"t": 30, "b": 0})

    # data_container = st.container()

    # with data_container:
    #     table,table1,table2 ,table4= st.columns((20,1,1,1))
    #     with table:
    #     # use st.dataframe instead of st.table
    #         st.plotly_chart(fig)
    #     with table2:
    #         st.plotly_chart(fig1)



    # tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])
    # with tab1:
    # Use the Streamlit theme.
    # This is the default. So you can also omit the theme argument.
    
        

    # with tab2:
    # Use the native Plotly theme.
    # fig = px.line(df, x='Date', y="Polarity", title='polarity over time from start date to the end date', template="ggplot2",
    # markers=True)
    # st.write(fig)



# components.html(
#     """
#         <a href="https://github.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" 
#         data-text="Check my cool Streamlit Web-App🎈" 
#         data-url="https://streamlit.io"
#         data-show-count="false">
#         data-size="Large" 
#         data-hashtags="streamlit,python"
#         Tweet
#         </a>
#         <script async src="https://platform.github.com/widgets.js" charset="utf-8"></script>
#     """
# )


