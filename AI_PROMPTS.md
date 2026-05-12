# Agent 交互日志

**团队名称：** 三个和尚没水喝
**成员名单：** 晋清杨、李逸宸、王一航
**使用的 AI Coding Agent 工具：** Claude Code + DeepSeek V4 Pro

---

## 🤖 交互记录导出说明

根据比赛要求，提交与 AI Coding Agent 的真实交互记录。

---

## 📋 对话记录总览

本次参赛共进行 **3 次主要会话**，涵盖项目从初始化到功能强化的完整开发过程。

| 会话文件 | 时间 | 主要内容 |
|---------|------|---------|
| conversation-2026-05-08-135049.txt | 13:50 | Phase 1 MVP 实现、pydeck bug 修复 |
| conversation-2026-05-08-153111.txt | 15:31 | 项目分析、进阶关卡完成、单元测试 |
| conversation-2026-05-08-154333.txt | 15:43 | 科技风格 UI 升级、多层地图渲染 |

---

## 🏗️ 会话一：Phase 1 MVP 实现（conversation-2026-05-08-135049.txt）

**时长：** 约 6 分钟  
**目标：** 根据 README 需求生成设计文档，实现最小可运行 MVP

### 1.1 设计文档生成

通过 Claude Code 分析项目需求，生成 `DESIGN.md`，包含：

- **应用架构**：单页 Web 看板（Streamlit）
- **技术栈**：Python + Streamlit + pandas + pydeck + plotly + numpy
- **需求实现方案**：基础关卡 3 项 + 进阶关卡 3 项
- **页面布局设计**：ASCII 布局图 + 配色方案
- **文件结构与交付件**：仓库结构、硬核交付物、Git Tag 打卡方式
- **开发与运行指南**：环境准备、启动命令、测试命令

### 1.2 Phase 1 基础 MVP 实现

**已实现功能：**

| 功能 | 实现方式 |
|------|---------|
| 数据加载 | pandas.read_csv() + @st.cache_data 缓存 |
| 2D 散点地图 | pydeck.ScatterplotLayer，RSRP 三色映射 |
| RSRP 颜色映射 | 绿 (> -90) / 橙 (-110~-90) / 红 (< -110) |
| KPI 指标卡 | 总采样点、平均 RSRP、平均 SINR、平均速率 |
| 频段柱状图 | plotly.express.bar 按 Band 聚合基站数 |
| 终端占比饼图 | plotly.express.pie 环形图 |
| 数据预览 | st.expander 折叠区，默认收起 |
| 悬停提示 | 地图点悬停显示 CellID/Band/RSRP/SINR/速率/终端类型 |

**启动方式：**
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 1.3 Bug 修复：pydeck 序列化错误

**问题：** 运行时报错 `TypeError: vars() argument must have __dict__ attribute`

**根因：** `get_fill_color=get_color_array(...)` 传入的是 numpy 二维数组，pydeck 序列化时对 numpy 标量调用 `vars()`，而 numpy 类型没有 `__dict__` 属性。

**修复方案：** 将颜色分量以独立的 R/G/B/A 列（纯 Python int）写入 DataFrame，然后用列名引用：
```python
get_fill_color=["color_r", "color_g", "color_b", "color_a"]
```

---

## 🚀 会话二：进阶关卡实现（conversation-2026-05-08-153111.txt）

**时长：** 约 5 分钟  
**目标：** 完成所有进阶关卡并添加单元测试

### 2.1 项目现状分析

Claude Code 完整分析项目后，输出报告：

| 类别 | 状态 |
|------|------|
| 基础关卡 | ✅ 全部完成 |
| 进阶关卡 | ❌ 未实现 |
| 运行截图 | ❌ 缺失 |
| AI_PROMPTS.md | ⚠️ 仅模板，未填写 |
| Git Tag | ❌ 未打 |

### 2.2 进阶关卡完成

**1. 侧边栏联动筛选 ✅**

- 频段多选（n28 / n41 / n78），默认全选
- RSRP 滑动条（-120 ~ -70 dBm 范围调节）
- 终端类型多选（Smartphone / CPE / IoT）
- 筛选器变化时地图和图表实时联动更新
- KPI 指标卡片也基于筛选后数据计算

**2. 3D 地图视觉增强 ✅**

- 侧边栏增加 "2D 散点图 / 3D 柱状图" 切换按钮
- 3D 模式下使用 pydeck ColumnLayer，柱体高度随下载速率变化
- 倾斜 45° 视角展示 3D 效果

**3. 代码注释 + 单元测试 ✅**

- 核心函数添加了规范 docstring
- 新建 `test_app.py`，覆盖 4 个核心模块：
  - `test_load_data` — 数据加载验证
  - `TestColorMapping` — 颜色映射边界测试（5 个）
  - `TestFilterData` — 筛选逻辑测试（4 个）
  - `TestAggregation` — 聚合计算测试（4 个）
