import requests
from typing import AsyncGenerator, Generator, Iterable, TypeVar, Union
import asyncio
from pathlib import Path

class Paper:
    
    def __init__(self, paper_id: str, abstract: str, title: str, pdf_path: Path = None):
        self.pdf_path = pdf_path
        self.paper_id = paper_id
        self.abstract = abstract
        self.title = title

class SemanticSearch:
    
    def __init__(self, session, x_api_key, limit=10):
        self.headers = {"X-API-KEY": x_api_key}
        self.limit = limit
        self.params = {"fields": "paperId,title,isOpenAccess,openAccessPdf,abstract"}
        self.session = session
        
    async def get_papers(self, query: str) -> AsyncGenerator[dict, None]:
        data = {
            'query': query,
            'limit': self.limit
        }

        async with self.session.get(f'https://api.semanticscholar.org/graph/v1/paper/search', params=self.params | data, headers=self.headers) as response:
            response.raise_for_status()

            result = await response.json()
            for paper in result['data']:
                yield paper
                
                
    async def download_pdf(self, url: str, save_path: str, user_agent: str = 'aiohttp/3.0.0'):
        # send a user-agent to avoid server error
        headers = {
            'user-agent': user_agent,
        }

        # stream the response to avoid downloading the entire file into memory
        async with self.session.get(url, headers=headers, verify_ssl=False) as response:
            # check if the request was successful
            response.raise_for_status()

            if response.headers['content-type'] != 'application/pdf':
                raise Exception('The response is not a pdf')

            with open(save_path, 'wb') as f:
                # write the response to the file, chunk_size bytes at a time
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)



    async def search_and_download_papers(self, query: str, save_directory: Path):
        if not save_directory.exists():
            save_directory.mkdir(parents=True)
            
        async for paper in self.get_papers(query):
            print(paper)

            # check if the paper is open access
            if not paper['isOpenAccess']:
                paper_obj = Paper(paper['paperId'], paper["abstract"], paper["title"])
                yield paper_obj

            try:
                pdf_url: str = paper['openAccessPdf']['url']
                pdf_path = save_directory / f'{paper["paperId"]}.pdf'
                paper_obj = Paper(paper['paperId'], paper["abstract"], paper["title"], pdf_path)
                await self.download_pdf(pdf_url, pdf_path)
                yield paper_obj
            except Exception as e:
                paper_obj = Paper(paper['paperId'], paper["abstract"], paper["title"])
                yield paper_obj
