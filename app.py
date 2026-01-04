import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Ultimate Book Analytics Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_books_data (1).csv')
    
    def get_rating(row):
        if row['rating_four']: return 4
        if row['rating_one']: return 1
        if row['rating_three']: return 3
        if row['rating_two']: return 2
        return 5 # Assume rest are 5 stars
    
    df['rating_score'] = df.apply(get_rating, axis=1)
    return df

df = load_data()

st.sidebar.header(" Control Panel")
st.sidebar.markdown("Use these filters to update all visuals (Sync Slicers).")

# Filter 1: Price Range Slider
min_p, max_p = float(df['price'].min()), float(df['price'].max())
price_range = st.sidebar.slider("Select Price Range ($)", min_p, max_p, (min_p, max_p))

# Filter 2: Price Category Multi-select
categories = sorted(df['price_category'].unique())
selected_cat = st.sidebar.multiselect("Price Categories", categories, default=categories)

# Filter 3: Rating Selection
ratings = sorted(df['rating_score'].unique())
selected_ratings = st.sidebar.multiselect("Book Ratings", ratings, default=ratings)

filtered_df = df[
    (df['price'] >= price_range[0]) & 
    (df['price'] <= price_range[1]) &
    (df['price_category'].isin(selected_cat)) &
    (df['rating_score'].isin(selected_ratings))]

st.sidebar.info("Bookmark: Dashboard filtered for 2024 Inventory Analysis.")

if st.sidebar.button("🔄 Reset All Filters"):
    st.rerun()

st.title("📚 Comprehensive Books Insights Dashboard")
st.markdown("---")

# SECTION 1: KPIs (Key Performance Indicators)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Total Inventory", f"{len(filtered_df)} Books")
with kpi2:
    st.metric("Avg. Price", f"${filtered_df['price'].mean():.2f}")
with kpi3:
    st.metric("Highest Price", f"${filtered_df['price'].max():.2f}")
with kpi4:
    avg_len = filtered_df['title_length'].mean() if not filtered_df.empty else 0
    st.metric("Avg. Title Length", f"{int(avg_len)} Chars")

st.divider()

# SECTION 2: PRICE CATEGORY DISTRIBUTION (LOW, MEDIUM, HIGH) 
st.subheader("Price Category Analysis (Low, Medium, High)")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("Book Counts by Category")
    cat_counts = filtered_df['price_category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']
    
    fig_cat_bar = px.bar(cat_counts, x='Category', y='Count', 
                         color='Category', 
                         color_discrete_map={'Low': '#636EFA', 'Medium': '#EF553B', 'High': '#00CC96'},
                         text_auto=True)
    st.plotly_chart(fig_cat_bar, use_container_width=True)

with col_b:
    st.markdown("Price Spread within Categories")
    fig_cat_box = px.box(filtered_df, x="price_category", y="price", 
                         color="price_category",
                         color_discrete_map={'Low': '#636EFA', 'Medium': '#EF553B', 'High': '#00CC96'},
                         labels={'price_category': 'Category', 'price': 'Price ($)'})
    st.plotly_chart(fig_cat_box, use_container_width=True)

st.divider()

# SECTION 3: RATINGS & FREQUENCY
col1, col2 = st.columns(2)

with col1:
    st.subheader("Market Share by Category")
    fig_pie = px.pie(filtered_df, names='price_category', 
                     hole=0.4, 
                     color='price_category',
                     color_discrete_map={'Low': '#636EFA', 'Medium': '#EF553B', 'High': '#00CC96'})
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Ratings Distribution")
    rating_counts = filtered_df['rating_score'].value_counts().reset_index()
    rating_counts.columns = ['Rating', 'Count']
    fig_rating = px.bar(rating_counts, x="Rating", y="Count", 
                        color="Rating", color_continuous_scale='Viridis')
    st.plotly_chart(fig_rating, use_container_width=True)

st.divider()

# SECTION 4: AI INSIGHTS & LEADERBOARD 
col5, col6 = st.columns([1.5, 1])

with col5:
    st.subheader("AI Insights: Title Length vs Price Trend")
    st.info("Visualizing the correlation using OLS Linear Regression.")
    if not filtered_df.empty:
        fig_trend = px.scatter(filtered_df, x="title_length", y="price", 
                         trendline="ols", 
                         color="price_category",
                         hover_name="title",
                         labels={'title_length': 'Length of Title', 'price': 'Price ($)'})
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("No data available for AI Trendline.")

with col6:
    st.subheader("🏆 Top 10 Most Expensive")
    top_10 = filtered_df.nlargest(10, 'price')[['title', 'price']]
    fig_top = px.bar(top_10, x='price', y='title', orientation='h',
                     color='price', color_continuous_scale='Reds',
                     labels={'price': 'Price ($)', 'title': 'Title'})
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)

st.divider()

# SECTION 5: DRILL THROUGH & REPORTING 
with st.expander("🔍 Drill Through: View Detailed Raw Data"):
    st.write("Below is the filtered dataset based on your sidebar selections.")
    st.dataframe(filtered_df, use_container_width=True)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Detailed Report (CSV)",data=csv,
        file_name='final_filtered_report.csv',mime='text/csv',)

st.caption("Dashboard developed for Book Inventory Management | Data Source: cleaned_books_data.csv")