from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup


@dataclass(slots=True)
class PhoneSummary:
    name: str
    url: str


@dataclass(slots=True)
class PhoneDetails:
    name: str
    url: str
    specs: dict[str, str]


def parse_brand_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a_tag in soup.select(".st-text a"):
        href = a_tag.get("href")
        if not href:
            continue
        links.append(urljoin(base_url + "/", href))
    return links


def parse_phone_summaries(html: str, base_url: str) -> list[PhoneSummary]:
    soup = BeautifulSoup(html, "lxml")
    output: list[PhoneSummary] = []
    for a_tag in soup.select(".makers li a"):
        href = a_tag.get("href")
        if not href:
            continue
        title = a_tag.find("span")
        name = title.get_text(strip=True) if title else a_tag.get_text(strip=True)
        output.append(PhoneSummary(name=name, url=urljoin(base_url + "/", href)))
    return output


def parse_phone_details(html: str, phone_name: str, phone_url: str) -> PhoneDetails:
    soup = BeautifulSoup(html, "lxml")
    specs: dict[str, str] = {}
    for row in soup.select("#specs-list table tr"):
        key_cell = row.select_one(".ttl")
        val_cell = row.select_one(".nfo")
        if not key_cell or not val_cell:
            continue
        key = key_cell.get_text(" ", strip=True)
        value = val_cell.get_text(" ", strip=True)
        if key:
            specs[key] = value

    if not specs:
        for row in soup.select("table tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                specs[th.get_text(" ", strip=True)] = td.get_text(" ", strip=True)

    return PhoneDetails(name=phone_name, url=phone_url, specs=specs)
