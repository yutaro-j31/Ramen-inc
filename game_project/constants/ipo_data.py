# constants/ipo_data.py
from typing import Dict, Any, Tuple, List

# --- 自社IPOシステム関連 ---
IPO_ELIGIBILITY_CRITERIA: Dict[str, Any] = {
    "min_weeks_in_operation": 52 * 3, 
    "min_annual_revenue_estimate": 500_000_000, 
    "min_cumulative_profit": 100_000_000,
    "required_departments": ["investment", "hr"],
}
IPO_UNDERWRITER_FEE_FIXED: float = 20_000_000
IPO_UNDERWRITER_FEE_RATE_ON_PROCEEDS: float = 0.04
IPO_VALUATION_PSR_RANGE: Tuple[float, float] = (0.5, 3.0)
IPO_VALUATION_PER_RANGE: Tuple[float, float] = (10.0, 25.0)
IPO_SHARES_TO_OFFER_PERCENT_RANGE: Tuple[float, float] = (0.15, 0.30)
IPO_PROCESS_WEEKS: int = 12
IPO_ROADSHOW_WEEKS: int = 4
IPO_INVESTOR_DEMAND_BASE_LEVEL: int = 50
IPO_INVESTOR_DEMAND_FACTORS: Dict[str, Any] = { 
    "economic_phase_bonus": {"好景気": 15, "普通": 0, "不景気": -25}, 
    "profit_trend_bonus_max": 20, 
    "revenue_trend_bonus_max": 15, 
    "valuation_attractiveness_factor": 0.15, 
    "random_event_max_change": 10 
}
IPO_DEMAND_LEVEL_THRESHOLDS: Dict[str, int] = {
    "very_high": 85, "high": 65, "moderate": 40, "low": 20
}
IPO_FAILURE_DEMAND_THRESHOLD: int = IPO_DEMAND_LEVEL_THRESHOLDS["low"]
IPO_PRICING_ADJUSTMENT_ON_DEMAND: Dict[str, float] = { "very_high": 0.15, "high": 0.05, "moderate": 0.0, "low": -0.10, "very_low": -0.25 }
IPO_SHARES_OFFERED_ADJUSTMENT_ON_DEMAND: Dict[str, float] = { "very_high": 0.05, "high": 0.02, "moderate": 0.0, "low": -0.05, "very_low": -0.10 }
