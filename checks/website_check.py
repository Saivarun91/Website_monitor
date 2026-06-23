import time

def run_website_check(page, url):

    report = {
        "status_code": None,
        "response_time": None,
        "console_errors": [],
        "issues": []
    }

    page.on(
        "console",
        lambda msg: report["console_errors"].append(
            f"{msg.type}: {msg.text}"
        )
    )

    start = time.time()

    response = page.goto(
        url,
        wait_until="networkidle",
        timeout=30000
    )

    report["response_time"] = round(
        time.time() - start,
        2
    )
    report["title"] = page.title()

    if response:
        report["status_code"] = response.status

    if report["status_code"] != 200:
        report["issues"].append(
            f"Unexpected status code: {report['status_code']}"
        )

    return report