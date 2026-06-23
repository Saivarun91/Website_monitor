import os
import json
import psycopg2

from dotenv import load_dotenv

load_dotenv()


def get_connection():

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def save_report(report, site_url, screenshot_path=None):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """ 
        INSERT INTO website_checks
        (
            site_url,
            page_title,
            status_code,
            response_time,
            issues,
            console_errors,
            screenshot_path
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            site_url,
            report["title"],
            report["status_code"],
            report["response_time"],
            json.dumps(report["issues"]),
            json.dumps(report["console_errors"]),
            screenshot_path
        )
    )

    conn.commit()

    cur.close()
    conn.close()

def get_active_websites():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            site_name,
            site_url
        FROM websites
        WHERE is_active = TRUE
        ORDER BY id
    """)

    websites = cur.fetchall()

    cur.close()
    conn.close()

    return websites


def get_site_contacts(website_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT email
        FROM website_contacts
        WHERE website_id = %s
        """,
        (website_id,)
    )

    contacts = [
        row[0]
        for row in cur.fetchall()
    ]

    cur.close()
    conn.close()

    return contacts

def get_website_status(website_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT last_status
        FROM website_status
        WHERE website_id = %s
        """,
        (website_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return row[0]

    return None

def update_website_status(
    website_id,
    status
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO website_status
        (
            website_id,
            last_status
        )
        VALUES
        (%s,%s)

        ON CONFLICT (website_id)
        DO UPDATE SET
            last_status = EXCLUDED.last_status,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            website_id,
            status
        )
    )

    conn.commit()

    cur.close()
    conn.close()

def get_website_rule(
    website_id
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            max_response_time,
            check_ssl,
            check_console_errors
        FROM website_rules
        WHERE website_id = %s
        """,
        (website_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row