import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="TMDB Movie Analytics", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #101827;
    color: #FFFFFF;
}

h1, h2, h3 {
    color: #01B4E4 !important;
}

div[data-testid="stMetric"] {
    background-color: #243247;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #01B4E4;
}

div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}

div[data-testid="stMetricLabel"] {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

</style>
""", unsafe_allow_html=True)


st.title("🎬 Reel Insights: TMDB Movie Analytics")
st.write("Explore movie ratings, revenue, and genres.")

movies = pd.read_csv("cleaned_movies.csv")
st.write(movies.columns.tolist())
genres = pd.read_csv("cleaned_genres.csv")
movie_genres = pd.read_csv("cleaned_movie_genres.csv")

st.subheader("🎭 Filter Movies by Genre")
selected_genre = st.selectbox(
    "Choose a genre",
    ["All Genres"] + sorted(
        genres["genre_name"].dropna().unique().tolist()
    )
)
if selected_genre == "All Genres":
    st.dataframe(movies)
else:
    st.dataframe(
        movies.merge(movie_genres, on="movie_id")
        .merge(genres, on="genre_id")
        .query("genre_name == @selected_genre")
    )


st.subheader("📊 Movie Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Movies", len(movies))

if "vote_average" in movies.columns:
    col2.metric("Average Rating", round(movies["vote_average"].mean(), 2))
else:
    col2.metric("Average Rating", "N/A")

if "revenue" in movies.columns:
    col3.metric("Total Revenue", f"${movies['revenue'].sum():,.0f}")
else:
    col3.metric("Total Revenue", "N/A")

st.subheader("🔍 Search Movie")
search = st.text_input("Enter movie name")

if "title" in movies.columns:
    filtered = movies.copy()

    if search:
        filtered = filtered[
            filtered["title"].astype(str).str.contains(
                search, case=False, na=False
            )
        ]

    st.write("Movies found:", len(filtered))
    st.dataframe(filtered, use_container_width=True)

if "vote_average" in movies.columns:
    st.subheader("⭐ Top Rated Movies")
    top_movies = movies.nlargest(10, "vote_average")

    if "title" in top_movies.columns:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(top_movies["title"], top_movies["vote_average"])
        ax.invert_yaxis()
        ax.set_xlabel("Rating")
        st.pyplot(fig)
        plt.close(fig)

if "revenue" in movies.columns and "title" in movies.columns:
    st.subheader("💰 Top 10 Movies by Revenue")
    top_revenue = movies.nlargest(10, "revenue")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top_revenue["title"], top_revenue["revenue"])
    ax.invert_yaxis()
    ax.set_xlabel("Revenue")
    st.pyplot(fig)
    plt.close(fig)

# Genre Analysis
st.subheader("🎭 Movie Genre Analysis")

genre_data = movie_genres.merge(
    genres,
    on="genre_id",
    how="left"
)

genre_summary = genre_data.groupby("genre_name")["movie_id"].count()
genre_summary = genre_summary.sort_values(ascending=False).head(10)

st.bar_chart(genre_summary)

# Movies Released by Year
st.subheader("📅 Movies Released by Year")

movies["release_date"] = pd.to_datetime(
    movies["release_date"], errors="coerce"
)

year_counts = movies.dropna(subset=["release_date"]).copy()
year_counts["year"] = year_counts["release_date"].dt.year

year_counts = year_counts.groupby("year")["title"].count()

st.line_chart(year_counts)

# Rating Distribution
st.subheader("⭐ Movie Rating Distribution")

rating_data = movies["vote_average"].dropna()

st.bar_chart(rating_data.value_counts().sort_index())

# Most Popular Movies
st.subheader("🔥 Top 10 Most Popular Movies")

popular_movies = movies.nlargest(10, "popularity")

st.bar_chart(
    popular_movies.set_index("title")["popularity"]
)

# Budget vs Revenue
st.subheader("💰 Movie Budget vs Revenue")

budget_data = movies[
    (movies["budget"] > 0) &
    (movies["revenue"] > 0)
]

st.scatter_chart(
    budget_data,
    x="budget",
    y="revenue",
    x_label="Movie Budget",
    y_label="Movie Revenue"
)

# Movie Runtime Analysis
st.subheader("⏱️ Movie Runtime Analysis")

runtime_data = movies[
    movies["runtime"].notna() &
    (movies["runtime"] > 0)
]

st.histogram if False else None

st.bar_chart(
    runtime_data["runtime"].round(-1).value_counts().sort_index()
)
