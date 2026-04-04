import dataclasses,os,time

@dataclasses.dataclass
class Configuration:
    interval: float
    lifecycle: float
    datetime_critical: float
    limitN: int
    count_threshold: int
    api_key: str # deprecated
    shit_articles_api_endpoint: str
    headers: dict

preferred_headers = {
    "Preferred-Language": "count=exact",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
    "Referer": "https://shit-journal-portal.vercel.app/",
    "Origin": "https://shit-journal-portal.vercel.app"
}

_DEFAULT_CONFIGURATION = Configuration(
    60*5, # Change by carful!!!!!
    1200+30,
    time.time() - time.time() % (60*60*24*7) + 144000,
    50, # maximum 50
    6,
    os.getenv("SHIT_API_KEY"), # deprecated
    "https://api.shitjournal.org/api/articles/",
    preferred_headers
)