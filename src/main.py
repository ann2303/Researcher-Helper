import asyncio
import argparse
from pathlib import Path
import json
from aiohttp import ClientSession
from search import SemanticSearch

async def main():
    parser = argparse.ArgumentParser(description='Download open access PDFs from Semantic Scholar.')
    parser.add_argument('--query', type=str, help='Query to search for papers.')
    parser.add_argument('--save_directory', type=Path, help='Directory to save PDFs to.')
    parser.add_argument('--limit', type=int, default=10, help='Number of papers to download.')
    parser.add_argument('--headers-path', type=Path, help='Path to a file containing the headers to use for the Semantic Scholar API.', default=Path(__file__).parent / 'headers.json')
    args = parser.parse_args()
    
    with open(args.headers_path, 'r') as f:
        headers = json.load(f)
        
    async with ClientSession() as session:
        searcher = SemanticSearch(session, headers, limit=args.limit)
        async for paper_id, result in searcher.search_and_download_papers(args.query, args.save_directory):
            if isinstance(result, Exception):
                print(f"Failed to download '{paper_id}': {type(result).__name__}: {result}")
            elif result is None:
                print(f"'{paper_id}' is not open access")
            else:
                print(f"Downloaded '{paper_id}' to '{result}'")
        
    
if __name__ == '__main__':
    asyncio.run(main())
    
