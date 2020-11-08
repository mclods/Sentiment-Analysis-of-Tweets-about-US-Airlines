import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

st.title("Sentiment Analysis of Tweets about US Airlines")
st.sidebar.title('Analyze Sentiments')

st.markdown("This application is a dashboard to analyze the Sentiment of Tweets 🐦")
st.sidebar.markdown("Analyze positive and negative mentions about Airlines on Twitter.")

DATA_URL = ("Tweets.csv")

# Cache the loaded dataset to increase speed

@st.cache(persist=True)
def load_data():
    data = pd.read_csv(DATA_URL)
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data

data = load_data()

st.sidebar.subheader("Show Random Tweet")
random_tweet = st.sidebar.radio('Sentiment', ('Positive', 'Neutral', 'Negative'))
random_tweet = random_tweet.lower()
st.sidebar.markdown(data.query('airline_sentiment == @random_tweet')[["text"]].sample(n=1).iat[0, 0])

st.sidebar.markdown("### Number of Tweets by Sentiment")
select = st.sidebar.selectbox('Visualization Type', ['Histogram', 'Pie Chart'], key='0')
sentiment_count = data['airline_sentiment'].value_counts()
sentiment_count = pd.DataFrame({'Sentiment': sentiment_count.index, 'Tweets': sentiment_count.values})

if not st.sidebar.checkbox('Hide', True):
    st.markdown("### Number of Tweets by Sentiment")
    if select == 'Histogram':
        fig = px.bar(sentiment_count,
                     x='Sentiment', 
                     y='Tweets',
                     color='Tweets',
                     height=500)
        st.plotly_chart(fig)
    else:
        fig = px.pie(sentiment_count, values='Tweets', names='Sentiment')
        st.plotly_chart(fig)

st.sidebar.subheader("When and Where are users Tweeting from ?")
hour = st.sidebar.slider("Hour of Day", 0, 23)
modified_data = data[data['tweet_created'].dt.hour == hour]
if not st.sidebar.checkbox("Close", True, key='1'):
    st.markdown("### Tweets locations based on time of day")
    st.markdown("%i tweets between %i:00 and %i:00" %(len(modified_data), hour, (hour+1)%24))
    st.map(modified_data)
    if st.sidebar.checkbox("Show Raw Data", False):
        st.write(modified_data)

st.sidebar.subheader("Breakdown Airline Tweets by Sentiment")
choice = st.sidebar.multiselect('Pick Airlines', ('American', 'US Airways', 'Delta', 'Southwest', 'United', 'Virgin America'), key='2')

if len(choice) > 0:
    choice_data = data[data.airline.isin(choice)]
    fig_choice = px.histogram(choice_data, 
                              x='airline',
                              y='airline_sentiment',
                              histfunc='count',
                              color='airline_sentiment',
                              facet_col='airline_sentiment',
                              labels={'airline_sentiment': 'Tweets'},
                              height=600,
                              width=800)
    st.plotly_chart(fig_choice)

st.sidebar.markdown("### Word Cloud")
word_sentiment = st.sidebar.radio("Select Sentiment for Word Cloud:", ('Positive', 'Neutral', 'Negative'))

if not st.sidebar.checkbox("Close", True, key='3'):
    st.markdown("### Word Cloud for %s Sentiment" % (word_sentiment))
    df = data[data['airline_sentiment'] == word_sentiment.lower()]
    words = ' '.join(df['text'])
    processed_words = ' '.join(word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT')
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', height=640, width=800).generate(processed_words)
    plt.imshow(wordcloud)
    plt.xticks([])
    plt.yticks([])
    st.pyplot(plt)
