# 5G 信号可视化看板 — 详细设计文档

---

## 一、整体设计

### 1.1 应用架构

本系统采用 **单页 Web 看板** 架构，基于 Streamlit 的页面渲染模型，将数据加载、筛选过滤、可视化展示三个环节串联在单一 Python 脚本中执行。

```
┌─────────────────────────────────────────────────────┐
│                    浏览器客户端                      │
└────────────────────────┬────────────────────────────┘
                         │ HTTP (Streamlit Server)
┌────────────────────────▼────────────────────────────┐
│                  Streamlit 应用层                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ 侧边栏    │  │ 地图区域  │  │ 图表区域          │  │
│  │ (筛选器)  │  │ (pydeck) │  │ (柱状图/饼图)     │  │
│  └─────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│        └──────────────┼────────────────┘            │
│               ┌───────▼────────┐                     │
│               │  会话状态管理   │                     │
│               │  (st.session_  │                     │
│               │   state)       │                     │
│               └───────┬────────┘                     │
│                       │                              │
│               ┌───────▼────────┐                     │
│               │   数据加载层    │                     │
│               │  (pandas CSV)  │                     │
│               └────────────────┘                     │
└─────────────────────────────────────────────────────┘
```

### 1.2 数据流

```
signal_samples.csv  →  pandas.read_csv()  →  DataFrame (全量数据)
                                                    │
                              ┌─────────────────────┤
                              ▼                     ▼
                      Sidebar 筛选器          未经筛选的全量视图
                      (Band / RSRP)           (初始默认状态)
                              │                     │
                              ▼                     ▼
                        filtered_df ────────→  pydeck 地图
                              │              →  matplotlib/plotly 图表
                              ▼
                       st.metrics (KPI)
```

### 1.3 组件树

```
Streamlit App (app.py)
├── st.set_page_config()                 # 页面元信息
├── st.title() / st.markdown()           # 标题区
├── Sidebar (st.sidebar)
│   ├── Band 频段下拉多选               # 进阶关卡
│   ├── RSRP 范围滑动条                 # 进阶关卡
│   ├── TerminalType 终端类型多选        # 可选扩展
│   └── SINR 范围滑动条                 # 可选扩展
├── Main Area
│   ├── KPI 指标卡片 (st.metrics)       # 总采样点/平均RSRP/平均速率
│   ├── 地图区域
│   │   ├── 2D 散点热力图 (pydeck)      # 基础关卡
│   │   └── 3D 柱状图 (pydeck ColumnLayer) # 进阶关卡
│   └── 图表区域 (st.columns)
│       ├── 频段分布柱状图              # 基础关卡
│       └── 终端类型占比饼图            # 基础关卡
└── Footer
    └── 数据表格 (st.dataframe)          # 原始数据预览
```

---

## 二、技术栈

| 层级 | 技术 | 版本要求 | 用途 |
|------|------|----------|------|
| 运行时 | Python | ≥ 3.9 | 主编程语言 |
| Web 框架 | Streamlit | ≥ 1.28 | 交互式 Web 看板引擎 |
| 数据处理 | pandas | ≥ 1.5 | CSV 读取、DataFrame 筛选与聚合 |
| 2D 地图 | pydeck | ≥ 0.8 | 基于 deck.gl 的高性能地图渲染 |
| 3D 地图 | pydeck (ColumnLayer) | ≥ 0.8 | 3D 柱状图层，高度映射下载速率 |
| 图表 | plotly / matplotlib | — | 柱状图、饼图渲染（推荐 plotly 以获得交互性） |
| 数值计算 | numpy | ≥ 1.24 | 辅助数组计算 |

**依赖清单 (requirements.txt)：**

```
streamlit
pandas
pydeck
numpy
plotly
```

---

## 三、需求实现方案

### 3.1 基础关卡（必做）

#### 3.1.1 数据加载

- **描述**：使用 pandas 读取 `data/signal_samples.csv`
- **实现**：`df = pd.read_csv("data/signal_samples.csv")`
- **验证标准**：应用启动时无报错，数据表格可正常预览
- **关键字段**：
  - `Latitude`, `Longitude` — 经纬度（地图定位）
  - `CellID` — 小区标识
  - `Band` — 频段（n28 / n41 / n78）
  - `RSRP_dBm` — 参考信号接收功率（信号强度，单位 dBm）
  - `SINR_dB` — 信噪比（单位 dB）
  - `TerminalType` — 终端类型（Smartphone / CPE / IoT）
  - `Download_Mbps` — 下载速率（Mbps）

