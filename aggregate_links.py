import json
import os
import re

def extract_links(file_path):
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            links = []
            
            # Extract from DDG results
            for res in data.get('ddg_results', []):
                links.append({
                    "title": res.get('title', 'No Title'),
                    "url": res.get('url', ''),
                    "source": "DuckDuckGo"
                })
                
            # Extract from Reddit results
            for res in data.get('reddit_results', []):
                links.append({
                    "title": res.get('title', 'No Title'),
                    "url": res.get('url', ''),
                    "source": f"Reddit (/r/{res.get('subreddit', 'unknown')})"
                })
                
            # Extract from Arxiv results
            for res in data.get('arxiv_results', []):
                links.append({
                    "title": res.get('title', 'No Title'),
                    "url": res.get('url', ''),
                    "source": "Arxiv"
                })

            # Extract from GitHub results
            for res in data.get('github_results', []):
                links.append({
                    "title": res.get('title', 'No Title'),
                    "url": res.get('url', ''),
                    "source": "GitHub (Repo)"
                })
                
            return links
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

all_links = []
# Dynamic file discovery for drp_results_*.json
import glob
files = glob.glob('drp_results_*.json')

for file in files:
    all_links.extend(extract_links(file))

# Deduplicate by URL
unique_links = {}
for link in all_links:
    url = link['url']
    if url and url not in unique_links:
        unique_links[url] = link

# Prepare markdown content
md_lines = []
for url, link in unique_links.items():
    title = link['title'].replace('[', '(').replace(']', ')') # Simple escape
    md_lines.append(f"- [{title}]({url})")

queue_path = '../docs/research/to-research-queue.md'
if os.path.exists(queue_path):
    with open(queue_path, 'r') as f:
        content = f.read()
    
    # Preserve everything before the "Deep Research Expansion" header
    header = "## Deep Research Expansion"
    if header in content:
        static_part = content.split(header)[0]
        # Check if "Agent Aggregation" is also there to preserve it if it was added AFTER
        agent_header = "## Agent Aggregation"
        agent_part = ""
        if agent_header in content:
            agent_part = agent_header + content.split(agent_header)[1]
            # Ensure static part doesn't include agent part if it was already split
            if agent_header in static_part:
                static_part = static_part.split(agent_header)[0]
        
        new_content = static_part + header + "\n\n" + "\n".join(md_lines) + "\n\n" + agent_part
    else:
        # Fallback if header not found
        new_content = content + "\n\n" + header + "\n\n" + "\n".join(md_lines)
        
    with open(queue_path, 'w') as f:
        f.write(new_content)

print(f"Total Unique DRP Links: {len(unique_links)}")
