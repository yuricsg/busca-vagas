import os
import json
import smtplib
import requests
import feedparser
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


KEYWORDS = [
    "desenvolvedor full stack jr",
    "desenvolvedor full stack junior",
    "full stack junior",
    "full stack jr",
    "desenvolvedor backend jr",
    "desenvolvedor backend junior",
    "backend junior",
    "backend jr",
    "node.js junior",
    "react junior",
    "nextjs junior",
    "desenvolvedor jr",
    "engenheiro de software jr",
    "analista de software jr",
    "jr",
    "developer",
    "engineer",
    "software",
    "backend",
    "full stack",
    "node",
    "react",
]

BLACKLIST = ["sênior", "senior", "pleno", "lead", "gerente", "manager", "staff"]

SEEN_JOBS_FILE = Path("seen_jobs.json")

EMAIL_SENDER    = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD  = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT")


def load_seen_jobs() -> set:
    if SEEN_JOBS_FILE.exists():
        return set(json.loads(SEEN_JOBS_FILE.read_text()))
    return set()

def save_seen_jobs(seen: set):
    SEEN_JOBS_FILE.write_text(json.dumps(list(seen), ensure_ascii=False, indent=2))

def is_relevant(title: str) -> bool:
    title_lower = title.lower()

    # precisa ter junior/jr
    is_junior = "junior" in title_lower or "jr" in title_lower

    # precisa ter área tech
    is_tech = any(kw in title_lower for kw in [
        "developer", "engineer", "software", "backend", "frontend", "full stack"
    ])

    has_blacklist = any(bl in title_lower for bl in BLACKLIST)

    return is_junior and is_tech and not has_blacklist


def fetch_gupy() -> list[dict]:
    jobs = []
    search_terms = ["full stack junior", "backend junior", "desenvolvedor junior"]
    
    for term in search_terms:
        try:
            url = "https://portal.api.gupy.io/api/v1/jobs"
            params = {"jobName": term, "limit": 20}
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json()
            for job in data.get("data", []):
                title = job.get("name", "")
                if not is_relevant(title):
                    continue
                jobs.append({
                    "id":       f"gupy_{job.get('id')}",
                    "title":    title,
                    "company":  job.get("company", {}).get("name", "N/A"),
                    "location": job.get("city") or "Remoto",
                    "url":      job.get("jobUrl", ""),
                    "source":   "Gupy",
                    "date":     job.get("publishedDate", "")[:10] if job.get("publishedDate") else "",
                })
        except Exception as e:
            print(f"[Gupy] Erro: {e}")
    
    return jobs


def fetch_linkedin_rss() -> list[dict]:
    jobs = []
    searches = [
        "full+stack+junior",
        "backend+junior+node",
        "desenvolvedor+junior+typescript",
    ]
    
    for term in searches:
        try:
            url = (
                f"https://www.linkedin.com/jobs/search/?keywords={term}"
                f"&location=Brazil&f_TPR=r86400&f_E=1,2"
            )
            rss_url = f"https://www.linkedin.com/jobs/search.rss?keywords={term}&location=Brazil&f_E=1,2"
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:15]:
                title = entry.get("title", "")
                if not is_relevant(title):
                    continue
                job_id = entry.get("id", entry.get("link", ""))
                jobs.append({
                    "id":       f"linkedin_{job_id}",
                    "title":    title,
                    "company":  entry.get("author", "N/A"),
                    "location": "Ver vaga",
                    "url":      entry.get("link", ""),
                    "source":   "LinkedIn",
                    "date":     entry.get("published", "")[:10] if entry.get("published") else "",
                })
        except Exception as e:
            print(f"[LinkedIn RSS] Erro: {e}")
    
    return jobs


def fetch_all_jobs() -> list[dict]:
    print("Buscando vagas...")
    all_jobs = []
    all_jobs.extend(fetch_gupy())
    all_jobs.extend(fetch_linkedin_rss())
    
    seen_ids = set()
    unique = []
    for job in all_jobs:
        if job["id"] not in seen_ids:
            seen_ids.add(job["id"])
            unique.append(job)
    
    print(f"   {len(unique)} vagas relevantes encontradas.")
    return unique

# EMAIL

def build_email_html(new_jobs: list[dict]) -> str:
    rows = ""
    for job in new_jobs:
        rows += f"""
        <tr>
          <td style="padding:12px 8px;border-bottom:1px solid #f0f0f0;">
            <strong><a href="{job['url']}" style="color:#4f46e5;text-decoration:none;">{job['title']}</a></strong><br>
            <span style="color:#6b7280;font-size:13px;">{job['company']} · {job['location']}</span>
          </td>
          <td style="padding:12px 8px;border-bottom:1px solid #f0f0f0;text-align:center;">
            <span style="background:#f3f4f6;padding:3px 10px;border-radius:99px;font-size:12px;">{job['source']}</span>
          </td>
          <td style="padding:12px 8px;border-bottom:1px solid #f0f0f0;text-align:center;color:#6b7280;font-size:13px;">
            {job['date']}
          </td>
        </tr>
        """

    return f"""
    <html><body style="font-family:sans-serif;background:#f9fafb;padding:24px;">
      <div style="max-width:700px;margin:auto;background:white;border-radius:12px;padding:32px;box-shadow:0 1px 4px rgba(0,0,0,0.08);">
        <h2 style="color:#111827;margin-top:0;"> {len(new_jobs)} vagas novas para você</h2>
        <p style="color:#6b7280;">Encontradas em {datetime.now().strftime('%d/%m/%Y às %H:%M')} — filtrando por: Full Stack Jr, Backend Jr</p>
        <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;margin-top:16px;">
          <thead>
            <tr style="background:#f3f4f6;">
              <th style="padding:10px 8px;text-align:left;font-size:13px;color:#6b7280;">Vaga</th>
              <th style="padding:10px 8px;text-align:center;font-size:13px;color:#6b7280;">Plataforma</th>
              <th style="padding:10px 8px;text-align:center;font-size:13px;color:#6b7280;">Data</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
        <p style="color:#9ca3af;font-size:12px;margin-top:24px;">Monitoramento automático · Yuri Job Monitor</p>
      </div>
    </body></html>
    """

def send_email(new_jobs: list[dict]):
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
        print("Variáveis de email não configuradas.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f" {len(new_jobs)} vagas novas — {datetime.now().strftime('%d/%m/%Y')}"
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECIPIENT
    msg.attach(MIMEText(build_email_html(new_jobs), "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print(f" Email enviado com {len(new_jobs)} vagas!")
    except Exception as e:
        print(f" Erro ao enviar email: {e}")


def main():
    test_jobs = [{
        "id": "1",
        "title": "Vaga Teste Full Stack Jr",
        "company": "Empresa Teste",
        "location": "Remoto",
        "url": "https://google.com",
        "source": "Teste",
        "date": "2026-04-06"
    }]

    send_email(test_jobs)

if __name__ == "__main__":
    main()
