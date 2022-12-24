import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import base64

import nltk
from nltk.corpus import stopwords
from textblob import Word, TextBlob
from nltk.stem import WordNetLemmatizer





# st.title('Sentiment analysis app')

@st.experimental_memo
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img= get_img_as_base64("st.jpg")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
background-image: url("data:image/png;base64,{img}");
background-size= cover;
}}

[data-testid="stHeader"] {{
background-color: rgba(0,0,0,0);
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: red;'>Sentiment analysis app</h1>", unsafe_allow_html=True)


col1,col2 = st.columns(2)
col3,col4= st.columns(2)


start_date= col1.date_input("Enter your start date")

end_date= col2.date_input("Enter your end date")

lang= col3.selectbox('Select Language:',('en', 'es', 'it', 'fr'))

tweet= col4.text_input('enter your search tweet')

limit= st.number_input('select limit tweets',0)



generate= st.button('analyis')

# query='elon musk lang:en until:2022-10-31 since:2021-04-17'

query= '{} lang:{} until:{} since:{}'.format(tweet,lang, end_date,start_date)
tweets=[]

if generate:
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
    

    st.write(df.head())


    fig, ax= plt.subplots(1,1, figsize=(20,7))
    ax.plot(df['Date'], df['Polarity'])
    ax.set_title('polarity over time from start date to the end date', fontsize= 20)
    st.pyplot(fig)






