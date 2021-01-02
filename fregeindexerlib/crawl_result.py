from dataclasses import dataclass

from typing import Dict, Optional

from fregeindexerlib.language import Language


@dataclass
class CrawlResult:
    id: str
    repo_url: str
    git_url: str
    languages: Optional[Dict[Language, bool]]