#### 3.1.2 信号热力/散点地图

- **描述**：在地图主体区域渲染一张交互地图，将经纬度数据打在地图上
- **实现方案**：使用 `pydeck` 的 `ScatterplotLayer` 或 `HeatmapLayer`
- **核心逻辑 — 颜色映射**：
  - RSRP > -90 dBm → **绿色** `[0, 255, 0]`（信号优秀）
  - -110 ≤ RSRP ≤ -90 dBm → **黄色/橙色** `[255, 165, 0]`（信号中等）
  - RSRP < -110 dBm → **红色** `[255, 0, 0]`（信号弱）
- **颜色函数设计**：

```python
def get_color(rsrp):
    if rsrp > -90:
        return [0, 255, 0]       # 绿色
    elif rsrp < -110:
        return [255, 0, 0]       # 红色
    else:
        return [255, 165, 0]     # 橙色
```

- **地图配置**：
  - 初始视角中心：数据经纬度的均值
  - 缩放级别：适中（zoom ≈ 11）
  - 底图：MapStyle.LIGHT（浅色地图，突出数据点）
  - Tooltip：悬停显示 CellID、Band、RSRP、SINR、Download_Mbps

#### 3.1.3 数据概览图表

- **图表 A — 频段基站数量柱状图**：
  - 数据聚合：`df.groupby("Band")["CellID"].nunique()`
  - 图表类型：柱状图（bar chart）
  - 推荐实现：`plotly.express.bar()` 或 `st.bar_chart()`
  - X 轴：频段 (n28, n41, n78)，Y 轴：基站数量

- **图表 B — 终端类型占比饼图**：
  - 数据聚合：`df["TerminalType"].value_counts()`
  - 图表类型：饼图（pie chart）
  - 推荐实现：`plotly.express.pie()`

### 3.2 进阶关卡（加分项）

#### 3.2.1 侧边栏联动筛选

- **组件清单**：
  1. **频段多选下拉框** (`st.sidebar.multiselect`)：可选 n28 / n41 / n78，默认全选
  2. **RSRP 范围滑动条** (`st.sidebar.slider`)：范围 -120 ~ -70 dBm，默认全范围
  3. **终端类型多选** (`st.sidebar.multiselect`)：可选 Smartphone / CPE / IoT（可选扩展）

- **联动机制**：
  - 所有筛选器位于 `st.sidebar` 中
  - 筛选操作触发 DataFrame 过滤：`filtered_df = df[(df["Band"].isin(selected_bands)) & (df["RSRP_dBm"].between(rsrp_min, rsrp_max))]`
  - 地图和图表的数据源全部替换为 `filtered_df`
  - Streamlit 的事件驱动模型天然支持：**每次 UI 操作 → 完整脚本重新执行 → 地图和图表实时更新**

- **性能考虑**：数据量较小（模拟数据集），无需引入缓存机制，筛选直接实时计算即可。

#### 3.2.2 3D 地图视觉增强

- **描述**：使用 3D 柱状图让信号点"站起来"，高度随下载速率变化
- **实现方案**：使用 `pydeck.ColumnLayer`
- **关键参数映射**：
  - `getPosition`：`[Longitude, Latitude]`
  - `getElevation`：`Download_Mbps`（归一化处理或直接使用原始值）
  - `getFillColor`：基于 RSRP 的颜色映射（同 2D 规则）
  - `radius`：柱体半径（约 50-100 米视觉单位）
  - `elevationScale`：高度缩放系数，使得速率差异在视觉上可区分
  - `extruded`：`True`（启用 3D 拉伸）
- **视角配置**：
  - `pitch`：约 45-60 度（倾斜视角以呈现 3D 效果）
  - `bearing`：约 0-15 度
- **交互建议**：允许用户在 2D 与 3D 视图之间切换（单选按钮 `st.radio`）

#### 3.2.3 工程化素养

- **代码注释**：
  - 每个函数添加 docstring
  - 关键逻辑段添加行内注释
  - 遵循 PEP 257 规范

- **单元测试**：
  - 测试框架：`pytest`
  - 测试文件：`test_app.py`
  - 测试覆盖：
    1. `test_load_data()` — 验证 CSV 正确加载，DataFrame 非空，包含必要字段
    2. `test_color_mapping()` — 验证颜色函数对三种 RSRP 区间的返回值正确
    3. `test_filter_data()` — 验证筛选逻辑：Band 筛选、RSRP 范围筛选正确
    4. `test_aggregation()` — 验证频段分组计数、终端类型分布统计正确

---

## 四、页面布局设计

