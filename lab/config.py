"""All the knobs in one place. Changing these mid-test invalidates the test."""

LAB_NAME = "Bunny Paper Lab"

START_CAPITAL_GBP = 1000.0
TEST_DAYS = 7

# Coins traded against GBP. (Kraken pair, Coinbase product)
UNIVERSE = {
    "BTC": ("XBTGBP", "BTC-GBP"),
    "ETH": ("ETHGBP", "ETH-GBP"),
    "SOL": ("SOLGBP", "SOL-GBP"),
    "XRP": ("XRPGBP", "XRP-GBP"),
    "ADA": ("ADAGBP", "ADA-GBP"),
    "LINK": ("LINKGBP", "LINK-GBP"),
}
REGIME_COIN = "BTC"

# --- Costs (checked 24 Nov 2026) ---------------------------------------
# Kraken Pro, Tier 1 (<$2.5k 30-day volume): maker 0.40%, taker 0.80%.
# The bot simulates market orders, so it pays the taker fee on every fill.
FEE_RATE = 0.0080
SLIPPAGE = {"BTC": 0.0005, "ETH": 0.0005}  # per side
SLIPPAGE_DEFAULT = 0.0010                   # smaller coins: wider spreads

# --- Risk (cautious profile) -------------------------------------------
RISK_PER_TRADE = 0.01        # 1% of equity lost if the stop is hit
MAX_POSITION_FRACTION = 0.25 # never more than 25% of equity in one coin
MAX_POSITIONS = 4
MIN_ORDER_GBP = 10.0
DAILY_LOSS_LIMIT = 0.03      # -3% on the UTC day: no new entries until tomorrow
KILL_SWITCH_DRAWDOWN = 0.10  # -10% from start: close everything and stop
LEVERAGE = 1.0               # none
ALLOW_SHORTS = False

# --- Strategy parameters (fixed in advance, not tuned on any data) -----
BAR_HOURS = 4
REGIME_EMA_FAST = 50
REGIME_EMA_SLOW = 200

TREND_BREAKOUT_BARS = 30     # 5-day high
TREND_EXIT_BARS = 15         # 2.5-day low trailing exit
TREND_STOP_ATR = 2.5

MR_RSI_LEN = 14
MR_RSI_ENTRY = 30
MR_BB_LEN = 20
MR_BB_STD = 2.0
MR_STOP_ATR = 2.0
MR_MAX_BARS = 12             # give up after 2 days

ATR_LEN = 14
ENABLE_TREND = True
ENABLE_MEANREV = True
