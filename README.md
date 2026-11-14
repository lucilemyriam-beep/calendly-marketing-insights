# Calendly Marketing Insights Streamlit dashboard

AWS data engineering and Streamlit analytics portfolio project

Live dashboard: Open the deployed Streamlit app 
https://calendly-marketing-insights-ybz7gq8d8xgmrgl8ysxbdr.streamlit.app/

Project overview
This project combines marketing advertising spend with Calendly booking activity to demonstrate an AWS data pipeline, SQL analysis, and a deployed interactive Streamlit dashboard. Users can upload CSV exports from Amazon Athena to explore marketing spend and booking trends without providing AWS credentials to the app.
Architecture and data flow
1. Marketing spend and Calendly data are stored in Amazon S3.
2. AWS Glue crawlers discover the available datasets and register table schemas in the AWS Glue Data Catalog.
3. Bronze-to-Silver transformation scripts prepare curated datasets; the marketing spend Silver dataset is cataloged as calendly_marketing_db.silver_marketing_spend.
4. Amazon Athena queries the Silver data and creates a Gold aggregation view, calendly_marketing_db.gold_marketing_spend.
5. Athena query results are exported as CSV files and uploaded into the Streamlit dashboard.
6. Streamlit Community Cloud serves the app from this GitHub repository.
The deployed dashboard uses manual CSV uploads; it does not automatically refresh from AWS or directly query Athena.

Technologies
- AWS S3, AWS Glue, AWS Glue Data Catalog, Amazon Athena
- SQL, Python, pandas, Streamlit
- GitHub and Streamlit Community Cloud
Data models
Marketing spend Silver table: date, channel, spend.

Gold marketing view: aggregated by channel with channel, total_spend, total_records, and average_spend.

Daily booking export: meeting_date, total_booking_events, unique_bookings, created_events, and cancellation_events.
Dashboard features
- Total advertising spend, number of channels, and spending records
- Spend by channel and daily spending trends
- Daily booking activity, created events, cancellations, and unique bookings
- Overall spend-to-bookings ratio for comparable dates
- Channel filters and CSV uploads
Validated example results
- Total marketing spend: $49,488.70
- Marketing channels: 3
- Spend records: 89
- Unique bookings: 303
- Created events: 245
- Cancellation events: 97
- Cost per booking (matching dates): $1,075.84
These figures are from the sample CSV exports used during validation; results change with uploaded files and filters. Booking events and unique bookings are different measures and should not be summed interchangeably.
Run locally
python -m pip install -r requirements.txt
python -m streamlit run app.py
Upload a marketing spend CSV with columns date, channel, spend. Upload a compatible booking export if you want booking analysis. The current deployed version supports the daily booking summary columns listed above.
SQL examples
SELECT date, channel, spend
FROM calendly_marketing_db.silver_marketing_spend;
CREATE OR REPLACE VIEW calendly_marketing_db.gold_marketing_spend AS
SELECT
    channel,
    ROUND(SUM(spend), 2) AS total_spend,
    COUNT(*) AS total_records,
    ROUND(AVG(spend), 2) AS average_spend
FROM calendly_marketing_db.silver_marketing_spend
GROUP BY channel;
Repository contents
- app.py — Streamlit dashboard
- requirements.txt — Python dependencies
- calendly_bronze_to_silver_script.txt — Calendly transformation script
- calendly_silver_to_gold_script.txt — Gold-layer transformation script
- marketing_spend_bronze_to_silver_script.txt — marketing spend transformation script
- Architecture .drawio files and solution-design PDF — design documentation
- screenshots/booking-performance.png — deployed dashboard evidence
Limitations and future enhancements
- The daily booking export lacks source/campaign attribution; therefore channel-specific cost per booking cannot be calculated reliably.
- The reported cost per booking is an overall ratio using matching spend and booking dates, not causal attribution.
- CSV uploads are manual and session-based. Automated refresh, webhook ingestion, scheduling, Delta Lake storage, CI/CD, retries, and production-grade security controls are not established by this dashboard deployment.
- Validate date coverage, booking definitions, and cancellations before using results for business decisions.
Data privacy
Do not commit customer-identifying Calendly data, secrets, access keys, or sensitive exports to a public repository. Use anonymized/sample data for public demonstrations.

## Run locally
1. Install Python 3.10 or later.
2. In this folder, run `pip install -r requirements.txt`.
3. Run `streamlit run app.py`.
4. Upload a marketing spending CSV exported from Athena. Query:
   `SELECT date, channel, spend FROM calendly_marketing_db.silver_marketing_spend;`
5. Optionally upload a Calendly bookings CSV with `booking_id`, `booking_date`, `source`; optional `booking_timestamp`, `employee_id`, `campaign`.

**Important:** The existing Gold view is aggregated by channel and cannot support daily spending trends. Export the Silver rows for the dashboard. CPB requires bookings and spend covering comparable dates and correctly mapped marketing channels. This starter dashboard does not implement the required Delta Lake storage, scheduling, webhook ingestion, encryption, retries, CI/CD, or production deployment.
