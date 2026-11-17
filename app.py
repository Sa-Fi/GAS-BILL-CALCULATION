
import streamlit as st
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from html import escape


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Gas Bill Calculation",
    page_icon="🔥",
    layout="wide"
)


# ==========================================
# 2. FIXED INFORMATION
# ==========================================

BARI_NAME = "Islam Khalifar Bari"
ADDRESS = "South Burischer, Hathazari, Chattogram"

PRICE_PER_BURNER = Decimal("1080")

MEMBERS = [
    {"name": "Kamal Uddin", "burners": Decimal("2.5")},
    {"name": "Jamal Uddin", "burners": Decimal("3.5")},
    {"name": "Fazal Karim", "burners": Decimal("2")},
    {"name": "Nur Uddin", "burners": Decimal("3")},
]


# ==========================================
# 3. CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.header-box {
    background: linear-gradient(135deg, #123c69, #1d70a2);
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 25px;
    text-align: center;
}

.header-box p {
    color: white;
    margin: 5px;
}

.header-title {
    font-size: 32px;
    font-weight: bold;
    color: white;
    margin-bottom: 12px;
}

.header-subtitle {
    font-size: 22px;
    font-weight: bold;
    color: white;
}

.footer-text {
    text-align: center;
    color: #64748b;
    padding: 15px;
    margin-top: 30px;
    border-top: 1px solid #ddd;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================

def to_paisa(amount):
    value = Decimal(str(amount))

    return int(
        (value * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )


def format_taka(amount_paisa):
    taka = Decimal(amount_paisa) / Decimal("100")

    return f"৳{taka:,.2f}"


# ==========================================
# 5. BILL CALCULATION FUNCTION
# ==========================================

def calculate_bill(months, online_total):

    online_total_paisa = to_paisa(online_total)

    member_data = []
    total_main_bill = 0

    # Calculate individual main bills

    for member in MEMBERS:

        main_bill = (
            Decimal(months)
            * member["burners"]
            * PRICE_PER_BURNER
        )

        main_bill_paisa = to_paisa(main_bill)

        total_main_bill += main_bill_paisa

        member_data.append({
            "Member": member["name"],
            "Burners": float(member["burners"]),
            "Main Bill": main_bill_paisa
        })

    # Calculate interest or shortfall

    difference = online_total_paisa - total_main_bill

    # Divide equally among 4 members

    sign = 1 if difference >= 0 else -1

    base_share, remainder = divmod(
        abs(difference),
        len(MEMBERS)
    )

    shares = [
        sign * (base_share + (1 if i < remainder else 0))
        for i in range(len(MEMBERS))
    ]

    # Calculate grand total

    for i, member in enumerate(member_data):

        member["Interest / Adjustment"] = shares[i]

        member["Grand Total"] = (
            member["Main Bill"] + shares[i]
        )

    total_grand_bill = sum(
        member["Grand Total"]
        for member in member_data
    )

    return {
        "members": member_data,
        "total_main_bill": total_main_bill,
        "online_total": online_total_paisa,
        "difference": difference,
        "total_grand_bill": total_grand_bill,
        "reconciled": total_grand_bill == online_total_paisa
    }


# ==========================================
# 6. DASHBOARD HEADER
# ==========================================

st.markdown(
    """
    <div class="header-box">
        <div class="header-title">GAS BILL CALCULATION</div>
        <div class="header-subtitle">Islam Khalifar Bari</div>
        <p>South Burischer, Hathazari, Chattogram</p>
        <p>Monthly Gas Bill Management System</p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# 7. INPUT SECTION
# ==========================================

st.subheader("📝 Bill Information")

col1, col2, col3 = st.columns(3)

with col1:

    months = st.number_input(
        "Number of Months",
        min_value=1,
        max_value=120,
        value=5,
        step=1
    )

with col2:

    online_total = st.number_input(
        "Online Total Amount (৳)",
        min_value=0.0,
        value=59840.0,
        step=100.0,
        format="%.2f"
    )

with col3:

    st.metric(
        "Price Per Burner / Month",
        "৳1,080"
    )


# ==========================================
# 8. CALCULATE BILL
# ==========================================

result = calculate_bill(
    int(months),
    online_total
)

members = result["members"]

total_main_bill = result["total_main_bill"]
online_total_paisa = result["online_total"]
difference = result["difference"]
total_grand_bill = result["total_grand_bill"]


# ==========================================
# 9. BILL SUMMARY
# ==========================================

st.divider()

st.subheader("📊 Bill Summary")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total Main Bill",
        format_taka(total_main_bill)
    )

with col2:

    if difference >= 0:

        st.metric(
            "Total Interest",
            format_taka(difference)
        )

    else:

        st.metric(
            "Total Shortfall",
            format_taka(abs(difference))
        )

with col3:

    st.metric(
        "Online Total Amount",
        format_taka(online_total_paisa)
    )


# ==========================================
# 10. INDIVIDUAL BILL TABLE
# ==========================================

st.divider()

st.subheader("👥 Individual Member Bill")

table_data = []

for member in members:

    table_data.append({
        "Member Name": member["Member"],
        "Burners": member["Burners"],
        "Main Bill (৳)": member["Main Bill"] / 100,
        "Interest / Adjustment (৳)": (
            member["Interest / Adjustment"] / 100
        ),
        "Grand Total (৳)": member["Grand Total"] / 100
    })

df = pd.DataFrame(table_data)

st.dataframe(
    df,
    width="stretch",
    hide_index=True,
    column_config={
        "Burners": st.column_config.NumberColumn(
            "Burners",
            format="%.1f"
        ),
        "Main Bill (৳)": st.column_config.NumberColumn(
            "Main Bill (৳)",
            format="৳%.2f"
        ),
        "Interest / Adjustment (৳)": st.column_config.NumberColumn(
            "Interest / Adjustment (৳)",
            format="৳%.2f"
        ),
        "Grand Total (৳)": st.column_config.NumberColumn(
            "Grand Total (৳)",
            format="৳%.2f"
        )
    }
)


# ==========================================
# 11. FINAL TOTAL
# ==========================================

st.divider()

st.subheader("💰 Final Bill Calculation")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Total Individual Grand Bills",
        format_taka(total_grand_bill)
    )

with col2:

    st.metric(
        "Online Total",
        format_taka(online_total_paisa)
    )


# ==========================================
# 12. RECONCILIATION CHECK
# ==========================================

st.divider()

st.subheader("🔍 Amount Reconciliation")

if result["reconciled"]:

    st.success(
        "Calculation Successful! "
        "All individual bills match the online total."
    )

else:

    st.error(
        "Reconciliation failed. Please check the calculation."
    )

if difference >= 0:

    st.info(
        f"Total Interest: {format_taka(difference)}. "
        "Interest is divided equally among all 4 members."
    )

else:

    st.warning(
        f"Total Shortfall: {format_taka(abs(difference))}. "
        "Shortfall is divided equally among all 4 members."
    )


# ==========================================
# 13. INDIVIDUAL BILL CHART
# ==========================================

st.divider()

st.subheader("📈 Individual Grand Total Comparison")

chart_df = pd.DataFrame({
    "Member": [m["Member"] for m in members],
    "Grand Total (৳)": [
        m["Grand Total"] / 100
        for m in members
    ]
})

st.bar_chart(
    chart_df,
    x="Member",
    y="Grand Total (৳)",
    width="stretch"
)


# ==========================================
# 14. CSV DOWNLOAD
# ==========================================

st.divider()

st.subheader("📥 Download Bill Report")

csv_data = df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="⬇️ Download CSV Report",
    data=csv_data,
    file_name="gas_bill_report.csv",
    mime="text/csv",
    width="stretch"
)


# ==========================================
# 15. PRINTABLE HTML BILL
# ==========================================

html_rows = ""

for member in members:

    html_rows += f"""
    <tr>
        <td>{escape(member["Member"])}</td>
        <td>{member["Burners"]}</td>
        <td>{format_taka(member["Main Bill"])}</td>
        <td>{format_taka(member["Interest / Adjustment"])}</td>
        <td>{format_taka(member["Grand Total"])}</td>
    </tr>
    """

difference_label = (
    "Total Interest" if difference >= 0
    else "Total Shortfall"
)

difference_value = abs(difference)

print_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Gas Bill Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 35px;
    color: #222;
}}

.header {{
    text-align: center;
    margin-bottom: 30px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 25px;
}}

th, td {{
    border: 1px solid #ccc;
    padding: 12px;
    text-align: center;
}}

th {{
    background-color: #eaf2f8;
}}

.summary {{
    margin-top: 25px;
    line-height: 1.9;
}}

.footer {{
    margin-top: 50px;
    text-align: center;
    color: #666;
}}

@media print {{
    body {{
        margin: 15mm;
    }}

    button {{
        display: none;
    }}
}}

</style>
</head>

<body>

<div class="header">

    <h1>GAS BILL CALCULATION</h1>

    <h2>{escape(BARI_NAME)}</h2>

    <p>{escape(ADDRESS)}</p>

    <p>Monthly Gas Bill Management System</p>

</div>

<h3>Bill Information</h3>

<p><strong>Number of Months:</strong> {months}</p>

<p><strong>Price Per Burner:</strong> ৳1,080</p>

<table>

<thead>
<tr>
    <th>Member Name</th>
    <th>Burners</th>
    <th>Main Bill</th>
    <th>Interest / Adjustment</th>
    <th>Grand Total</th>
</tr>
</thead>

<tbody>
{html_rows}
</tbody>

</table>

<div class="summary">

    <h3>Final Summary</h3>

    <p><strong>Total Main Bill:</strong>
    {format_taka(total_main_bill)}</p>

    <p><strong>{difference_label}:</strong>
    {format_taka(difference_value)}</p>

    <p><strong>Online Total Amount:</strong>
    {format_taka(online_total_paisa)}</p>

    <p><strong>Total Individual Grand Bills:</strong>
    {format_taka(total_grand_bill)}</p>

    <p><strong>Reconciliation:</strong>
    {"Successful" if result["reconciled"] else "Failed"}</p>

</div>

<div class="footer">
    <p>Made by Md. Safi Ullah</p>
</div>

<button onclick="window.print()">Print Bill</button>

</body>
</html>
"""

st.download_button(
    label="🖨️ Download Printable Bill",
    data=print_html.encode("utf-8"),
    file_name="gas_bill_print.html",
    mime="text/html",
    width="stretch"
)


# ==========================================
# 16. FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "Gas Bill Calculation System | Made by Md. Safi Ullah"
)
