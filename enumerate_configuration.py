import dataclasses,os,time

@dataclasses.dataclass
class Configuration:
    interval: float
    lifecycle: float
    datetime_critical: float
    limitN: int
    count_threshold: int
    api_key: str
    headers: dict

preferred_headers = {
    "Preferred-Language": "count=exact",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
    "Referer": "https://shit-journal-portal.vercel.app/",
    "Origin": "https://shit-journal-portal.vercel.app"
}

_DEFAULT_CONFIGURATION = Configuration(
    60*5, # Change by carful!!!!!
    1200,
    time.time() - time.time() % (60*60*24*7) + 144000,
    99999,
    6,
    os.getenv("SHIT_API_KEY"),
    preferred_headers
)