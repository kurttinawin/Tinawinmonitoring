import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="TINAWIN MONITORING", page_icon="📊", initial_sidebar_state="expanded")

# Apply custom styles for the background and font
st.markdown(
    """
    <style>
    /* Change the background color to orange */
    .reportview-container {
        background: #FFA500;
        color: white;
        font-family: 'Roboto', sans-serif;
    }
    .sidebar .sidebar-content {
        background: #FFA500;
        font-family: 'Roboto', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Roboto', sans-serif;
        font-weight: bold;
    }
    /* Adding Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Daily Remark Summary')

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df[~df['Remark By'].isin(['KFTINAWIN', 'KPILUSTRISIMO','SPMADRID'])]
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    def calculate_combined_summary(df):
        summary_table = pd.DataFrame(columns=[
            'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #'
        ])

        for date, group in df.groupby(df['Date'].dt.date):
            accounts = group[group['Remark'] != 'Broken Promise']['Account No.'].nunique()
            total_dialed = group[group['Remark'] != 'Broken Promise']['Account No.'].count()

            connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            connected_acc = group[group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

            ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

            call_drop_count = group[group['Call Status'] == 'DROPPED']['Account No.'].count()
            call_drop_ratio = (call_drop_count / connected * 100) if connected != 0 else None

            summary_table = pd.concat([summary_table, pd.DataFrame([{
                'Day': date,
                'ACCOUNTS': accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                'CONNECTED ACC': connected_acc,
                'PTP ACC': ptp_acc,
                'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                'CALL DROP #': call_drop_count,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
            }])], ignore_index=True)

        return summary_table

    st.write("## Overall Combined Summary Table")
    combined_summary_table = calculate_combined_summary(df)
    st.write(combined_summary_table, container_width=True)

    def calculate_summary(df, remark_type, remark_by=None):
        summary_table = pd.DataFrame(columns=[
            'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #'
        ])

        for date, group in df.groupby(df['Date'].dt.date):
            accounts = group[(group['Remark Type'] == remark_type) | ((group['Remark'] != 'Broken Promise') & (group['Remark Type'] == 'Follow Up') & (group['Remark By'] == remark_by))]['Account No.'].nunique()
            total_dialed = group[(group['Remark Type'] == remark_type) | ((group['Remark'] != 'Broken Promise') & (group['Remark Type'] == 'Follow Up') & (group['Remark By'] == remark_by))]['Account No.'].count()

            connected = group[(group['Call Status'] == 'CONNECTED') & (group['Remark Type'] == remark_type)]['Account No.'].count()
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            connected_acc = group[(group['Call Status'] == 'CONNECTED') & (group['Remark Type'] == remark_type)]['Account No.'].nunique()

            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

            ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0) & (group['Remark Type'] == remark_type)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

            call_drop_count = group[(group['Call Status'] == 'DROPPED') & (group['Remark Type'] == remark_type)]['Account No.'].count()
            call_drop_ratio = (call_drop_count / connected * 100) if connected != 0 else None

            summary_table = pd.concat([summary_table, pd.DataFrame([{
                'Day': date,
                'ACCOUNTS': accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                'CONNECTED ACC': connected_acc,
                'PTP ACC': ptp_acc,
                'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                'CALL DROP #': call_drop_count,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
            }])], ignore_index=True)

        return summary_table

    col1, col2 = st.columns(2)

    with col1:
        st.write("## Overall Predictive Summary Table")
        overall_summary_table = calculate_summary(df, 'Predictive', 'SYSTEM')
        st.write(overall_summary_table)

    with col2:
        st.write("## Overall Manual Summary Table")
        overall_manual_table = calculate_summary(df, 'Outgoing')
        st.write(overall_manual_table)

    col3, col4 = st.columns(2)

    with col3:
        st.write("## Summary Table by Cycle Predictive")
        for cycle, cycle_group in df.groupby('Service No.'):
            st.write(f"Cycle: {cycle}")
            summary_table = calculate_summary(cycle_group, 'Predictive', 'SYSTEM')
            st.write(summary_table)

    with col4:
        st.write("## Summary Table by Cycle Manual")
        for manual_cycle, manual_cycle_group in df.groupby('Service No.'):
            st.write(f"Cycle: {manual_cycle}")
            summary_table = calculate_summary(manual_cycle_group, 'Outgoing')
            st.write(summary_table)

    col5, col6 = st.columns(2)

    with col5:
        st.write("## Summary Table by Collector per Day")

        # Add date filter for Collector Table
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()

        try:
            start_date, end_date = st.date_input("Select date range for Collector", [min_date, max_date], min_value=min_date, max_value=max_date)
        except ValueError:
            start_date, end_date = None, None

        if start_date and end_date:
            filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
        else:
            filtered_df = df  # If no date range is selected, show all data

        # Initialize an empty DataFrame for the summary table by collector
        collector_summary = pd.DataFrame(columns=[
            'Day', 'Collector', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
        ])

        for (date, collector), collector_group in filtered_df[~filtered_df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([filtered_df['Date'].dt.date, 'Remark By']):
            total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = collector_group[collector_group['Status'].str.contains('POSITIVE CONTACT', na=False)]['Account No.'].nunique()
            ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            balance_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['Balance'] != 0)]['Balance'].sum()

            collector_summary = pd.concat([collector_summary, pd.DataFrame([{
                'Day': date,
                'Collector': collector,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'PTP Amount': ptp_amount,
                'Balance Amount': balance_amount,
            }])], ignore_index=True)

        totals_row = {
            'Day': 'Total',
            'Collector': '',
            'Total Connected': collector_summary['Total Connected'].sum(),
            'Total PTP': collector_summary['Total PTP'].sum(),
            'Total RPC': collector_summary['Total RPC'].sum(),
            'PTP Amount': collector_summary['PTP Amount'].sum(),
            'Balance Amount': collector_summary['Balance Amount'].sum(),
        }
        collector_summary = pd.concat([collector_summary, pd.DataFrame([totals_row])], ignore_index=True)

        st.write(collector_summary)
