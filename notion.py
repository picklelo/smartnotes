import os
from notion_client import Client

notion = Client(auth=os.environ["NOTION_TOKEN"])
search = notion.search(query="Roadmap Planning")["results"][0]["id"]
page = notion.pages.retrieve(page_id=search)
block = notion.blocks.children.list(block_id=search)['results']
block_ids = [b['id'] for b in block]
print(block_ids)
blocks = [notion.blocks.retrieve(block_id=bid) for bid in block_ids]
print(blocks)
print(page)
print(len(block))
print(block)
