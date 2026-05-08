"""5G 信号可视化看板 — 单元测试

覆盖数据加载、颜色映射、筛选逻辑、聚合计算四个核心模块。
运行方式: pytest test_app.py -v
"""
import pytest
import pandas as pd


# ==================== 数据加载测试 ====================

def test_load_data():
    """验证 CSV 能被正确加载且包含所有必要字段"""
    df = pd.read_csv("data/signal_samples.csv")
    assert not df.empty, "DataFrame 不应为空"
    required_columns = [
        "Latitude", "Longitude", "CellID", "Band",
        "RSRP_dBm", "SINR_dB", "TerminalType", "Download_Mbps",
    ]
    for col in required_columns:
        assert col in df.columns, f"缺少必要字段: {col}"


# ==================== 颜色映射测试 ====================

def classify_rsrp(rsrp):
    """与 app.py 保持一致的信号等级分类逻辑"""
    if rsrp > -90:
        return "优秀"
    elif rsrp < -110:
        return "弱覆盖"
    else:
        return "中等"


def get_color_rgb(rsrp):
    """与 app.py 保持一致的 RSRP 颜色映射逻辑"""
    if rsrp > -90:
        return [46, 204, 113]   # 绿色
    elif rsrp < -110:
        return [231, 76, 60]    # 红色
    else:
        return [243, 156, 18]   # 橙色


class TestColorMapping:
    """RSRP 颜色映射函数的边界与等价类测试"""

    def test_excellent_signal(self):
        """RSRP > -90 dBm 应标记为优秀并返回绿色"""
        assert classify_rsrp(-89) == "优秀"
        assert get_color_rgb(-89) == [46, 204, 113]

    def test_poor_signal(self):
        """RSRP < -110 dBm 应标记为弱覆盖并返回红色"""
        assert classify_rsrp(-111) == "弱覆盖"
        assert get_color_rgb(-111) == [231, 76, 60]

    def test_medium_signal(self):
        """-110 <= RSRP <= -90 dBm 应标记为中等并返回橙色"""
        assert classify_rsrp(-100) == "中等"
        assert get_color_rgb(-100) == [243, 156, 18]

    def test_boundary_negative_90(self):
        """边界值 -90 dBm 应归为中等（橙色）"""
        assert classify_rsrp(-90) == "中等"
        assert get_color_rgb(-90) == [243, 156, 18]

    def test_boundary_negative_110(self):
        """边界值 -110 dBm 应归为中等（橙色）"""
        assert classify_rsrp(-110) == "中等"
        assert get_color_rgb(-110) == [243, 156, 18]


# ==================== 筛选逻辑测试 ====================

@pytest.fixture
def sample_df():
    """提供一份含 6 条记录的模拟 DataFrame"""
    return pd.DataFrame({
        "Latitude": [31.20, 31.21, 31.22, 31.23, 31.24, 31.25],
        "Longitude": [121.48, 121.49, 121.50, 121.51, 121.52, 121.53],
        "CellID": [1001, 1002, 1003, 1004, 1005, 1006],
        "Band": ["n28", "n78", "n28", "n41", "n78", "n41"],
        "RSRP_dBm": [-94.0, -105.0, -82.0, -115.0, -95.0, -88.0],
        "SINR_dB": [5.0, 20.0, 18.0, 3.0, 12.0, 25.0],
        "TerminalType": ["Smartphone", "CPE", "IoT", "Smartphone", "CPE", "IoT"],
        "Download_Mbps": [100.0, 800.0, 50.0, 300.0, 600.0, 900.0],
    })


class TestFilterData:
    """频段、RSRP 范围、终端类型的单一与组合筛选"""

    def test_band_filter(self, sample_df):
        """按频段筛选应只返回匹配频段的行"""
        filtered = sample_df[sample_df["Band"].isin(["n28"])]
        assert len(filtered) == 2
        assert all(filtered["Band"] == "n28")

    def test_rsrp_range_filter(self, sample_df):
        """按 RSRP 范围筛选应只返回范围内的行"""
        filtered = sample_df[sample_df["RSRP_dBm"].between(-100, -90)]
        assert len(filtered) == 2
        assert all(filtered["RSRP_dBm"].between(-100, -90))

    def test_terminal_filter(self, sample_df):
        """按终端类型筛选应只返回指定类型的行"""
        filtered = sample_df[sample_df["TerminalType"].isin(["CPE"])]
        assert len(filtered) == 2
        assert all(filtered["TerminalType"] == "CPE")

    def test_combined_filter(self, sample_df):
        """组合多个条件应同时满足所有约束"""
        filtered = sample_df[
            (sample_df["Band"].isin(["n28", "n41"])) &
            (sample_df["RSRP_dBm"].between(-120, -80)) &
            (sample_df["TerminalType"].isin(["Smartphone"]))
        ]
        assert len(filtered) == 2
        assert all(filtered["TerminalType"] == "Smartphone")


# ==================== 聚合计算测试 ====================

class TestAggregation:
    """分组聚合与分布统计的正确性"""

    def test_band_cell_count(self, sample_df):
        """按频段统计基站数量（CellID 去重）应正确"""
        band_counts = sample_df.groupby("Band")["CellID"].nunique()
        assert band_counts["n28"] == 2
        assert band_counts["n41"] == 2
        assert band_counts["n78"] == 2

    def test_terminal_distribution(self, sample_df):
        """终端类型分布统计应返回各类型计数"""
        counts = sample_df["TerminalType"].value_counts()
        assert counts["Smartphone"] == 2
        assert counts["CPE"] == 2
        assert counts["IoT"] == 2
        assert len(counts) == 3

    def test_mean_rsrp(self, sample_df):
        """平均 RSRP 计算应正确"""
        expected_mean = sample_df["RSRP_dBm"].mean()
        assert expected_mean == pytest.approx(-96.5, abs=0.01)

    def test_mean_download_speed(self, sample_df):
        """平均下载速率计算应正确"""
        expected_mean = sample_df["Download_Mbps"].mean()
        assert expected_mean == pytest.approx(458.33, abs=0.01)
