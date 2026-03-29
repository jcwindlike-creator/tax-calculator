import streamlit as st

st.set_page_config(page_title="个税计算器 Pro", page_icon="🧮", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f5f7fa; }
    section[data-testid="stSidebar"] { display: none; }
    .block-container { padding: 2rem 2rem 4rem; max-width: 820px; }
    label { font-size: 14px !important; font-weight: 500 !important; color: #374151 !important; }
    [data-testid="stMetric"] {
        background: white; border-radius: 12px;
        padding: 1rem 1.2rem; border: 1px solid #e5e7eb;
    }
    [data-testid="stMetricLabel"] { font-size: 13px !important; color: #6b7280 !important; }
    [data-testid="stMetricValue"] { font-size: 20px !important; font-weight: 600 !important; }
    [data-testid="stExpander"] {
        background: white; border-radius: 12px; border: 1px solid #e5e7eb;
    }
    hr { margin: 1.5rem 0; border-color: #e5e7eb; }
</style>
""", unsafe_allow_html=True)


# ── 税率表 ─────────────────────────────────────────────────────

# 综合所得年度税率表（2026年）
ANNUAL_BRACKETS = [
    (36_000,        0.03,  0),
    (144_000,       0.10,  2_520),
    (300_000,       0.20,  16_920),
    (420_000,       0.25,  31_920),
    (660_000,       0.30,  52_920),
    (960_000,       0.35,  85_920),
    (float('inf'),  0.45,  181_920),
]

# 月度税率表（用于年终奖/股权激励 ÷12 后查档）
MONTHLY_BRACKETS = [
    (3_000,         0.03,  0),
    (12_000,        0.10,  210),
    (25_000,        0.20,  1_410),
    (35_000,        0.25,  2_660),
    (55_000,        0.30,  4_410),
    (80_000,        0.35,  7_160),
    (float('inf'),  0.45,  15_160),
]


def calc_annual_tax(taxable: float):
    if taxable <= 0:
        return 0.0, "0%（免税）"
    for limit, rate, deduction in ANNUAL_BRACKETS:
        if taxable <= limit:
            return round(taxable * rate - deduction, 2), f"{int(rate*100)}%"


def calc_single_tax(income: float):
    """年终奖 / 股权激励单独计税：收入 ÷12 查月度档，再 × 全额"""
    if income <= 0:
        return 0.0, "-"
    monthly_eq = income / 12
    for limit, rate, deduction in MONTHLY_BRACKETS:
        if monthly_eq <= limit:
            return round(income * rate - deduction, 2), f"{int(rate*100)}%"


# ══════════════════════════════════════════════════════════════
# 页面标题
# ══════════════════════════════════════════════════════════════
st.markdown("## 🧮 个人所得税计算器 Pro")
st.caption("工资薪金 · 年终奖 · 股权激励 | 2026年税率 | 适用中国境内居民个人")
st.divider()


# ══════════════════════════════════════════════════════════════
# 模块一：工资薪金
# ══════════════════════════════════════════════════════════════
st.markdown("### 一、工资薪金")
col1, col2 = st.columns(2)
with col1:
    monthly_salary = st.number_input("月税前工资（元）", min_value=0, value=30_000, step=500)
with col2:
    social_insurance = st.number_input("五险一金个人缴纳（元/月）", min_value=0, value=4_500, step=100)

st.markdown("**专项附加扣除（元/月）**")
st.caption("不享受的填 0")
c1, c2, c3 = st.columns(3)
with c1:
    children_edu   = st.number_input("子女教育",          min_value=0, value=0, step=500)
    housing_loan   = st.number_input("住房贷款利息",      min_value=0, value=0, step=500)
with c2:
    elderly_care   = st.number_input("赡养老人",          min_value=0, value=0, step=500)
    housing_rent   = st.number_input("住房租金",          min_value=0, value=0, step=500)
with c3:
    continuing_edu = st.number_input("继续教育",          min_value=0, value=0, step=400)
    infant_care    = st.number_input("3岁以下婴幼儿照护", min_value=0, value=0, step=500)

st.divider()

# ══════════════════════════════════════════════════════════════
# 模块二：年终奖
# ══════════════════════════════════════════════════════════════
st.markdown("### 二、年终奖")
st.caption("单独计税优惠政策（不并入综合所得），延续至 2027年12月31日")
bonus = st.number_input("全年一次性奖金金额（元）", min_value=0, value=0, step=1_000)

st.divider()

# ══════════════════════════════════════════════════════════════
# 模块三：股权激励
# ══════════════════════════════════════════════════════════════
st.markdown("### 三、股权激励")
st.caption("适用：限制性股票（RSU）· 股票期权 · 股权奖励 | 优惠计税延续至 2027年12月31日")

equity_type = st.selectbox(
    "股权激励类型",
    ["限制性股票（RSU）",
     "股票期权",
     "股权奖励（其他）"]
)

equity_income = 0

if equity_type == "限制性股票（RSU）":
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        rsu_shares = st.number_input("本次归属股数（股）", min_value=0, value=0, step=100)
    with col_e2:
        rsu_price = st.number_input("归属日收盘价（元/股）", min_value=0.0, value=0.0, step=0.1, format="%.2f")
    equity_income = rsu_shares * rsu_price
    if equity_income > 0:
        st.caption(f"应税收入 = {rsu_shares:,} 股 × ¥{rsu_price:.2f} = **¥{equity_income:,.2f}**")

elif equity_type == "股票期权":
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        opt_shares = st.number_input("行权股数（股）", min_value=0, value=0, step=100)
    with col_e2:
        market_price = st.number_input("行权日市价（元/股）", min_value=0.0, value=0.0, step=0.1, format="%.2f")
    with col_e3:
        grant_price = st.number_input("授予价格（元/股）", min_value=0.0, value=0.0, step=0.1, format="%.2f")
    equity_income = max(opt_shares * (market_price - grant_price), 0)
    if equity_income > 0:
        st.caption(f"应税收入 = {opt_shares:,} 股 × (¥{market_price:.2f} - ¥{grant_price:.2f}) = **¥{equity_income:,.2f}**")

else:
    equity_income = st.number_input("股权激励应税收入（元）", min_value=0, value=0, step=10_000)


# ══════════════════════════════════════════════════════════════
# 核心计算
# ══════════════════════════════════════════════════════════════
BASIC_DEDUCTION = 5_000

monthly_special    = (children_edu + housing_loan + elderly_care +
                      housing_rent + continuing_edu + infant_care)
monthly_taxable    = monthly_salary - BASIC_DEDUCTION - social_insurance - monthly_special
annual_taxable     = max(monthly_taxable, 0) * 12

annual_salary_tax, salary_rate = calc_annual_tax(annual_taxable)
monthly_salary_tax             = round(annual_salary_tax / 12, 2)
after_tax_salary               = round(monthly_salary - social_insurance - monthly_salary_tax, 2)

bonus_tax,  bonus_rate         = calc_single_tax(bonus)
equity_tax, equity_rate        = calc_single_tax(equity_income)

total_annual_tax  = annual_salary_tax + bonus_tax + equity_tax
annual_gross      = monthly_salary * 12 + bonus + equity_income
annual_after_tax  = annual_gross - social_insurance * 12 - total_annual_tax
effective_rate    = round(total_annual_tax / annual_gross * 100, 1) if annual_gross > 0 else 0


# ══════════════════════════════════════════════════════════════
# 结果展示
# ══════════════════════════════════════════════════════════════
st.divider()
st.markdown("### 📊 计算结果")

st.markdown("**工资薪金**")
m1, m2, m3, m4 = st.columns(4)
m1.metric("月应缴个税",  f"¥{monthly_salary_tax:,.0f}")
m2.metric("年应缴个税",  f"¥{annual_salary_tax:,.0f}")
m3.metric("月税后到手",  f"¥{after_tax_salary:,.0f}")
m4.metric("适用税率",    salary_rate)

if bonus > 0:
    st.markdown("**年终奖（单独计税）**")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("奖金金额",  f"¥{bonus:,.0f}")
    b2.metric("应缴个税",  f"¥{bonus_tax:,.0f}")
    b3.metric("税后到手",  f"¥{bonus - bonus_tax:,.0f}")
    b4.metric("适用税率",  bonus_rate)

if equity_income > 0:
    st.markdown("**股权激励（优惠计税）**")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("激励收入",  f"¥{equity_income:,.0f}")
    e2.metric("应缴个税",  f"¥{equity_tax:,.0f}")
    e3.metric("税后到手",  f"¥{equity_income - equity_tax:,.0f}")
    e4.metric("适用税率",  equity_rate)

st.markdown("**全年综合汇总**")
t1, t2, t3, t4 = st.columns(4)
t1.metric("年度总收入",   f"¥{annual_gross:,.0f}")
t2.metric("全年总税额",   f"¥{total_annual_tax:,.0f}")
t3.metric("年度税后收入", f"¥{annual_after_tax:,.0f}")
t4.metric("综合税负率",   f"{effective_rate}%")


# ══════════════════════════════════════════════════════════════
# 明细 & 政策说明
# ══════════════════════════════════════════════════════════════
with st.expander("📋 完整计算明细"):
    st.markdown("**工资薪金**")
    st.markdown(f"""
| 项目 | 月度（元） | 年度（元） |
|------|-----------|-----------|
| 税前收入 | ¥{monthly_salary:,.2f} | ¥{monthly_salary*12:,.2f} |
| 减：基本减除费用 | ¥{BASIC_DEDUCTION:,} | ¥{BASIC_DEDUCTION*12:,} |
| 减：五险一金 | ¥{social_insurance:,.2f} | ¥{social_insurance*12:,.2f} |
| 减：专项附加扣除 | ¥{monthly_special:,.2f} | ¥{monthly_special*12:,.2f} |
| **应纳税所得额** | **¥{max(monthly_taxable,0):,.2f}** | **¥{annual_taxable:,.2f}** |
| 适用税率 | | {salary_rate} |
| **应缴个税** | **¥{monthly_salary_tax:,.2f}** | **¥{annual_salary_tax:,.2f}** |
| **税后到手** | **¥{after_tax_salary:,.2f}** | **¥{after_tax_salary*12:,.2f}** |
    """)

    if bonus > 0:
        st.markdown("**年终奖单独计税**")
        st.markdown(f"""
| 项目 | 金额 |
|------|------|
| 奖金总额 | ¥{bonus:,.2f} |
| ÷12 确定税率档位 | ¥{bonus/12:,.2f}/月 |
| 适用税率 | {bonus_rate} |
| 应缴个税 | ¥{bonus_tax:,.2f} |
| 税后到手 | ¥{bonus - bonus_tax:,.2f} |
        """)

    if equity_income > 0:
        st.markdown("**股权激励优惠计税**")
        st.markdown(f"""
| 项目 | 金额 |
|------|------|
| 股权激励收入 | ¥{equity_income:,.2f} |
| ÷12 确定税率档位 | ¥{equity_income/12:,.2f}/月 |
| 适用税率 | {equity_rate} |
| 应缴个税 | ¥{equity_tax:,.2f} |
| 税后到手 | ¥{equity_income - equity_tax:,.2f} |
        """)

with st.expander("📊 2026年综合所得税率表"):
    st.markdown("""
| 级数 | 全年应纳税所得额 | 税率 | 速算扣除数（元）|
|-----|----------------|------|--------------|
| 1 | 不超过 36,000 元 | 3% | 0 |
| 2 | 36,001 ~ 144,000 元 | 10% | 2,520 |
| 3 | 144,001 ~ 300,000 元 | 20% | 16,920 |
| 4 | 300,001 ~ 420,000 元 | 25% | 31,920 |
| 5 | 420,001 ~ 660,000 元 | 30% | 52,920 |
| 6 | 660,001 ~ 960,000 元 | 35% | 85,920 |
| 7 | 超过 960,000 元 | 45% | 181,920 |
    """)
    st.caption("年终奖/股权激励：将收入÷12查月度档位后乘以全额，不可减除专项附加扣除。优惠政策延续至2027年12月31日。")

st.divider()
st.caption("⚠️ 本工具仅供参考，不构成税务意见。实际纳税以主管税务机关核定为准。")
