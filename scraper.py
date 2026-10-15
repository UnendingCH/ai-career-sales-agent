"""
ISRAEL BABALOLA - COMPLETE 24/7 MULTI-PILLAR LEAD & REMOTE JOB HUNTER
Hunts 20+ high-ticket leads/day across English-speaking Africa & Global markets for:
1. School Websites, Teacher Result Portals & Admin Consoles (SCHOOL-SYS-01)
2. Social Media Graphic Designer, Ad Creatives & Brand Identity Requests (GRAPHIC-SOC-03)
3. UI/UX Redesigns & AI Web App Development (UIUX-WEB-02)
Plus strict skill-matched Remote Jobs for Job_Pipeline.
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

WEBHOOK_URL = os.environ.get("APPS_SCRIPT_WEBHOOK_URL", "").strip()

# Strict Role Title & Skill Matching for Israel's 3 Pillars
STRICT_TITLE_KEYWORDS = [
    "graphic designer", "social media designer", "brand designer", "visual designer",
    "creative designer", "ui", "ux", "product designer", "web designer",
    "web developer", "frontend", "front-end", "full stack", "fullstack",
    "lovable", "webflow", "portal"
]

# 1. School Portal Lead Queries (English-Speaking Africa + Global High-Ticket)
SCHOOL_LEAD_QUERIES = [
    "International Academy Private School Lagos Abuja Johannesburg Nairobi admissions contact",
    "British International School College Accra Dubai London Toronto admissions email",
    "Montessori Academy High School admissions open contact info@",
    "newly established private school academy admissions principal contact"
]

# 2. Social Media Graphic Design & Brand Identity Lead Queries (Socials, Boards & AI/LLM Search Requests)
GRAPHIC_DESIGN_LEAD_QUERIES = [
    '"looking for a graphic designer" OR "need a social media designer" agency founder',
    '"hiring graphic designer" social media visuals brand identity remote',
    '"need someone to design" social media posts flyers brand kit startup',
    'marketing agency "graphic designer" overflow retainer remote US UK Canada Africa'
]

# 3. UI/UX & AI Web Developer Lead Queries
UIUX_WEB_LEAD_QUERIES = [
    '"looking for a UI/UX designer" OR "need a web developer" startup founder',
    '"redesign our website" OR "custom web portal" business owner contact'
]


def fetch_url(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "Accept": "application/json, application/xml, text/xml, text/html, */*"
        }
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read().decode("utf-8", errors="ignore")


def clean_html(raw_html):
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(raw_html))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:3500]


def extract_email_from_text(text):
    if not text:
        return ""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", str(text))
    if match:
        email = match.group(0).lower()
        if not any(bad in email for bad in ["example.com", "sentry.io", ".png", ".jpg", ".svg"]):
            return email
    return ""


def is_strict_skill_match(title):
    t = str(title).lower()
    return any(kw in t for kw in STRICT_TITLE_KEYWORDS)


def scrape_tailored_remote_jobs():
    """Gathers remote jobs strictly matching Social Media Graphic Design, UI/UX, or AI Web Dev."""
    jobs = []
    seen_urls = set()

    # 1. Remotive Design, Marketing Creative & Software
    for cat in ["design", "software-dev", "marketing"]:
        try:
            raw = fetch_url(f"https://remotive.com/api/remote-jobs?category={cat}&limit=25")
            for item in json.loads(raw).get("jobs", []):
                title = item.get("title", "")
                url = item.get("url", "")
                if is_strict_skill_match(title) and url not in seen_urls:
                    seen_urls.add(url)
                    jobs.append({
                        "company": item.get("company_name", "Remote Company"),
                        "role_title": title,
                        "platform_source": "Remotive (" + item.get("candidate_required_location", "Global") + ")",
                        "job_url": url,
                        "job_description": clean_html(item.get("description", ""))
                    })
        except Exception as e:
            print(f"Remotive notice ({cat}): {e}")

    # 2. Jobicy Unsaturated Design & Creative Feed
    try:
        raw = fetch_url("https://jobicy.com/api/v2/remote-jobs?count=25&tag=design")
        for item in json.loads(raw).get("jobs", []):
            title = item.get("jobTitle", "")
            url = item.get("url", "")
            if is_strict_skill_match(title) and url not in seen_urls:
                seen_urls.add(url)
                jobs.append({
                    "company": item.get("companyName", "Remote Brand"),
                    "role_title": title,
                    "platform_source": "Jobicy (" + str(item.get("jobGeo", "Anywhere")) + ")",
                    "job_url": url,
                    "job_description": clean_html(item.get("jobDescription", ""))
                })
    except Exception as e:
        print(f"Jobicy notice: {e}")

    # 3. WeWorkRemotely Design RSS
    try:
        xml_text = fetch_url("https://weworkremotely.com/categories/remote-design-jobs.rss")
        root = ET.fromstring(xml_text)
        for item in root.findall(".//item")[:10]:
            raw_title = item.findtext("title", "")
            link = item.findtext("link", "").strip()
            desc = clean_html(item.findtext("description", ""))
            company, role_title = raw_title.split(":", 1) if ":" in raw_title else ("Remote Company", raw_title)
            if is_strict_skill_match(role_title) and link not in seen_urls:
                seen_urls.add(link)
                jobs.append({
                    "company": company.strip(),
                    "role_title": role_title.strip(),
                    "platform_source": "WeWorkRemotely",
                    "job_url": link,
                    "job_description": desc
                })
    except Exception as e:
        print(f"WWR notice: {e}")

    return jobs[:12]


def run_bing_rss_lead_search(queries, offer_id, default_role_label, signal_prefix, max_items):
    """Searches live web/news RSS indexes for high-ticket leads in Africa & globally."""
    collected = []
    seen = set()
    for q in queries:
        try:
            encoded = urllib.parse.quote(q)
            rss_url = f"https://www.bing.com/news/search?q={encoded}&format=rss"
            xml_text = fetch_url(rss_url)
            root = ET.fromstring(xml_text)
            for item in root.findall(".//item")[:6]:
                title = clean_html(item.findtext("title", ""))
                link = item.findtext("link", "")
                desc = clean_html(item.findtext("description", ""))
                if not title or title in seen:
                    continue
                seen.add(title)
                email = extract_email_from_text(desc)
                collected.append({
                    "offer_id": offer_id,
                    "prospect_name_role": default_role_label,
                    "company_url": f"{title[:70]} ({link})",
                    "contact_email": email,
                    "social_buying_signal": f"{signal_prefix}: {title} | Context: {desc[:420]}"
                })
                if len(collected) >= max_items:
                    return collected
        except Exception as e:
            print(f"Search notice ({offer_id}): {e}")
    return collected


def scrape_social_and_community_requests():
    """Scans Reddit & Global Founder/Design Communities for Graphic Design, UI/UX & Web requests."""
    leads = []
    seen = set()
    feeds = [
        (
            "GRAPHIC-SOC-03",
            "https://www.reddit.com/r/DesignJobs+forhire+GraphicDesign+smallbusiness+Entrepreneur/search.rss?q=hiring+graphic+designer+OR+social+media+design+OR+flyer+OR+brand+identity&restrict_sr=on&sort=new&t=week"
        ),
        (
            "UIUX-WEB-02",
            "https://www.reddit.com/r/forhire+DesignJobs+startups+SaaS+web_design/search.rss?q=hiring+ui+ux+OR+web+developer+OR+website+redesign+OR+portal&restrict_sr=on&sort=new&t=week"
        )
    ]
    for offer_id, url in feeds:
        try:
            xml_text = fetch_url(url)
            root = ET.fromstring(xml_text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns)[:8]:
                title = entry.findtext("atom:title", "", ns)
                if "[for hire]" in title.lower() or title in seen:
                    continue
                seen.add(title)
                link_el = entry.find("atom:link", ns)
                link = link_el.attrib.get("href", "") if link_el is not None else ""
                content = clean_html(entry.findtext("atom:content", "", ns))
                email = extract_email_from_text(content)

                leads.append({
                    "offer_id": offer_id,
                    "prospect_name_role": "Founder / Brand Owner (Social Request)",
                    "company_url": link,
                    "contact_email": email,
                    "social_buying_signal": f"Direct Social Request: {title} | Details: {content[:450]}"
                })
        except Exception as e:
            print(f"Community feed notice ({offer_id}): {e}")
        time.sleep(1.5)
    return leads


def compile_20_plus_daily_high_ticket_leads():
    """Compiles 20+ daily leads across School Portals, Social Media Graphic Design, and UI/UX Web Dev."""
    all_leads = []

    # 1. School Website, Teacher Result Portal & Admin Console Leads (Africa + Global)
    school_leads = run_bing_rss_lead_search(
        SCHOOL_LEAD_QUERIES,
        "SCHOOL-SYS-01",
        "School Proprietor / Principal",
        "School Portal Opportunity (Pitch ableinternationalacademy.com, /portal, /admin)",
        10
    )
    all_leads.extend(school_leads)

    # 2. Social Media Graphic Design & Brand Identity Leads (Web/AI Discovery + Social Requests)
    graphic_web_leads = run_bing_rss_lead_search(
        GRAPHIC_DESIGN_LEAD_QUERIES,
        "GRAPHIC-SOC-03",
        "Marketing Director / Brand Founder",
        "Social Media Graphic Design & Brand Asset Need (Pitch babalola-folio.lovable.app)",
        6
    )
    all_leads.extend(graphic_web_leads)

    # 3. UI/UX & AI Web App Leads
    uiux_leads = run_bing_rss_lead_search(
        UIUX_WEB_LEAD_QUERIES,
        "UIUX-WEB-02",
        "Startup Founder / Product Lead",
        "UI/UX & Web Portal Need (Pitch babalola-folio.lovable.app)",
        4
    )
    all_leads.extend(uiux_leads)

    # 4. Direct Social & Community Hiring Requests (Graphic Design + UI/UX + Web)
    social_requests = scrape_social_and_community_requests()
    all_leads.extend(social_requests)

    return all_leads[:25]


def send_to_google_sheet(jobs, social_leads):
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
    with urllib.request.urlopen(req, timeout=45) as resp:
        print("Google Sheet Webhook Response:", resp.read().decode("utf-8", errors="ignore"))


if __name__ == "__main__":
    print("1. Hunting strict skill-matched remote jobs (Social Graphic Design, UI/UX, AI Web Dev)...")
    tailored_jobs = scrape_tailored_remote_jobs()
    print(f"Gathered {len(tailored_jobs)} tailored remote jobs.")

    print("2. Compiling 20+ daily High-Ticket Leads (Schools, Graphic Design & UI/UX across Africa & Global)...")
    daily_leads = compile_20_plus_daily_high_ticket_leads()
    print(f"Compiled {len(daily_leads)} high-ticket leads.")

    print("3. Sending to Google Sheet Command Center...")
    send_to_google_sheet(tailored_jobs, daily_leads)
    print("Complete!")
