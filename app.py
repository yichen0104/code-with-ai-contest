import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

# ==================== 页面配置 ====================
st.set_page_config(page_title="5G 信号可视化看板", layout="wide")

# ==================== 标题 ====================
st.title("📡 5G 信号可视化看板")
st.markdown("基于 5G 路测数据的交互式信号质量分析平台")

# ==================== 数据加载 ====================
@st.cache_data
def load_data():
    """从 data/signal_samples.csv 加载 5G 路测数据，返回 DataFrame"""
    df = pd.read_csv("data/signal_samples.csv")
    return df

df = load_data()

# ==================== 颜色映射函数 ====================
def classify_rsrp(rsrp):
    """根据 RSRP 值返回信号等级标签（优秀/中等/弱覆盖）"""
    if rsrp > -90:
        return "优秀"
    elif rsrp < -110:
        return "弱覆盖"
    else:
        return "中等"

# 在 DataFrame 中预计算 RGBA 颜色分量
# pydeck 要求颜色值为原生 Python int 类型，避免 numpy 类型序列化报错
df["color_r"] = df["RSRP_dBm"].apply(lambda v: 46 if v > -90 else (231 if v < -110 else 243))
df["color_g"] = df["RSRP_dBm"].apply(lambda v: 204 if v > -90 else (76 if v < -110 else 156))
df["color_b"] = df["RSRP_dBm"].apply(lambda v: 113 if v > -90 else (60 if v < -110 else 18))
df["color_a"] = 200

# ==================== 侧边栏筛选器 ====================
st.sidebar.header("筛选条件")

selected_bands = st.sidebar.multiselect(
    "频段 Band",
    options=sorted(df["Band"].unique()),
    default=sorted(df["Band"].unique()),
)

rsrp_min, rsrp_max = st.sidebar.slider(
    "RSRP 范围 (dBm)",
    min_value=-120.0,
    max_value=-70.0,
    value=(float(df["RSRP_dBm"].min()), float(df["RSRP_dBm"].max())),
    step=1.0,
)

selected_terminals = st.sidebar.multiselect(
    "终端类型",
    options=sorted(df["TerminalType"].unique()),
    default=sorted(df["TerminalType"].unique()),
)

view_mode = st.sidebar.radio(
    "地图视图",
    options=["2D 散点图", "3D 柱状图"],
    index=0,
)

# 应用筛选：频段 + RSRP 范围 + 终端类型
filtered_df = df[
    (df["Band"].isin(selected_bands)) &
    (df["RSRP_dBm"].between(rsrp_min, rsrp_max)) &
    (df["TerminalType"].isin(selected_terminals))
]

# ==================== KPI 指标卡片 ====================
st.subheader("📊 数据概览")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总采样点", f"{len(filtered_df):,}")
with col2:
    st.metric("平均 RSRP", f"{filtered_df['RSRP_dBm'].mean():.2f} dBm")
with col3:
    st.metric("平均 SINR", f"{filtered_df['SINR_dB'].mean():.2f} dB")
with col4:
    st.metric("平均下载速率", f"{filtered_df['Download_Mbps'].mean():.2f} Mbps")

st.divider()

# ==================== 信号地图（2D/3D 切换） ====================
st.subheader("🗺️ 5G 信号覆盖地图")

# 以筛选后数据的中心作为地图初始视角
view_center_lat = filtered_df["Latitude"].mean()
view_center_lon = filtered_df["Longitude"].mean()

if view_mode == "2D 散点图":
    # 2D 散点图层，颜色根据 RSRP 强度映射为绿/橙/红
    map_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        get_fill_color=["color_r", "color_g", "color_b", "color_a"],
        get_radius=120,
        pickable=True,
        opacity=0.8,
        radius_min_pixels=3,
        radius_max_pixels=15,
    )
    view_state = pdk.ViewState(
        latitude=view_center_lat,
        longitude=view_center_lon,
        zoom=12,
        pitch=0,
    )
else:
    # 3D 柱状图层：高度映射下载速率，柱体颜色仍按 RSRP 强度
    map_layer = pdk.Layer(
        "ColumnLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        get_elevation="Download_Mbps",
        elevation_scale=0.5,
        radius=80,
        get_fill_color=["color_r", "color_g", "color_b", "color_a"],
        pickable=True,
        extruded=True,
        coverage=0.8,
    )
    view_state = pdk.ViewState(
        latitude=view_center_lat,
        longitude=view_center_lon,
        zoom=12,
        pitch=45,
        bearing=10,
    )

st.pydeck_chart(
    pdk.Deck(
        layers=[map_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v10",
        tooltip={
            "html": """
            <b>Cell ID:</b> {CellID}<br/>
            <b>Band:</b> {Band}<br/>
            <b>RSRP:</b> {RSRP_dBm} dBm<br/>
            <b>SINR:</b> {SINR_dB} dB<br/>
            <b>下载速率:</b> {Download_Mbps} Mbps<br/>
            <b>终端:</b> {TerminalType}
            """,
            "style": {"backgroundColor": "steelblue", "color": "white"},
        },
    ),
    use_container_width=True,
)

st.caption("🟢 绿色: RSRP > -90 dBm (优秀)  |  🟠 橙色: -110 ~ -90 dBm (中等)  |  🔴 红色: RSRP < -110 dBm (弱覆盖)")

st.divider()

# ==================== 数据概览图表 ====================
st.subheader("📈 数据统计分析")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # 各频段基站数量柱状图（以 CellID 去重计数）
    band_counts = filtered_df.groupby("Band")["CellID"].nunique().reset_index()
    band_counts.columns = ["频段", "基站数量"]
    fig_bar = px.bar(
        band_counts,
        x="频段",
        y="基站数量",
        color="频段",
        color_discrete_map={"n28": "#3498DB", "n41": "#9B59B6", "n78": "#1ABC9C"},
        title="各频段基站数量分布",
    )
    fig_bar.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    # 终端类型占比饼图
    terminal_counts = filtered_df["TerminalType"].value_counts().reset_index()
    terminal_counts.columns = ["终端类型", "数量"]
    fig_pie = px.pie(
        terminal_counts,
        names="终端类型",
        values="数量",
        color="终端类型",
        color_discrete_map={"Smartphone": "#E74C3C", "CPE": "#2ECC71", "IoT": "#F39C12"},
        title="终端类型占比分布",
        hole=0.4,
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ==================== 数据表格预览 ====================
with st.expander("📋 查看原始数据", expanded=False):
    st.dataframe(filtered_df, use_container_width=True)
    st.caption(f"共加载 {len(filtered_df)} 条信号采样记录")
