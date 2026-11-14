# Calendly Marketing Insights Streamlit dashboard

## Run locally
1. Install Python 3.10 or later.
2. In this folder, run `pip install -r requirements.txt`.
3. Run `streamlit run app.py`.
4. Upload a marketing spending CSV exported from Athena. Query:
   `SELECT date, channel, spend FROM calendly_marketing_db.silver_marketing_spend;`
5. Optionally upload a Calendly bookings CSV with `booking_id`, `booking_date`, `source`; optional `booking_timestamp`, `employee_id`, `campaign`.

**Important:** The existing Gold view is aggregated by channel and cannot support daily spending trends. Export the Silver rows for the dashboard. CPB requires bookings and spend covering comparable dates and correctly mapped marketing channels. This starter dashboard does not implement the required Delta Lake storage, scheduling, webhook ingestion, encryption, retries, CI/CD, or production deployment.
