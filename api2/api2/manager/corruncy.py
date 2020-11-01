import asyncio
from elasticsearch import Elasticsearch


async def create_data(es, doc):
    res = es.index(index="earthquake", id=doc['id'], body=doc)
    return res


async def update_data(es, doc):
    res = es.update(index="earthquake", id=doc['id'], body={"doc": doc})
    return res


async def delete_data(es, deleted_id):
    res = es.delete(index="earthquake", id=deleted_id)
    return res


async def post_concurrency(es, docs):
    cos = [create_data(es, doc) for doc in docs]
    res = await asyncio.gather(*cos)
    return res


async def patch_concurrency(es, docs):
    cos = [update_data(es, doc) for doc in docs]
    res = await asyncio.gather(*cos)
    return res


async def delete_concurrency(es, ids):
    cos = [delete_data(es, id) for id in ids]
    res = await asyncio.gather(*cos)
    return res



