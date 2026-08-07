import re
import json
from typing import Dict
from bs4 import BeautifulSoup
from app.scraper.auth import create_driver, manual_login_if_needed
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def clean(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

def extract_job_from_full_text(full_text: str) -> Dict:
    """
    Extract structured job data from the raw soup.text of a Jobinja page.
    """
    text = full_text

    job = {
        "title": None,
        "company": None,
        "location": None,
        "employment_type": None,
        "min_experience": None,
        "salary": None,
        "category": None,
        "must_have": [],
        "nice_to_have": [],
        "responsibilities": [],
        "description_short": None,
    }

    m = re.search(r'استخدام\s+(.+?)\s+در\s+', text)
    if m:
        job["title"] = clean(m.group(1))

    m = re.search(r'در\s+(.+?)\s+\|\s*جابینجا', text)
    if m:
        job["company"] = clean(m.group(1))

    m = re.search(r'موقعیت مکانی\s*\n?\s*(.+?)(?:\n|نوع همکاری)', text, re.DOTALL)
    if m:
        job["location"] = clean(m.group(1).replace('\n', ' '))

    m = re.search(r'نوع همکاری\s*\n?\s*(.+?)(?:\n|حداقل سابقه)', text, re.DOTALL)
    if m:
        job["employment_type"] = clean(m.group(1))

    m = re.search(r'حداقل سابقه کار\s*\n?\s*(.+?)(?:\n|حقوق)', text, re.DOTALL)
    if m:
        job["min_experience"] = clean(m.group(1))

    m = re.search(r'حقوق\s*\n?\s*(.+?)(?:\n|شرح موقعیت)', text, re.DOTALL)
    if m:
        job["salary"] = clean(m.group(1))

    m = re.search(r'دسته\u200cبندی شغلی\s*\n?\s*(.+?)(?:\n|موقعیت مکانی)', text, re.DOTALL)
    if m:
        job["category"] = clean(m.group(1))

    desc_match = re.search(
        r'شرح موقعیت شغلی\s*(.+?)ثبت آگهی استخدام در جابینجا',
        text,
        re.DOTALL
    )
    if not desc_match:
        # fallback
        desc_match = re.search(r'شرح موقعیت شغلی\s*(.+?)معرفی شرکت', text, re.DOTALL)

    if desc_match:
        desc = desc_match.group(1)

        job["description_short"] = clean(desc)[:350] + "..."
        must_patterns = [
            r'شرایط احراز\s*\n(.+?)(?=مزایا|امتیاز محسوب|ویژگی‌های شخصی|شرایط همکاری|مهارت‌های مورد نیاز|$)',
            r'مهارت[^\n]*مورد[^\n]*\n(.+?)(?=امتیاز محسوب|ویژگی‌های شخصی|شرایط همکاری|مزایا|$)',
            r'نیازمندی[^\n]*\n(.+?)(?=امتیاز محسوب|ویژگی‌های شخصی|مزایا|$)',
        ]
        raw_must = []
        for pattern in must_patterns:
            must_match = re.search(pattern, desc, re.DOTALL)
            if must_match:
                must_block = must_match.group(1)
                items = re.split(r'[\n•▪➤●\-–]', must_block)
                for item in items:
                    cleaned = clean(item)
                    if len(cleaned) > 3 and cleaned not in raw_must:
                        raw_must.append(cleaned)

        job["must_have"] = raw_must
        # resp_match = re.search(
        #     r'مسئولیت[^\n]*\n(.+?)(?:شرایط احراز|مهارت|[^\n]*مورد|امتیاز محسوب|ویژگی‌های شخصی|$)',
        #     desc,
        #     re.DOTALL
        # )
        resp_match = re.search(
            r'(?:مسئولیت[^\n]*|شرح شغل)\s*\n(.+?)(?=شرایط احراز|مهارت[^\n]*مورد|امتیاز محسوب|مزایا|ویژگی‌های شخصی|$)',
            desc,
            re.DOTALL
        )
        if resp_match:
            resp_block = resp_match.group(1)
            items = re.split(r'[\n•▪➤●\-–]', resp_block)
            job["responsibilities"] = [
                clean(item) for item in items
                if len(clean(item)) > 8
            ]



        if resp_match:
            resp_block = resp_match.group(1)

            items = re.split(r'[\n•▪➤●]', resp_block)
            job["responsibilities"] = [
                clean(item) for item in items
                if len(clean(item)) > 10 and not clean(item).startswith("مهارت")
            ]

        must_match = re.search(
            r'مهارت[^\n]*مورد[^\n]*\n(.+?)(?:|شرایط احراز|ویژگی‌های شخصی|شرایط احراز$)',
            desc,
            re.DOTALL
        )
        if must_match:
            must_block = must_match.group(1)
            items = re.split(r'[\n•▪➤●]', must_block)
            raw_must = [clean(item) for item in items if len(clean(item)) > 3]
            job["must_have"] = raw_must

        nice_match = re.search(
            r'امتیاز محسوب می[^\n]*\n(.+?)(?:ویژگی‌های شخصی|شرایط همکاری|$)',
            desc,
            re.DOTALL
        )
        if nice_match:
            nice_block = nice_match.group(1)
            items = re.split(r'[\n•▪➤●]', nice_block)
            raw_nice = [clean(item) for item in items if len(clean(item)) > 3]
            job["nice_to_have"] = raw_nice

    sidebar_skills = re.findall(r'مهارت‌های مورد نیاز\s*\n(.+?)(?:جنسیت|وضعیت نظام)', text, re.DOTALL)
    if sidebar_skills:
        extra = re.split(r'[\n\s]+', sidebar_skills[0])
        for s in extra:
            s = clean(s)
            if s and s not in job["must_have"] and len(s) > 2:
                job["must_have"].append(s)

    return job



def scrape_jobinja(url: str) -> str:
    driver = None
    text = ""
    try:
        driver = create_driver()
        manual_login_if_needed(driver)
        driver.get(url)

        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.o-listView__itemInfo, h1"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        text = soup.get_text(separator='\n')
    except Exception as e:
        print(e)
    finally:
        if driver:
            driver.quit()

    return text

def scrape_multiple_jobs(jobs: list) -> dict[int, dict]:
    """
    Open browser once, visit all job links, return {job_id: extracted_data}
    """
    driver = None
    results = {}

    try:
        driver = create_driver()
        manual_login_if_needed(driver)

        for job in jobs:
            try:
                print(f"Scraping: {job.title}")
                driver.get(job.link)

                WebDriverWait(driver, 12).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.o-listView__itemInfo, h1")
                    )
                )

                soup = BeautifulSoup(driver.page_source, "html.parser")
                full_text = soup.get_text(separator="\n")

                extracted = extract_job_from_full_text(full_text)

                # Keep only the important parts for the LLM
                results[job.id] = {
                    "must_have": extracted.get("must_have", []),
                    "nice_to_have": extracted.get("nice_to_have", []),
                    "responsibilities": extracted.get("responsibilities", []),
                    "title": extracted.get("title") or job.title,
                    "company": extracted.get("company") or job.company,
                }

            except Exception as e:
                print(f"Failed to scrape job {job.id} ({job.title}): {e}")
                results[job.id] = None   # or skip

    finally:
        if driver:
            driver.quit()

    return results

def job_data(url: str) -> dict[str, list[str]]:
    full_text = scrape_jobinja(url)
    job = extract_job_from_full_text(full_text)
    print(job)
    job_important_part = {"must_have": [job["must_have"]], "nice_to_have": [job["nice_to_have"]],
                          "responsibilities": [job["responsibilities"]]}
    return job_important_part

if __name__ == "__main__":
    site = "https://jobinja.ir/companies/amnafzar/jobs/t4EV/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-python-developer-%D9%85%D8%B4%D9%87%D8%AF-%D8%AF%D8%B1-%D8%A7%D9%85%D9%86-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1-%DA%AF%D8%B3%D8%AA%D8%B1-%D8%B4%D8%B1%DB%8C%D9%81?_ref=25"
    job = job_data(site)
    print(job)