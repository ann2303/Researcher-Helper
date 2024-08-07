from typing import AsyncGenerator, Generator, Iterable, TypeVar, Union
from pathlib import Path
from articles_info_collector import ArticleInfo
import pandas as pd
import arxiv


class Paper:

    def __init__(
        self,
        paperId,
        title,
        isOpenAccess,
        openAccessPdf,
        abstract,
        year,
        authors,
        doi,
        citationCount,
        url,
    ):
        self.paperId = paperId
        self.title = title
        self.isOpenAccess = isOpenAccess
        self.openAccessPdf = openAccessPdf
        self.abstract = abstract
        self.year = year
        self.authors = authors
        self.doi = doi
        self.citationCount = citationCount
        self.url = url


class SemanticSearch:

    def __init__(self, session, x_api_key, limit=10):
        self.headers = {"X-API-KEY": x_api_key}
        self.limit = limit
        self.params = {
            "fields": "paperId,title,isOpenAccess,openAccessPdf,abstract,year,authors,citationCount,url,journal"
        }
        self.session = session

    async def get_papers(self, query: str) -> AsyncGenerator[dict, None]:
        data = {"query": query, "limit": self.limit}
        
        session_params = self.params.copy()
        session_params.update(data)

        async with self.session.get(
            f"https://api.semanticscholar.org/graph/v1/paper/search",
            params=session_params,
            headers=self.headers,
        ) as response:
            response.raise_for_status()

            result = await response.json()
            for paper in result["data"]:
                yield paper

    async def download_pdf(
        self, url: str, save_path: str, user_agent: str = "aiohttp/3.0.0"
    ):
        # send a user-agent to avoid server error
        headers = {
            "user-agent": user_agent,
        }

        # stream the response to avoid downloading the entire file into memory
        async with self.session.get(url, headers=headers, verify_ssl=False) as response:
            # check if the request was successful
            response.raise_for_status()

            if response.headers["content-type"] != "application/pdf":
                raise Exception("The response is not a pdf")

            with open(save_path, "wb") as f:
                # write the response to the file, chunk_size bytes at a time
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)

    async def search_and_download_papers(self, query: str, save_directory: Path):
        if not save_directory.exists():
            save_directory.mkdir(parents=True)

        result = []

        async for paper in self.get_papers(query):
            print("Analyze paper " + paper["paperId"])

            pdf_path = None

            # check if the paper is open access
            if paper["isOpenAccess"]:

                try:
                    pdf_url: str = paper["openAccessPdf"]["url"]
                    pdf_dir = save_directory / f'{paper["paperId"]}'
                    pdf_dir.mkdir(parents=True, exist_ok=True)
                    pdf_path = (pdf_dir / f'{paper["paperId"]}.pdf').absolute()
                    await self.download_pdf(pdf_url, pdf_path)
                except Exception as e:
                    print(e)
                    pdf_path = None
            paper["authors"] = ", ".join(
                [author["name"] for author in paper.get("authors", [])]
            )
            paper["journal"] = paper["journal"].get("name", None)
            paper_info = ArticleInfo(
                paper.get("title", None),
                paper.get("authors", None),
                paper.get("journal", None),
                paper.get("year", None),
                paper.get("abstract", None),
                paper.get("citationCount", None),
                pdf_path,
            )
            result.append(paper_info.__dict__)

        result = pd.DataFrame(result)
        return result


class ArxivSearch:

    def __init__(self, session, limit):
        self.client = arxiv.Client()
        self.session = session
        self.limit = limit

    async def get_papers(self, query: str):
        search = arxiv.Search(
            query=query,
            max_results=self.limit,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        for result in self.client.results(search):
            yield {
                "title": result.title,
                "authors": ", ".join([author.name for author in result.authors]),
                "journal": result.journal_ref,
                "year": result.published.year,
                "abstract": result.summary,
                "citationCount": None,
                "isOpenAccess": True,
                "openAccessPdf": {"url": result.pdf_url},
                "paperId": result.entry_id.split("/")[-1],
            }

    async def download_pdf(self, pdf_url: str, save_path: Path):
        async with self.session.get(pdf_url) as response:
            response.raise_for_status()
            with open(save_path, "wb") as f:
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)

    async def search_and_download_papers(self, query: str, save_directory: Path):
        if not save_directory.exists():
            save_directory.mkdir(parents=True)

        result = []

        async for paper in self.get_papers(query):
            print("Analyze paper " + paper["paperId"])

            pdf_path = None

            try:
                pdf_url: str = paper["openAccessPdf"]["url"]
                pdf_dir = save_directory / f'{paper["paperId"]}'
                pdf_dir.mkdir(parents=True, exist_ok=True)
                pdf_path = (pdf_dir / f'{paper["paperId"]}.pdf').absolute()
                await self.download_pdf(pdf_url, pdf_path)
            except Exception as e:
                print(e)
                pdf_path = None

            paper_info = ArticleInfo(
                paper.get("title", None),
                paper.get("authors", None),
                paper.get("journal", ""),
                paper.get("year", None),
                paper.get("abstract", None),
                paper.get("citationCount", None),
                pdf_path,
            )
            result.append(paper_info.__dict__)

        result = pd.DataFrame(result).drop(columns=["citationCount"])
        return result
