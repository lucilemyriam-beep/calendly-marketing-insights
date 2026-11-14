import pandas as pd
import streamlit as st

st.set_page_config(page_title='Calendly Marketing Insights', layout='wide')
st.title('Calendly Marketing Insights')
st.caption('Marketing spend and Calendly booking performance | Upload Athena CSV exports')

spend_file = st.sidebar.file_uploader('Marketing spend CSV (date, channel, spend)', type='csv')
bookings_file = st.sidebar.file_uploader('Bookings CSV (optional)', type='csv')
st.sidebar.info('No AWS credentials needed. Export query results as CSV from Athena.')

if spend_file is None:
    st.info('Upload your marketing spend CSV to begin. In Athena, run SELECT date, channel, spend FROM calendly_marketing_db.silver_marketing_spend and download results as CSV.')
    st.stop()

spend = pd.read_csv(spend_file)
required = {'date','channel','spend'}
if not required.issubset(spend.columns):
    st.error('Spend CSV must contain: date, channel, spend')
    st.stop()
spend['date'] = pd.to_datetime(spend['date'], errors='coerce')
spend['spend'] = pd.to_numeric(spend['spend'], errors='coerce')
spend = spend.dropna(subset=['date','channel','spend'])
channels = sorted(spend['channel'].unique())
selected = st.sidebar.multiselect('Channels', channels, default=channels)
spend = spend[spend['channel'].isin(selected)]

st.subheader('Marketing spending')
a,b,c = st.columns(3)
a.metric('Total spend', f"${spend['spend'].sum():,.2f}")
b.metric('Channels', spend['channel'].nunique())
c.metric('Spend records', len(spend))
summary = spend.groupby('channel', as_index=False).agg(total_spend=('spend','sum'), records=('spend','size'))
left,right = st.columns(2)
with left:
    st.markdown('**Spend by channel**')
    st.bar_chart(summary.set_index('channel')['total_spend'])
with right:
    st.markdown('**Daily spend by channel**')
    daily = spend.groupby(['date','channel'])['spend'].sum().unstack(fill_value=0)
    st.line_chart(daily)
st.dataframe(summary.sort_values('total_spend', ascending=False), use_container_width=True)


st.subheader('Calendly bookings and cost per booking')

if bookings_file is None:
    st.warning('Upload your Calendly bookings CSV to view booking analytics.')
    st.stop()

bookings = pd.read_csv(bookings_file)

required_booking_columns = {
    'meeting_date',
    'total_booking_events',
    'unique_bookings',
    'created_events',
    'cancellation_events'
}

if not required_booking_columns.issubset(bookings.columns):
    st.error(
        'Bookings CSV must contain: meeting_date, '
        'total_booking_events, unique_bookings, '
        'created_events, cancellation_events'
    )
    st.stop()

# Clean booking data
bookings['meeting_date'] = pd.to_datetime(
    bookings['meeting_date'], errors='coerce'
)

numeric_columns = [
    'total_booking_events',
    'unique_bookings',
    'created_events',
    'cancellation_events'
]

for column in numeric_columns:
    bookings[column] = pd.to_numeric(
        bookings[column], errors='coerce'
    ).fillna(0)

bookings = bookings.dropna(subset=['meeting_date'])

# Aggregate daily booking activity
daily_bookings = (
    bookings.groupby('meeting_date', as_index=False)[numeric_columns]
    .sum()
    .sort_values('meeting_date')
)

total_bookings = int(daily_bookings['unique_bookings'].sum())
total_created = int(daily_bookings['created_events'].sum())
total_cancelled = int(daily_bookings['cancellation_events'].sum())
total_events = int(daily_bookings['total_booking_events'].sum())

# Booking KPIs
st.markdown('### Booking performance')

col1, col2, col3, col4 = st.columns(4)

col1.metric('Unique bookings', f'{total_bookings:,}')
col2.metric('Created events', f'{total_created:,}')
col3.metric('Cancellation events', f'{total_cancelled:,}')
col4.metric('Total booking events', f'{total_events:,}')

# Booking trends
st.markdown('### Daily booking trends')

st.line_chart(
    daily_bookings.set_index('meeting_date')[
        ['unique_bookings', 'created_events', 'cancellation_events']
    ]
)

# Booking data table
st.markdown('### Daily booking summary')
st.dataframe(daily_bookings, use_container_width=True)

# Spending and bookings date comparison
st.markdown('### Marketing spend and booking efficiency')

spend_start = spend['date'].min()
spend_end = spend['date'].max()

matching_bookings = daily_bookings[
    daily_bookings['meeting_date'].between(spend_start, spend_end)
]

matching_count = int(matching_bookings['unique_bookings'].sum())

if matching_count > 0:
    overall_cpb = spend['spend'].sum() / matching_count
    st.metric('Cost per booking (matching dates)', f'${overall_cpb:,.2f}')
    st.caption(
        'This is an overall spending-to-bookings ratio, '
        'not channel-attributed cost per booking.'
    )
else:
    st.info(
        'No booking dates overlap the uploaded marketing spend dates. '
        'Cost per booking cannot be calculated for matching dates.'
    )

st.info(
    'Channel-level attribution requires a booking source or campaign field. '
    'The current daily bookings export does not contain that information.'
)

st.success('Calendly Marketing Insights dashboard loaded successfully!')
