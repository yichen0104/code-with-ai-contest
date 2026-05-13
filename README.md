# 📡 5G 信号可视化看板

基于 Streamlit 构建的 5G 路测数据交互式 Web 看板。将 `signal_samples.csv` 中的信号采样数据转化为地图热力图、3D 柱状图、统计图表，支持侧边栏实时筛选联动。

---

## 一、看板功能

### 🟢 基础功能

| 功能 | 说明 |
|------|------|
| **CSV 数据加载** | 使用 pandas 自动读取 `data/signal_samples.csv`，启动即加载，带 `@st.cache_data` 缓存 |
| **2D 信号散点地图** | 基于 pydeck ScatterplotLayer，将经纬度采样点打在交互地图上，颜色按 RSRP 信号强度映射 |
| **信号热力云** | HeatmapLayer 叠加层，直观展示信号覆盖密度与强度分布 |
| **悬停 Tooltip** | 鼠标悬停采样点显示 CellID、频段、RSRP、SINR、下载速率、终端类型等详情 |
| **KPI 指标卡片** | 顶部实时展示总采样点数、平均 RSRP、平均 SINR、平均下载速率 |
| **频段基站柱状图** | 按 Band 分组统计唯一基站数量（plotly 交互图表） |
| **终端类型饼图** | Smartphone / CPE / IoT 三类终端占比环形图（plotly 交互图表） |
| **原始数据预览** | 可折叠的 DataFrame 表格，查看当前筛选后的全部数据 |

### 🟡 进阶功能

| 功能 | 说明 |
|------|------|
| **侧边栏联动筛选** | 左侧筛选控制台提供：频段多选下拉、RSRP 范围滑动条、终端类型多选。所有筛选器操作触发地图与图表**实时更新** |
| **3D 柱状图地图** | pydeck ColumnLayer 渲染，采样点以 3D 柱体"站立"在地图上，柱高随下载速率（Download_Mbps）变化，支持拖拽旋转视角 |
| **2D / 3D 视图切换** | 侧边栏 Radio 按钮一键切换 2D 散点图与 3D 柱状图 |
| **科技风格 UI** | 暗色赛博朋克主题：玻璃态 KPI 卡片、发光渐变标题、霓虹色系信号配色、暗色地图底图 |
| **单元测试** | pytest 覆盖数据加载、颜色映射、筛选逻辑、聚合统计 |

### 信号颜色映射

| 信号等级 | RSRP 范围 | 颜色 | 色值 |
|----------|-----------|------|------|
| 优秀 | > -90 dBm | 青 Cyan | `#00E5FF` |
| 中等 | -110 ~ -90 dBm | 电紫 Purple | `#AA00FF` |
| 弱覆盖 | < -110 dBm | 霓虹粉 Magenta | `#FF0055` |

---

## 二、技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| Web 框架 | **Streamlit** ≥ 1.28 | 交互式看板引擎，事件驱动自动重渲染 |
| 数据处理 | **pandas** ≥ 1.5 | CSV 读取、DataFrame 筛选与聚合 |
| 2D/3D 地图 | **pydeck** ≥ 0.8 | 基于 deck.gl 的高性能地图（ScatterplotLayer / HeatmapLayer / ColumnLayer） |
| 统计图表 | **plotly** ≥ 5.0 | 交互式柱状图、饼图（暗色主题） |
| 数值计算 | **numpy** ≥ 1.24 | 辅助计算 |
| 测试框架 | **pytest** | 单元测试 |

---

## 三、快速开始

### 3.1 环境要求

- Python ≥ 3.9
- pip

### 3.2 安装与运行

```bash
# 1. 克隆仓库
git clone <your-repo-url>
cd code-with-ai-contest

# 2. （推荐）创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动看板
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`，即可查看 5G 信号可视化看板。

### 3.3 运行单元测试

```bash
pytest test_app.py -v
```

---

## 四、使用指南

### 筛选器操作

1. **频段筛选**：在左侧侧边栏的"频段 Band"多选框中勾选/取消 n28、n41、n78，地图和图表将仅展示对应频段数据
2. **RSRP 范围**：拖动滑动条调整 RSRP 区间（-120 ~ -70 dBm），用于聚焦特定信号强度范围的采样点
3. **终端类型**：筛选 Smartphone、CPE、IoT 终端类型
4. **地图视图**：通过 Radio 按钮在"2D 散点图"与"3D 柱状图"之间切换
5. **热力云开关**：勾选/取消"信号热力云"控制热力图叠加层的显示

### 地图交互

- **缩放**：鼠标滚轮
- **平移**：鼠标拖拽
- **旋转/倾斜**（3D 模式）：按住 Ctrl + 拖拽
- **悬停**：鼠标悬停采样点查看信号详情

---

## 五、项目结构

```
code-with-ai-contest/
├── app.py                  # 主应用程序（Streamlit 看板）
├── requirements.txt        # Python 依赖清单
├── README.md               # 项目说明文档
├── README_new.md           # 项目说明文档（终版，本文件）
├── DESIGN.md               # 详细设计文档
├── AI_PROMPTS.md           # AI Agent 交互日志
├── test_app.py             # 单元测试文件
├── screenshots/            # 运行截图
│   ├── screenshot_1.png
│   ├── screenshot_2.png
│   └── screenshot_3.png
└── data/
    └── signal_samples.csv  # 5G 路测模拟数据集
```

### 数据字段说明

| 字段 | 说明 |
|------|------|
| `Latitude` / `Longitude` | 采样点经纬度 |
| `CellID` | 基站小区标识 |
| `Band` | 频段（n28 / n41 / n78） |
| `RSRP_dBm` | 参考信号接收功率（dBm） |
| `SINR_dB` | 信噪比（dB） |
| `TerminalType` | 终端类型（Smartphone / CPE / IoT） |
| `Download_Mbps` | 下载速率（Mbps） |

---

## 六、进度打卡（Git Tag）

| 关卡 | Tag 名称 | 完成标志 |
|------|----------|----------|
| 基础关卡 | `basic-done` | 数据加载 + 2D 地图 + 柱状图/饼图 |
| 进阶关卡 | `advanced-done` | 侧边栏联动筛选 + 3D 地图 + 注释与单元测试 |

```bash
# 基础关卡完成时打标
git tag basic-done
git push origin basic-done

# 进阶关卡完成时打标
git tag advanced-done
git push origin advanced-done
```

---

## 七、交付物清单

| 序号 | 交付物 | 文件名 | 说明 |
|------|--------|--------|------|
| 1 | 源代码 | `app.py` + `requirements.txt` | `streamlit run app.py` 一键启动 |
| 2 | 项目说明文档 | `README_new.md` | 功能介绍、运行方法、技术栈 |
| 3 | 运行截图 | `screenshots/*.png` | 展示地图、侧边栏、图表交互 |
| 4 | Agent 交互日志 | `AI_PROMPTS.md` | 完整 AI Coding Agent 对话记录 |
