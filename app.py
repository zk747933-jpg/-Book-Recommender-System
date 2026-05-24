import streamlit as st
import pickle
import numpy as np
import os

# Page config
st.set_page_config(
    page_title="Book Recommender",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Book Recommender System")
st.subheader("Search and get book recommendations")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Safe loader (improved)
def load_pickle(filename):
    try:
        path = os.path.join(BASE_DIR, filename)

        if not os.path.exists(path):
            st.error(f"❌ {filename} NOT FOUND")
            st.stop()

        with open(path, 'rb') as file:
            data = pickle.load(file)

        return data

    except ModuleNotFoundError as e:
        st.error("❌ Dependency error while loading pickle file")
        st.error(str(e))
        st.stop()

    except Exception as e:
        st.error(f"❌ Error loading {filename}")
        st.error(str(e))
        st.stop()


# Load files
popular_df = load_pickle("popular.pkl")
pt = load_pickle("pt.pkl")
books = load_pickle("books.pkl")
similarity_scores = load_pickle("similarity_scores.pkl")


# Recommendation function (safe version)
def recommend(book_name):
    data = []

    if book_name not in pt.index:
        return []

    index = np.where(pt.index == book_name)[0][0]

    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    for i in similar_items:

        try:
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            temp_df = temp_df.drop_duplicates('Book-Title')

            if temp_df.empty:
                continue

            item = [
                temp_df['Book-Title'].values[0],
                temp_df['Book-Author'].values[0],
                temp_df['Image-URL-M'].values[0]
            ]

            data.append(item)

        except Exception:
            continue

    return data


# Search box
book_list = pt.index.tolist()

selected_book = st.selectbox(
    "Search Book",
    book_list,
    index=None,
    placeholder="Type or select a book..."
)


# Recommend button
if st.button("Recommend"):

    if selected_book:

        results = recommend(selected_book)

        st.subheader("📖 Recommended Books")

        if len(results) == 0:
            st.warning("No recommendations found.")
        else:
            cols = st.columns(5)

            for idx, book in enumerate(results):

                with cols[idx]:

                    st.image(book[2])
                    st.markdown(f"**{book[0]}**")
                    st.caption(book[1])

    else:
        st.warning("Please select a book first")


st.markdown("---")

st.subheader("🔥 Top Popular Books")

cols = st.columns(5)

for i in range(min(10, len(popular_df))):

    with cols[i % 5]:

        st.image(popular_df['Image-URL-M'].values[i])
        st.write(popular_df['Book-Title'].values[i])
        st.caption(popular_df['Book-Author'].values[i])
