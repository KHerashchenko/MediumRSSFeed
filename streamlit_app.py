import streamlit as st
from streamlit.components.v1 import html
import pymongo
import webbrowser
from datetime import datetime

# MongoDB configuration
MONGODB_HOST = "node1"
MONGODB_PORT = 27017
MONGODB_DB_NAME = "rss_db"
MONGODB_COLLECTION_NAME = "general"


# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)


client = init_connection()


# Pull data from the collection.
def get_data(tag=None):
    db = client[MONGODB_DB_NAME]
    query = {}
    if tag:
        query["tag"] = tag
    items = db[MONGODB_COLLECTION_NAME].find(query)

    # Convert the "published" strings to datetime objects
    items = [(item, datetime.strptime(item["published"], "%a, %d %b %Y %H:%M:%S GMT")) for item in items]

    # Sort by the datetime objects in ascending order
    items.sort(key=lambda x: x[1], reverse=True)

    # Extract the original items without the datetime objects
    sorted_items = [item[0] for item in items]

    return sorted_items


# Sidebar for filtering by tag
tag_list = ["All", "data-science", "finance", "life", "startup"]
selected_tag = st.sidebar.selectbox("Filter by Tag", tag_list)

# Main content area
st.title("Medium Story Summaries Project")

if selected_tag == "All":
    items = get_data()
else:
    items = get_data(selected_tag)

if not items:
    st.warning("No articles found for the selected tag.")

# Define CSS styles for different elements
css = """
.field-name {
    color: #cc0000;
    font-weight: bold;
    font-size: 18px;
}

.bordered-box {
    border-radius: 5px;
    padding: 10px;
    background-color: #eeeeee;
    margin-bottom: 10px;
}

.styled-link {
    text-decoration: none;
}
"""


def open_page(url):
    open_script= """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (url)
    html(open_script)


# Use Streamlit's write method to inject the CSS
st.write("<style>" + css + "</style>", unsafe_allow_html=True)

for index, item in enumerate(items):
    # Style the title using CSS class "field-name"
    st.markdown(f'<p class="field-name">{item["title"]}</p>', unsafe_allow_html=True)

    # Style the summary using CSS class "bordered-box"
    st.markdown(f'<div class="bordered-box">{item["summary"]}</div>', unsafe_allow_html=True)

    with st.expander("Start reading"):
        st.write(item["description"])
        # Style the "Continue" link using CSS class "styled-link"
        st.markdown(f'<a class="styled-link" href="{item["link"]}">Continue 🔗</a>', unsafe_allow_html=True)

    button = st.button(item['tag'], key=f"{item['tag']}_{index}", on_click=open_page, args=(f'https://medium.com/tag/{item["tag"].replace(" ", "-")}',))

    st.markdown(f'**Published:** {item["published"]}')
    st.write("---")
