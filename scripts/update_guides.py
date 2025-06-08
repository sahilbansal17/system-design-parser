import sys
import requests
import os
from bs4 import BeautifulSoup
import urllib.parse

README_PATH = os.path.join(os.path.dirname(__file__), '..', 'README.md')
DAYS_DIR = os.path.join(os.path.dirname(__file__), '..', 'days')


def parse_topics():
    topics = {}
    with open(README_PATH, 'r') as f:
        for line in f:
            if line.startswith('|') and line.count('|') >= 3:
                parts = [p.strip() for p in line.split('|')[1:4]]
                try:
                    day = int(parts[0])
                except ValueError:
                    continue
                topic = parts[1]
                topics[day] = topic
    return topics


def search_web(query, num_results=3):
    url = 'https://duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []
    for a in soup.select('a.result__a')[:num_results]:
        title = a.get_text(strip=True)
        href = a['href']
        results.append((title, href))
    return results


def build_content(day, topic, links):
    content = [f"# Day {day}: {topic}", ""]
    if links:
        b_title, b_href = links[0]
        content.extend([
            "## Beginner",
            f"- Read [{b_title}]({b_href}) for an introduction to {topic}.",
            "",
        ])
    else:
        content.extend(["## Beginner", f"- Search online for introductory articles about {topic}", ""])

    if len(links) > 1:
        i_title, i_href = links[1]
        content.extend([
            "## Intermediate",
            f"- Deep dive with [{i_title}]({i_href}) and take notes.",
            "",
        ])
    else:
        content.extend(["## Intermediate", f"- Explore deeper resources on {topic}", ""])

    if len(links) > 2:
        a_title, a_href = links[2]
        content.extend([
            "## Advanced",
            f"- Apply concepts from [{a_title}]({a_href}) in a small prototype.",
            "",
        ])
    else:
        content.extend(["## Advanced", f"- Implement a small prototype demonstrating {topic}", ""])

    content.append("## Resources")
    for title, href in links:
        content.append(f"- [{title}]({href})")
    content.extend(["", "## Project Ideas", f"- Build a demo or write notes applying {topic}", ""])
    return '\n'.join(content)


def update_days(start, end):
    topics = parse_topics()
    for day in range(start, end + 1):
        topic = topics.get(day)
        if not topic:
            continue
        links = search_web(f"{topic} system design")
        content = build_content(day, topic, links)
        path = os.path.join(DAYS_DIR, f"day_{day:03}.md")
        with open(path, 'w') as f:
            f.write(content)
        print(f"Updated {path}")


if __name__ == '__main__':
    start = int(sys.argv[1])
    end = int(sys.argv[2]) if len(sys.argv) > 2 else start
    update_days(start, end)
