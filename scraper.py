"""
ISRAEL BABALOLA - PHASE 2: 24/7 REMOTE JOB & HIGH-TICKET SOCIAL LEAD SCRAPER
Runs 100% free on GitHub Actions every 6 hours and sends fresh data directly
to your Google Sheet Command Center via your Apps Script Web App URL.
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

WEBHOOK_URL = os.environ.get("APPS_SCRIPT_WEBHOOK_URL", "").strip()

# Keywords tailored to Israel's 3 Pillars: Graphic Design, UI/UX, AI Web Dev
TARGET_JOB_KEYWORDS = [
    "ui/ux", "ui designer", "ux designer", "product designer",
    "graphic designer", "brand designer", "visual designer",
    "web developer", "frontend", "front-end", "lovable", "webflow", "portal"
]

# High-Ticket Social Buying Signals (Reddit & Startup Communities RSS)
SOCIAL_SIGNAL_FEEDS = [
    {
        "offer_id": "UIUX-WEB-01",
        "url": "https://www.reddit.com/r/forhire+DesignJobs+startups+SaaS+Entrepreneur/search.rss?q=hiring+designer+OR+need+website+OR+ui+ux+OR+redesign&restrict_sr=on&sort=new&t=day"
    },
    {
        "offer_id": "UIUX-WEB-01",
        "url": "https://www.reddit.com/r/smallbusiness+web_design+WebDeveloperJobs/search.rss?q=looking+for+web+developer+OR+graphic+designer+OR+landing+page&restrict_sr=on&sort=new&t=day"
    }
]


def fetch_url(url):
    """Fetches a URL safely with a browser User-Agent."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "Accept": "application/json, application/xml, text/xml, */*"
        }
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read().decode("utf-8", errors="ignore")


def clean_html(raw_html):
    """Strips HTML tags and collapses whitespace."""
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(raw_html))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:3500]


def extract_email_from_text(text):
    """Extracts an email address if the prospect included one in their post."""
    if not text:
        return ""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def matches_skills(title, description):
    """Checks if a job matches Graphic Design, UI/UX, or Web Development."""
    combined = (str(title) + " " + str(description)).lower()
    return any(kw in combined for kw in TARGET_JOB_KEYWORDS)


def scrape_remotive_jobs():
    """1. Scrapes Remotive's curated remote Design & Software API."""
    jobs = []
    categories = ["design", "software-dev"]
    for cat in categories:
        try:
            url = f"https://remotive.com/api/remote-jobs?category={cat}&limit=15"
            raw = fetch_url(url)
            data = json.loads(raw)
            for item in data.get("jobs", []):
                title = item.get("title", "")
                desc = clean_html(item.get("description", ""))
                if matches_skills(title, desc):
                    jobs.append({
                        "company": item.get("company_name", "Remote Company"),
                        "role_title": title,
                        "platform_source": "Remotive (" + item.get("candidate_required_location", "Worldwide") + ")",
                        "job_url": item.get("url", ""),
                        "job_description": desc
                    })
        except Exception as e:
            print(f"Remotive warning ({cat}): {e}")
    return jobs[:6]


def scrape_jobicy_jobs():
    """2. Scrapes Jobicy's unsaturated remote Design & Web Dev feed."""
    jobs = []
    try:
        url = "https://jobicy.com/api/v2/remote-jobs?count=15&tag=design"
        raw = fetch_url(url)
        data = json.loads(raw)
        for item in data.get("jobs", []):
            title = item.get("jobTitle", "")
            desc = clean_html(item.get("jobDescription", "") or item.get("jobExcerpt", ""))
            if matches_skills(title, desc):
                jobs.append({
                    "company": item.get("companyName", "Remote Startup"),
                    "role_title": title,
                    "platform_source": "Jobicy (" + str(item.get("jobGeo", "Anywhere")) + ")",
                    "job_url": item.get("url", ""),
                    "job_description": desc
                })
    except Exception as e:
        print(f"Jobicy warning: {e}")
    return jobs[:5]


def scrape_weworkremotely_rss():
    """3. Scrapes WeWorkRemotely Design & Frontend RSS feeds."""
    jobs = []
    rss_urls = [
        "https://weworkremotely.com/categories/remote-design-jobs.rss",
        "https://weworkremotely.com/categories/remote-front-end-programming-jobs.rss"
    ]
    for rss_url in rss_urls:
        try:
            xml_text = fetch_url(rss_url)
            root = ET.fromstring(xml_text)
            for item in root.findall(".//item")[:8]:
                raw_title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = clean_html(item.findtext("description", ""))
                if ":" in raw_title:
                    company, role_title = raw_title.split(":", 1)
                else:
                    company, role_title = "Remote Company", raw_title

                if matches_skills(role_title, desc):
                    jobs.append({
                        "company": company.strip(),
                        "role_title": role_title.strip(),
                        "platform_source": "WeWorkRemotely",
                        "job_url": link.strip(),
                        "job_description": desc
                    })
        except Exception as e:
            print(f"WWR RSS warning: {e}")
    return jobs[:5]


def scrape_social_buying_signals():
    """4. Scans Reddit & Founder RSS Feeds for live high-ticket buying signals."""
    leads = []
    for feed in SOCIAL_SIGNAL_FEEDS:
        try:
            xml_text = fetch_url(feed["url"])
            root = ET.fromstring(xml_text)
            # Atom RSS namespace handling
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)
            for entry in entries[:6]:
                title = entry.findtext("atom:title", "", ns)
                # Skip "[For Hire]" posts; we only want "[Hiring]" or business owners with a problem
                if "[for hire]" in title.lower():
                    continue

                author_el = entry.find("atom:author/atom:name", ns)
                author = author_el.text if author_el is not None else "Founder / Poster"
                link_el = entry.find("atom:link", ns)
                link = link_el.attrib.get("href", "") if link_el is not None else ""
                content = clean_html(entry.findtext("atom:content", "", ns))

                extracted_email = extract_email_from_text(content)

                leads.append({
                    "offer_id": feed["offer_id"],
                    "prospect_name_role": f"{author} (Social Lead)",
                    "company_url": link,
                    "contact_email": extracted_email,
                    "social_buying_signal": f"Post Title: {title} | Details: {content[:800]}"
                })
        except Exception as e:
            print(f"Social feed warning: {e}")
        time.sleep(2)
    return leads[:8]


def send_to_google_sheet(jobs, social_leads):
    """Pushes all scraped jobs and social leads to your Google Sheet Webhook."""
    if not WEBHOOK_URL:
        raise ValueError("Missing APPS_SCRIPT_WEBHOOK_URL secret in GitHub!")

    payload = json.dumps({
        "jobs": jobs,
        "social_leads": social_leads
    }).encode("utf-8")

    req = urllib.request.Request(
        WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("Google Sheet Webhook Response:", resp.read().decode("utf-8", errors="ignore"))


if __name__ == "__main__":
    print("1. Hunting fresh remote jobs across Design, UI/UX, and AI Web Dev...")
    all_jobs = []
    all_jobs.extend(scrape_remotive_jobs())
    all_jobs.extend(scrape_jobicy_jobs())
    all_jobs.extend(scrape_weworkremotely_rss())
    print(f"Found {len(all_jobs)} matching remote jobs.")

    print("2. Scanning social buying signals for High-Ticket Sales...")
    social_leads = scrape_social_buying_signals()
    print(f"Found {len(social_leads)} high-intent social leads.")

    print("3. Sending payload to Google Sheet Command Center...")
    send_to_google_sheet(all_jobs, social_leads)
    print("Done!")
