from playwright.sync_api import sync_playwright
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger
from dotenv import load_dotenv
from datetime import datetime

from alerts.email_alerts import send_email_alert
from checks.website_check import run_website_check
from ai.gemini_analyzer import analyze_report

from db import (
    save_report,
    get_active_websites,
    get_site_contacts,
    get_website_status,
    update_website_status,
    get_website_rule
)

import os


# =========================
# Environment
# =========================

load_dotenv()

# =========================
# Logger
# =========================

logger.add(
    "automation.log",
    rotation="10 MB"
)

# =========================
# Analysis Rules
# =========================

def needs_analysis(report, max_response_time, check_ssl, check_console_errors):

    if report["status_code"] is None:
        return True

    if report["status_code"] >= 300:
        return True

    if len(report["issues"]) > 0:
        return True

    if report["response_time"] > max_response_time :
        return True

    if check_console_errors and len(
        report["console_errors"]) > 0:
        return True

    return False


# =========================
# Main Monitor Task
# =========================

def run_task():

    logger.info("=" * 80)
    logger.info("Starting Website Monitor")

    sites = get_active_websites()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        for site in sites:

            site_id = site[0]
            site_name = site[1]
            site_url = site[2]

            rule = get_website_rule(
                site_id
            )

            max_response_time = rule[0]
            check_ssl = rule[1]
            check_console_errors = rule[2]
            ssl_days_left = None

            if check_ssl:

                try:

                    from checks.ssl_check import (
                        get_ssl_expiry_days
                    )

                    ssl_days_left = (
                        get_ssl_expiry_days(
                            site_url
                        )
                    )

                    logger.info(
                        f"{site_name}: SSL expires in "
                        f"{ssl_days_left} days"
                    )

                except Exception as e:

                    logger.exception(
                        f"{site_name}: SSL check failed"
                    )

            logger.info(
                f"Checking {site_name} ({site_url})"
            )

            contacts = get_site_contacts(
                site_id
            )

            page = browser.new_page()

            try:

                report = run_website_check(
                    page,
                    site_url
                )
                previous_status = get_website_status(
                    site_id
                )

                current_status = "UP"

                if needs_analysis(report, max_response_time, check_ssl, check_console_errors):
                    current_status = "DOWN"

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                screenshot_path = (
                    f"screenshots/"
                    f"{site_name.replace(' ', '_')}_{timestamp}.png"
                )

                page.screenshot(
                    path=screenshot_path,
                    full_page=True
                )

                logger.info(report)

                save_report(
                    report,
                    site_url,
                    screenshot_path
                )

                logger.info(
                    f"{site_name}: Report saved to PostgreSQL"
                )
                if (
                    check_ssl
                    and ssl_days_left is not None
                    and ssl_days_left < 20
                ):

                    send_email_alert(
                        subject=f"⚠ {site_name} SSL Expiry",

                        body=f"""
                Website:
                {site_name}

                URL:
                {site_url}

                SSL expires in:
                {ssl_days_left} days

                Please renew the certificate.
                        """,

                        recipients=contacts
                    )

                    logger.warning(
                        f"{site_name}: SSL expiring in "
                        f"{ssl_days_left} days"
                    )
                # Recovery Email
                if (
                    previous_status == "DOWN"
                    and current_status == "UP"
                ):

                    logger.info(
                        f"{site_name}: Website Recovered"
                    )

                    send_email_alert(
                        subject=f"✅ {site_name} Recovered",
                        body=f"""
                Website:
                {site_name}

                URL:
                {site_url}

                Status:
                RECOVERED

                Status Code:
                {report.get('status_code')}

                Response Time:
                {report.get('response_time')} seconds

                The website is healthy again.
                        """,
                        recipients=contacts
                    )

                # Issue Alert
                elif needs_analysis(report, max_response_time, check_ssl, check_console_errors):
                    
                    
                    
                    logger.warning(
                        f"{site_name}: Issue detected"
                    )

                    ai_summary = analyze_report(
                        report
                    )

                    logger.info(
                        f"{site_name}: AI Analysis Completed"
                    )

                    send_email_alert(
                        subject=f"🚨 {site_name} Website Alert",
                        body=f"""
                Website:
                {site_name}

                URL:
                {site_url}

                Title:
                {report.get('title')}

                Status Code:
                {report.get('status_code')}

                Response Time:
                {report.get('response_time')} seconds

                Issues:
                {report.get('issues')}

                Console Errors:
                {report.get('console_errors')}

                AI Analysis:

                {ai_summary}
                        """,
                        recipients=contacts
                    )

                    logger.info(
                        f"{site_name}: Alert email sent"
                    )

                else:

                    logger.info(
                        f"{site_name}: Healthy"
                    )

                # Update status in DB
                update_website_status(
                    site_id,
                    current_status
                )

            except Exception as e:

                logger.exception(
                    f"{site_name}: Monitor Failed"
                )

                try:

                    send_email_alert(
                        subject=f"🚨 {site_name} Monitor Failure",
                        body=f"""
Website:
{site_name}

URL:
{site_url}

Error:

{str(e)}
                        """,
                        recipients=contacts
                    )

                except Exception:
                    logger.exception(
                        "Failed to send alert email"
                    )

                update_website_status(
                    site_id,
                    "DOWN"
                )

            finally:

                page.close()

        browser.close()


# =========================
# Scheduler
# =========================

scheduler = BlockingScheduler()

scheduler.add_job(
    run_task,
    "interval",
    minutes=5
)

# Run immediately
run_task()

logger.info(
    "Scheduler Started"
)

scheduler.start()