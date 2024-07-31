import asyncio
import argparse
from pathlib import Path
import json
from aiohttp import ClientSession
from search import SemanticSearch
import pandas as pd
from articles_info_collector import ArticleInfo

class Config:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            data = json.load(f)
        self.x_api_key = data["X-API-KEY"] # semantic scholar api
        self.openai_api_key = data["OPENAI_API_KEY"] # gpt api key
        

async def run_semantic_search(args, config):
    articles_path = args.save_directory / "articles"
    articles_path.mkdir(exist_ok=True, parents=True)
        
    async with ClientSession() as session:
        searcher = SemanticSearch(session, config.x_api_key, limit=args.limit)
        result = await searcher.search_and_download_papers(args.query, articles_path)
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Download open access PDFs from Semantic Scholar.')
    parser.add_argument('--query', type=str, help='Query to search for papers.')
    parser.add_argument('--save_directory', type=Path, help='Directory to save PDFs to.')
    parser.add_argument('--limit', type=int, default=10, help='Number of papers to download.')
    parser.add_argument('--config', type=Path, help='Path to config with Semantic Scholar API and OpenAI API key.', default=Path(__file__).parent / 'config.json')
    args = parser.parse_args()
    
    
    config = Config(args.config)
    
    result = asyncio.run(run_semantic_search(args, config))
    
    result.to_html("result.html")
                
    
if __name__ == '__main__':
    main()
    
