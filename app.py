import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

# ==================== 页面配置 ====================
st.set_page_config(page_title="5G 信号可视化看板", layout="wide")

# ==================== 科技风格 CSS ====================
st.markdown("""
<style>
    /* 暗色科技主题 */
    .stApp {
        background: #0a0e17;
        color: #e0e0e0;
    }

    /* 玻璃态 KPI 卡片 */
    .kpi-card {
        background: linear-gradient(135deg, rgba(20, 30, 60, 0.9), rgba(10, 15, 30, 0.9));
        border: 1px solid rgba(0, 200, 255, 0.2);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 200, 255, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        text-align: center;
        transition: all 0.3s ease;
    }
    .kpi-card:hover {
        box-shadow: 0 8px 32px 0 rgba(0, 200, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(0, 200, 255, 0.5);
        transform: translateY(-2px);
    }
    .kpi-title {
        font-size: 13px;
        color: rgba(0, 229, 255, 0.7);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 8px;
        font-family: 'SF Mono', 'Consolas', monospace;
        font-weight: 500;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, #00e5ff, #7c4dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'SF Mono', 'Consolas', monospace;
    }

    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background: rgba(10, 14, 23, 0.95);
        border-right: 1px solid rgba(0, 200, 255, 0.1);
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #00e5ff;
        font-family: 'SF Mono', 'Consolas', monospace;
    }

    /* 标题 */
    .tech-title {
        background: linear-gradient(135deg, #00e5ff, #7c4dff, #ff0055);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0;
        line-height: 1.2;
    }
    .tech-subtitle {
        color: rgba(0, 229, 255, 0.5);
        font-size: 0.95rem;
        margin-top: 4px;
        letter-spacing: 3px;
        font-weight: 300;
    }

    /* 子标题 */
    .tech-subheader {
        color: #00e5ff;
        border-left: 3px solid #7c4dff;
        padding-left: 12px;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0;
    }

    /* 图例 */
    .tech-legend {
        background: rgba(10, 14, 23, 0.9);
        border: 1px solid rgba(0, 200, 255, 0.15);
        border-radius: 8px;
        padding: 8px 16px;
        color: #aaa;
        font-size: 13px;
        text-align: center;
        margin-top: 8px;
    }
    .legend-item {
        display: inline-block;
        margin: 0 16px;
    }
    .legend-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 6px;
        vertical-align: middle;
    }

    /* 滚动条 */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0a0e17; }
    ::-webkit-scrollbar-thumb { background: rgba(0, 200, 255, 0.25); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0, 200, 255, 0.4); }

    /* divider */
    hr {
        border-color: rgba(0, 200, 255, 0.08) !important;
        margin: 1.5em 0 !important;
    }

    /* 侧边栏控件微调 */
    .stSlider label, .stMultiSelect label, .stRadio label, .stCheckbox label {
        color: #ccc !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 标题 ====================
st.markdown('<h1 class="tech-title">5G 信号可视化看板</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="tech-subtitle">✦ 基于 5G 路测数据的交互式信号质量分析平台 ✦</p>',
    unsafe_allow_html=True,
)

# ==================== 数据加载 ====================
@st.cache_data
def load_data():
    """从 CSV 加载 5G 路测数据"""
    df = pd.read_csv("data/signal_samples.csv")
    return df


df = load_data()

# ==================== 科技风格颜色映射 ====================
# 赛博朋克配色：优秀→青 Cyan · 中等→电紫 Purple · 弱覆盖→霓虹粉 Magenta
CYAN = [0, 229, 255]       # #00E5FF  优秀
PURPLE = [170, 0, 255]     # #AA00FF  中等
MAGENTA = [255, 0, 85]     # #FF0055  弱覆盖

def classify_rsrp(rsrp):
    """根据 RSRP 返回信号等级标签"""
    if rsrp > -90:
        return "优秀"
    elif rsrp < -110:
        return "弱覆盖"
    else:
        return "中等"

df["color_r"] = df["RSRP_dBm"].apply(
    lambda v: CYAN[0] if v > -90 else (MAGENTA[0] if v < -110 else PURPLE[0])
)
df["color_g"] = df["RSRP_dBm"].apply(
    lambda v: CYAN[1] if v > -90 else (MAGENTA[1] if v < -110 else PURPLE[1])
)
df["color_b"] = df["RSRP_dBm"].apply(
    lambda v: CYAN[2] if v > -90 else (MAGENTA[2] if v < -110 else PURPLE[2])
)
df["color_a"] = 200

# 预计算 HeatmapLayer 权重列（归一化到 0~1，信号越强权重越高）
df["weight"] = df["RSRP_dBm"].apply(lambda v: max(0.05, (v + 120) / 50))

# ==================== 侧边栏筛选器 ====================
st.sidebar.markdown("### ⚡ 筛选控制台")
st.sidebar.markdown("---")

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

view_mode = st.sidebar.radio("地图视图", options=["2D 散点图", "3D 柱状图"], index=0)

show_heatmap = st.sidebar.checkbox("信号热力云", value=True)

st.sidebar.markdown("---")
st.sidebar.caption("🚀 Code with AI Contest · 5G 信号可视化")

# 应用筛选
filtered_df = df[
    (df["Band"].isin(selected_bands))
    & (df["RSRP_dBm"].between(rsrp_min, rsrp_max))
    & (df["TerminalType"].isin(selected_terminals))
].copy()

# ==================== KPI 指标卡片（玻璃态效果） ====================
st.markdown("---")
st.markdown('<p class="tech-subheader">数据概览</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-title">总采样点</div>'
        f'<div class="kpi-value">{len(filtered_df):,}</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    val = filtered_df["RSRP_dBm"].mean()
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-title">平均 RSRP</div>'
        f'<div class="kpi-value">{val:.1f} dBm</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    val = filtered_df["SINR_dB"].mean()
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-title">平均 SINR</div>'
        f'<div class="kpi-value">{val:.1f} dB</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    val = filtered_df["Download_Mbps"].mean()
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-title">平均下载速率</div>'
        f'<div class="kpi-value">{val:.1f} Mbps</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ==================== 信号地图 ====================
st.markdown('<p class="tech-subheader">5G 信号覆盖地图</p>', unsafe_allow_html=True)

view_center_lat = filtered_df["Latitude"].mean()
view_center_lon = filtered_df["Longitude"].mean()

map_layers = []

# ── 热力云层（背景辉光效果） ──
if show_heatmap and len(filtered_df) > 1:
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        aggregation="MEAN",
        radiusPixels=40,
        intensity=1.8,
        threshold=0.02,
        colorRange=[
            [0, 0, 0, 0],
            [0, 180, 255, 60],
            [0, 229, 255, 90],
            [170, 0, 255, 100],
            [255, 0, 85, 110],
        ],
        get_weight="weight",
    )
    map_layers.append(heatmap_layer)

# ── 2D 或 3D 主图层 ──
if view_mode == "2D 散点图":
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        get_fill_color=["color_r", "color_g", "color_b", "color_a"],
        get_radius=120,
        pickable=True,
        opacity=0.85,
        radius_min_pixels=3,
        radius_max_pixels=14,
        stroked=True,
        get_line_color=["color_r", "color_g", "color_b", 255],
        line_width_min_pixels=1,
    )
    map_layers.append(scatter_layer)

    view_state = pdk.ViewState(
        latitude=view_center_lat,
        longitude=view_center_lon,
        zoom=12,
        pitch=0,
    )
else:
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        get_elevation="Download_Mbps",
        elevation_scale=0.6,
        radius=70,
        get_fill_color=["color_r", "color_g", "color_b", 200],
        pickable=True,
        extruded=True,
        coverage=0.85,
        diskResolution=24,
    )
    map_layers.append(column_layer)

    view_state = pdk.ViewState(
        latitude=view_center_lat,
        longitude=view_center_lon,
        zoom=12,
        pitch=45,
        bearing=15,
    )

st.pydeck_chart(
    pdk.Deck(
        layers=map_layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={
            "html": """
            <div style="font-family:'SF Mono',Consolas,monospace;background:rgba(10,14,23,0.94);
                        border:1px solid rgba(0,229,255,0.25);border-radius:8px;padding:12px;">
                <div style="color:#00e5ff;font-size:13px;font-weight:600;margin-bottom:8px;
                            border-bottom:1px solid rgba(0,229,255,0.15);padding-bottom:6px;">
                    📡 信号详情
                </div>
                <div style="display:grid;grid-template-columns:auto 1fr;gap:3px 14px;font-size:12px;">
                    <span style="color:#888;">Cell ID</span>
                    <span style="color:#fff;text-align:right;">{CellID}</span>
                    <span style="color:#888;">频段</span>
                    <span style="color:#aa00ff;text-align:right;">{Band}</span>
                    <span style="color:#888;">RSRP</span>
                    <span style="color:#ff0055;text-align:right;">{RSRP_dBm} dBm</span>
                    <span style="color:#888;">SINR</span>
                    <span style="color:#00e5ff;text-align:right;">{SINR_dB} dB</span>
                    <span style="color:#888;">下载速率</span>
                    <span style="color:#00ff88;text-align:right;">{Download_Mbps} Mbps</span>
                    <span style="color:#888;">终端</span>
                    <span style="color:#ffaa00;text-align:right;">{TerminalType}</span>
                </div>
            </div>
            """,
            "style": {"backgroundColor": "transparent", "border": "none", "boxShadow": "none"},
        },
    ),
    use_container_width=True,
)

# 图例
st.markdown(
    '<div class="tech-legend">'
    '<span class="legend-item"><span class="legend-dot" style="background:#00e5ff;box-shadow:0 0 8px #00e5ff;"></span> 优秀 &gt; -90 dBm</span>'
    '<span class="legend-item"><span class="legend-dot" style="background:#aa00ff;box-shadow:0 0 8px #aa00ff;"></span> 中等 -110 ~ -90 dBm</span>'
    '<span class="legend-item"><span class="legend-dot" style="background:#ff0055;box-shadow:0 0 8px #ff0055;"></span> 弱覆盖 &lt; -110 dBm</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

# ==================== 数据统计分析 ====================
st.markdown('<p class="tech-subheader">数据统计分析</p>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    band_counts = filtered_df.groupby("Band")["CellID"].nunique().reset_index()
    band_counts.columns = ["频段", "基站数量"]
    fig_bar = px.bar(
        band_counts,
        x="频段",
        y="基站数量",
        color="频段",
        color_discrete_map={"n28": "#00e5ff", "n41": "#aa00ff", "n78": "#ff0055"},
        title="各频段基站数量分布",
        template="plotly_dark",
    )
    fig_bar.update_layout(
        showlegend=False,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc", size=12),
        title=dict(text="各频段基站数量分布", font=dict(color="#00e5ff", size=16), x=0.5),
        margin=dict(t=40),
    )
    fig_bar.update_traces(marker=dict(line=dict(width=0)))
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    terminal_counts = filtered_df["TerminalType"].value_counts().reset_index()
    terminal_counts.columns = ["终端类型", "数量"]
    fig_pie = px.pie(
        terminal_counts,
        names="终端类型",
        values="数量",
        color="终端类型",
        color_discrete_map={"Smartphone": "#00e5ff", "CPE": "#aa00ff", "IoT": "#ff0055"},
        title="终端类型占比分布",
        hole=0.4,
        template="plotly_dark",
    )
    fig_pie.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc", size=12),
        title=dict(text="终端类型占比分布", font=dict(color="#00e5ff", size=16), x=0.5),
        margin=dict(t=40),
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ==================== 数据表格预览 ====================
with st.expander("📋 查看原始数据", expanded=False):
    st.dataframe(filtered_df, use_container_width=True)
    st.caption(f"共加载 {len(filtered_df)} 条信号采样记录")
