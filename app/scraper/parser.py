import logging
from bs4 import BeautifulSoup

from app.utils.helpers import clean_text

logger = logging.getLogger(__name__)


def parse_jobs(html):
    soup = BeautifulSoup(html, "lxml")

    cards = soup.select(
        "div.o-listView__itemInfo"
    )

    jobs = []

    for card in cards:
        try:
            title_tag = card.select_one(
                "h2 a"
            )

            title = clean_text(
                title_tag.get_text()
            )

            link = title_tag["href"]

            days_tag = card.select_one(
                "span.c-jobListView__passedDays"
            )

            posted = (
                clean_text(
                    days_tag.get_text()
                )
                if days_tag
                else ""
            )

            meta = card.select(
                "li.c-jobListView__metaItem span"
            )

            company = (
                clean_text(meta[0].get_text())
                if len(meta) > 0
                else ""
            )

            location = (
                clean_text(meta[1].get_text())
                if len(meta) > 1
                else ""
            )

            contract = (
                clean_text(meta[2].get_text())
                if len(meta) > 2
                else ""
            )

            img = card.select_one("img")

            logo = (
                img["src"]
                if img
                else ""
            )

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "job_info": contract,
                "posted": posted,
                "link": link,
                "logo": logo,
            })

        except Exception as e:
            logger.exception("Parse error:", e)

    return jobs
