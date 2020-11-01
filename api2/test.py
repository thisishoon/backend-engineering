import asyncio
import time
from elasticsearch import Elasticsearch, helpers


dummy = [
    {
        "id": "a",
        "name": "aa"
    },
    {
        "id": "b",
        "name": "bb"
    }
]


async def post_put_concurrency(es, doc):
    res = es.index(index="earthquake", id=doc['id'], body=doc)
    return res


async def main():
    data = dummy
    cos = [post_put_concurrency(Elasticsearch(), i) for i in data]
    res = await asyncio.gather(*cos)
    print(res)


asyncio.run(main())