### 4.1 整体布局

```
┌──────────────────────────────────────────────────────────┐
│  📡 5G 信号可视化看板                                      │
│  ─────────────────────────────────────────────────────── │
├────────────┬─────────────────────────────────────────────┤
│  侧边栏     │  主内容区域                                   │
│            │                                              │
│  ▼ 频段    │  ┌─────────────────────────────────────┐    │
│  [n28]    │  │  📊 KPI 指标卡                        │    │
│  [n41]    │  │  [总采样点] [平均RSRP] [平均速率]       │    │
│  [n78]    │  └─────────────────────────────────────┘    │
│            │                                              │
│  RSRP范围  │  ┌─────────────────────────────────────┐    │
│  [─●──]   │  │  🗺️ 地图区域                         │    │
│  -120~-70 │  │  (pydeck 2D / 3D 切换)              │    │
│            │  │                                      │    │
│  终端类型  │  │                                      │    │
│  [全部]   │  └─────────────────────────────────────┘    │
│            │                                              │
│            │  ┌──────────────┬──────────────────────┐    │
│            │  │ 📊 频段分布   │ 🥧 终端类型占比       │    │
│            │  │  (柱状图)    │  (饼图)               │    │
│            │  └──────────────┴──────────────────────┘    │
│            │                                              │
│            │  ┌─────────────────────────────────────┐    │
│            │  │ 📋 数据预览 (可折叠)                  │    │
│            │  │ st.dataframe(filtered_df)            │    │
│            │  └─────────────────────────────────────┘    │
└────────────┴─────────────────────────────────────────────┘
```

### 4.2 配色方案

| 信号等级 | RSRP 范围 | 颜色 | 色值 |
|----------|-----------|------|------|
| 优秀 | > -90 dBm | 绿色 | `#2ECC71` |
| 中等 | -110 ~ -90 dBm | 橙色 | `#F39C12` |
| 弱 | < -110 dBm | 红色 | `#E74C3C` |

---

## 五、文件结构与交付件清单

### 5.1 仓库文件结构

```
code-with-ai-contest/
├── app.py                  # 主应用程序
├── requirements.txt        # Python 依赖
├── README.md               # 项目说明文档（终版）
├── DESIGN.md               # 本详细设计文档
├── AI_PROMPTS.md           # Agent 交互日志
├── test_app.py             # 单元测试文件
├── screenshots/            # 运行截图（2-3张）
│   ├── screenshot_1.png
│   ├── screenshot_2.png
│   └── screenshot_3.png
└── data/
    └── signal_samples.csv  # 5G 路测模拟数据
```

### 5.2 四项硬核交付物

| 序号 | 交付物 | 文件名 | 验收标准 |
|------|--------|--------|----------|
| 1 | 源代码 | `app.py` + `requirements.txt` | 一键 `streamlit run app.py` 可运行 |
| 2 | 项目说明文档 | `README.md` | 包含功能介绍、运行方法、技术栈说明 |
| 3 | 运行截图 | `screenshots/*.png` | 2-3 张，展示地图和侧边栏交互 |
| 4 | Agent 交互日志 | `AI_PROMPTS.md` | 完整 AI 对话记录，反映代码构建过程 |

### 5.3 Git Tag 进度打卡

| 关卡 | Tag 名称 | 完成标志 |
|------|----------|----------|
| 基础关卡 | `basic-done` | 数据加载 + 地图 + 图表 三项全部完成 |
| 进阶关卡 | `advanced-done` | 侧边栏联动 + 3D 地图 + 注释与测试 三项全部完成 |

---

## 六、开发与运行指南

### 6.1 环境准备

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 6.2 启动应用

```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`，展示 5G 信号可视化看板。

### 6.3 运行单元测试

```bash
pytest test_app.py -v
```

---

## 七、实现优先级与阶段划分

| 阶段 | 内容 | 预计工作量 | 产出 |
|------|------|-----------|------|
| Phase 1 | 数据加载 + 2D 地图 + 颜色映射 | 基础关卡核心 | 可运行的最小看板 |
| Phase 2 | 频段柱状图 + 终端占比饼图 | 基础关卡收尾 | 基础关卡完成，打 `basic-done` tag |
| Phase 3 | 侧边栏筛选器 + 联动 | 进阶关卡 | 交互式看板 |
| Phase 4 | 3D 柱状图地图 | 进阶关卡 | 3D 视觉效果 |
| Phase 5 | 代码注释 + 单元测试 | 进阶关卡收尾 | 进阶关卡完成，打 `advanced-done` tag |
