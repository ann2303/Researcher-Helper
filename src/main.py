import asyncio
import argparse
from pathlib import Path
import json
from aiohttp import ClientSession
from search import SemanticSearch, ArxivSearch
import utils


class Config:
    def __init__(self, config_path):
        with open(config_path, "r") as f:
            data = json.load(f)
        self.x_api_key = data.get("X-API-KEY", None)  # semantic scholar api


async def run_semantic_search(args, config):
    articles_path = args.save_directory / "articles"
    articles_path.mkdir(exist_ok=True, parents=True)

    async with ClientSession() as session:
        searcher = SemanticSearch(session, config.x_api_key, limit=args.limit)
        result = await searcher.search_and_download_papers(args.query, articles_path)

    return result


async def run_arxiv_search(args):
    articles_path = args.save_directory / "articles"
    articles_path.mkdir(exist_ok=True, parents=True)

    async with ClientSession() as session:
        searcher = ArxivSearch(session, limit=args.limit)
        result = await searcher.search_and_download_papers(args.query, articles_path)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Download open access PDFs from Semantic Scholar."
    )
    parser.add_argument("--query", type=str, help="Query to search for papers.")
    parser.add_argument(
        "--save_directory", type=Path, help="Directory to save PDFs to."
    )
    parser.add_argument(
        "--limit", type=int, default=10, help="Number of papers to download."
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to config with Semantic Scholar API and OpenAI API key.",
        default=Path(__file__).parent / "config.json",
    )
    parser.add_argument(
        "--database",
        choices=["arxiv", "semantic_scholar"],
        default="arxiv",
        help="Database to use for searching",
    )
    args = parser.parse_args()

    if args.database == "arxiv":
        result = asyncio.run(run_arxiv_search(args))
    elif args.database == "semantic_scholar":
        config = Config(args.config)
        result = asyncio.run(run_semantic_search(args, config))

    result = utils.make_hrefs_in_dataframe(
        result, ["saved_pdf", "tables_path"], ["github_links"]
    )

    result.to_html(Path(args.save_directory) / "result.html", index=False)


if __name__ == "__main__":
    main()
