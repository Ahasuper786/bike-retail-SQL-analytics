from pathlib import Path
import importlib.util

MODULE = Path(__file__).resolve().parents[1] / "src" / "retail_analytics.py"
spec = importlib.util.spec_from_file_location("retail_analytics", MODULE)
analytics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analytics)


def test_net_revenue_percentage_discount():
    assert analytics.net_revenue(100.0, 0.20, 2) == 160.0


def test_zero_discount():
    assert analytics.net_revenue(250.0, 0.0, 3) == 750.0


def test_full_discount():
    assert analytics.net_revenue(250.0, 1.0, 3) == 0.0
