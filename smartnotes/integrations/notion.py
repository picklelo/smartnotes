import os
from notion_client import Client
from notion2md.exporter.block import StringExporter

notion = Client(auth=os.environ["NOTION_TOKEN"])

def search_page(query: str):
    try:
        page_id = notion.search(query=query)["results"][0]["id"]
    except IndexError:
        raise ValueError(f"Page '{query}' not found.")
    return page_id


def get_page_content(page_name: str):
    page = search_page(page_name)
    return StringExporter(block_id=page, output_path="...").export()
