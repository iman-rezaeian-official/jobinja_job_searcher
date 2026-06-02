import re

from bs4 import BeautifulSoup


def get_last_page(html):
    soup = BeautifulSoup(html, "lxml")

    paginator = soup.select_one("div.paginator")

    if not paginator:
        return 1

    pages = []

    for a in paginator.select("a[href]"):
        href = a.get("href", "")

        match = re.search(
            r"page=(\d+)",
            href
        )

        if match:
            pages.append(
                int(match.group(1))
            )

    return max(pages) if pages else 1