- **14 个测试全部通过**
- `requirements.txt` 补充了 pytest

---

## 🎨 会话三：科技风格 UI 升级（conversation-2026-05-08-154333.txt）

**时长：** 约 7 分钟  
**目标：** 将地图和看板做得更精致，科技效果更强

### 3.1 暗色科技主题

- 地图底图切换为 `mapbox/dark-v10` 暗色主题
- 全页暗色科技风 CSS（#0a0e17 深空底色）
- 所有控件、卡片、图表统一适配暗色主题

### 3.2 赛博朋克配色方案

| 信号等级 | 旧颜色 | 新颜色 |
|---------|--------|--------|
| 优秀 | 绿色 #2ECC71 | 青色 #00E5FF（霓虹光晕） |
| 中等 | 橙色 #F39C12 | 电紫 #AA00FF |
| 弱覆盖 | 红色 #E74C3C | 霓虹粉 #FF0055 |

### 3.3 多层地图复合渲染

- **HeatmapLayer 热力云（新增）**：信号强度以辉光云效果呈现
- **ScatterplotLayer 描边增强（2D）**：点带发光边框，更清晰
- **ColumnLayer 平滑化（3D）**：柱体更圆滑，配合暗色底图更突出

### 3.4 玻璃态 UI

- **KPI 卡片**：backdrop-filter: blur 玻璃拟态 + 渐变文字 + 悬浮发光动效
- **工具提示**：暗色半透明 + 网格布局 + 按数据类型配色的值
- **图例**：带霓虹光晕色块

### 3.5 Plotly 暗色图表

- 双图表统一 `plotly_dark` 模板，透明背景，科技色系
- 柱状图/饼图颜色与地图配色一致（青/紫/粉）

### 3.6 代码质量保证

- 14 项单元测试全部通过
- 筛选逻辑完全保留，新增热力云开关
- 新增 weight 列预计算，避免运行时重复计算

---

## 📊 开发过程总结

### 技术演进路径

```
Phase 1 MVP → 修复 Bug → 进阶关卡 → 单元测试 → 科技风格升级
```

### 关键技术决策

| 决策点 | 选择 | 原因 |
|--------|------|------|
| 地图方案 | pydeck | 支持 2D/3D 切换 |
| 图表方案 | plotly | 交互性优，与 Streamlit 集成好 |
| 颜色映射 | 三色区间（青/紫/粉） | 赛博朋克风格，科技感强 |
| 联动机制 | Streamlit 事件驱动 | 筛选器变化自动触发重渲染 |

### 文件变更记录

| 文件 | 操作 | 说明 |
|------|------|------|
| DESIGN.md | 新增 | 详细设计文档 |
| app.py | 新增/修改 | 主应用代码 |
| requirements.txt | 新增 | Python 依赖 |
| test_app.py | 新增 | 单元测试（14 个测试用例） |
| README.md | 修改 | 补充一键启动说明 |

### 测试通过情况

```
============================= test session starts =============================
platform win32 -- Python 3.13.11, pytest-9.0.3, pluggy-1.5.0
collected 14 items

test_app.py::test_load_data PASSED
test_app.py::TestColorMapping::test_excellent_signal PASSED
test_app.py::TestColorMapping::test_poor_signal PASSED
test_app.py::TestColorMapping::test_medium_signal PASSED
test_app.py::TestColorMapping::test_boundary_negative_90 PASSED
test_app.py::TestColorMapping::test_boundary_negative_110 PASSED
test_app.py::TestFilterData::test_band_filter PASSED
test_app.py::TestFilterData::test_rsrp_range_filter PASSED
test_app.py::TestFilterData::test_terminal_filter PASSED
test_app.py::TestFilterData::test_combined_filter PASSED
test_app.py::TestAggregation::test_band_aggregation PASSED
test_app.py::TestAggregation::test_terminal_aggregation PASSED
test_app.py::TestAggregation::test_avg_metrics PASSED
test_app.py::TestAggregation::test_data_integrity PASSED

============================== 14 passed in 0.XX s ==============================
```

---
## 交付物清单

| # | 交付物 | 文件 | 状态 |
|---|--------|------|------|
| 1 | 源代码 | `app.py`, `test_app.py`, `requirements.txt` | ✅ |
| 2 | 项目说明文档 | `README.md` | ✅ |
| 3 | 运行截图 | `screenshots/` | ✅ |
| 4 | Agent 交互日志 | `AI_PROMPTS.md`（本文件） | ✅ |
| 4 | basic-done tag | GitHub release | ✅手动release完成 |
| 4 | advanced-done tag | GitHub release | ✅手动release完成 |
---

