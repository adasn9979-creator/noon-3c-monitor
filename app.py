import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 页面配置
st.set_page_config(page_title="Noon UAE 3C 数据台", layout="wide", page_icon="📱")

# 标题
st.title("📱 Noon UAE 3C 全类目监控中心")
st.markdown("*专为佛山跨境电商运营设计 - 阿联酋站实时选品分析*")

# 模拟 Noon 3C 数据
@st.cache_data
def load_mock_data():
    np.random.seed(42)
    categories = ['Mobiles', 'Audio', 'Laptops', 'Tablets', 'Accessories']
    
    data = {
        'Product': [
            'iPhone 16 Pro Max', 'Samsung Galaxy S25', 'Xiaomi 14 Ultra', 
            'Sony WH-1000XM6', 'AirPods Pro 3', 'JBL Flip 7',
            'MacBook Pro M4', 'Dell XPS 15', 'HP Spectre x360',
            'iPad Pro 13"', 'Samsung Galaxy Tab S10', 'Lenovo Tab P12',
            'GaN 65W Charger', 'Anker Power Bank', 'USB-C Hub',
            'Logitech MX Master 4', 'Razer DeathAdder V4', 'Apple Magic Keyboard'
        ],
        'Category': ['Mobiles']*3 + ['Audio']*3 + ['Laptops']*3 + ['Tablets']*3 + ['Accessories']*6,
        'Price_AED': [4299, 3799, 2999, 1299, 899, 399, 7999, 5999, 4599, 3999, 2799, 1499, 89, 149, 199, 399, 299, 449],
        'Sales_30D': [850, 1200, 1800, 650, 2100, 890, 320, 580, 410, 720, 960, 450, 3200, 2800, 1900, 780, 1100, 520],
        'Growth_Rate': [0.15, 0.22, 0.45, 0.08, 0.35, 0.18, 0.05, 0.12, 0.09, 0.20, 0.28, 0.15, 0.62, 0.48, 0.38, 0.11, 0.25, 0.07],
        'Rating': [4.8, 4.6, 4.7, 4.9, 4.7, 4.5, 4.9, 4.7, 4.6, 4.8, 4.5, 4.4, 4.6, 4.8, 4.5, 4.7, 4.6, 4.8]
    }
    
    df = pd.DataFrame(data)
    
    # 计算爆款指数 (3C 专用算法)
    df['Boom_Index'] = (df['Sales_30D'] * (1 + df['Growth_Rate']) * df['Rating']) / np.sqrt(df['Price_AED'])
    df['Boom_Index'] = df['Boom_Index'] / df['Boom_Index'].max() * 100
    
    return df

df = load_mock_data()

# 侧边栏过滤器
st.sidebar.header("🔍 筛选条件")
selected_categories = st.sidebar.multiselect(
    "选择 3C 子类目",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

price_range = st.sidebar.slider(
    "价格区间 (AED)",
    min_value=0,
    max_value=int(df['Price_AED'].max()),
    value=(0, int(df['Price_AED'].max()))
)

# 数据过滤
filtered_df = df[
    (df['Category'].isin(selected_categories)) &
    (df['Price_AED'] >= price_range[0]) &
    (df['Price_AED'] <= price_range[1])
]

# 核心指标卡片
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("监控商品数", len(filtered_df))
with col2:
    st.metric("平均增长率", f"{filtered_df['Growth_Rate'].mean():.1%}")
with col3:
    st.metric("高潜力爆款", len(filtered_df[filtered_df['Boom_Index'] > 50]))
with col4:
    avg_rating = filtered_df['Rating'].mean()
    st.metric("平均评分", f"{avg_rating:.2f}⭐")

# 可视化图表
tab1, tab2, tab3 = st.tabs(["📊 爆款分布图", "📈 类目分析", "📋 详细数据"])

with tab1:
    st.subheader("🔥 3C 爆款指数分布 (销量 vs 增长率)")
    fig1 = px.scatter(
        filtered_df,
        x='Sales_30D',
        y='Growth_Rate',
        size='Boom_Index',
        color='Category',
        hover_name='Product',
        hover_data={'Price_AED': ':,.0f', 'Rating': ':.1f', 'Boom_Index': ':.1f'},
        title='销量-增长率象限图',
        labels={'Sales_30D': '30天销量', 'Growth_Rate': '增长率', 'Category': '类目'},
        size_max=60
    )
    fig1.update_layout(height=500)
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📦 类目销量分布")
        category_sales = filtered_df.groupby('Category')['Sales_30D'].sum().reset_index()
        fig2 = px.pie(
            category_sales,
            values='Sales_30D',
            names='Category',
            title='各类目销量占比'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col_b:
        st.subheader("💰 类目平均价格")
        category_price = filtered_df.groupby('Category')['Price_AED'].mean().reset_index()
        fig3 = px.bar(
            category_price,
            x='Category',
            y='Price_AED',
            title='各类目平均售价 (AED)',
            color='Price_AED',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("📊 详细商品数据清单")
    
    # 添加潜力标签
    def boom_label(score):
        if score > 70:
            return "🔥 极高潜力"
        elif score > 50:
            return "⭐ 高潜力"
        elif score > 30:
            return "📈 中等潜力"
        else:
            return "🔵 稳定款"
    
    display_df = filtered_df.copy()
    display_df['潜力标签'] = display_df['Boom_Index'].apply(boom_label)
    display_df['增长率'] = display_df['Growth_Rate'].apply(lambda x: f"{x:.1%}")
    display_df['价格'] = display_df['Price_AED'].apply(lambda x: f"{x:,.0f} AED")
    display_df['爆款指数'] = display_df['Boom_Index'].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(
        display_df[['Product', 'Category', '价格', 'Sales_30D', '增长率', 'Rating', '爆款指数', '潜力标签']].sort_values(by='Boom_Index', ascending=False),
        use_container_width=True,
        hide_index=True
    )

# 底部运营建议
st.markdown("---")
st.subheader("💡 佛山运营建议")
top_3 = filtered_df.nlargest(3, 'Boom_Index')

for idx, row in top_3.iterrows():
    with st.expander(f"🎯 {row['Product']} - 爆款指数: {row['Boom_Index']:.1f}"):
        col_x, col_y = st.columns([2, 1])
        with col_x:
            st.write(f"**类目**: {row['Category']}")
            st.write(f"**售价**: {row['Price_AED']:,.0f} AED")
            st.write(f"**30天销量**: {row['Sales_30D']:,} 件")
            st.write(f"**增长率**: {row['Growth_Rate']:.1%}")
            st.write(f"**评分**: {row['Rating']}⭐")
        with col_y:
            if row['Category'] == 'Accessories':
                st.success("✅ 建议从佛山货源快速补货至 FBN 仓")
            elif row['Growth_Rate'] > 0.3:
                st.warning("⚡ 增长迅猛，建议加大库存")
            else:
                st.info("📊 稳定爆款，保持库存监控")

st.markdown("---")
st.caption("数据更新时间: 2026-01-03 | 专为 Noon 阿联酋站 3C 类目设计")
