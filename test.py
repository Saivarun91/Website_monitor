# import psycopg2

# conn = psycopg2.connect(
#     host="localhost",
#     port="5432",
#     dbname="website_monitor",
#     user="postgres",
#     password="Saivarun1234"
# )

# print("Connected Successfully!")

# conn.close()
# from alerts.email_alerts import send_email_alert

# send_email_alert(
#     "Test Alert",
#     "Website Monitor is working."
# )
# test_sites.py

# from db import get_active_websites
# from db import get_site_contacts

# sites = get_active_websites()

# for site in sites:

#     print(site)

#     contacts = get_site_contacts(site[0])

#     print(contacts)
#     print("-" * 50)
# from alerts.email_alerts import send_email_alert

# send_email_alert(
#     subject="Test Multi Email",
#     body="Testing multiple recipients",
#     recipients=[
#         "saivarun7032@gmail.com",
#         "srinivasbalam520@gmail.com"
#     ]
# )
from checks.ssl_check import get_ssl_expiry_days

print(
    get_ssl_expiry_days(
        "https://findmyguru.com"
    )
)