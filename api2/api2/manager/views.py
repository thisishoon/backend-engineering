import json
import asyncio
from datetime import datetime, timedelta
from dateutil.parser import parse, isoparse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from elasticsearch import Elasticsearch, ElasticsearchException, helpers, NotFoundError
from .corruncy import post_concurrency, patch_concurrency, delete_concurrency


class ManagerView(APIView):
    es = Elasticsearch("elasticsearch:9200")
    index = "earthquake"

    def get(self, request, pk=None):
        start = request.query_params.get('start')
        end = request.query_params.get('end')

        if end is None:
            end = datetime.utcnow().isoformat()
        else:
            try:
                end = isoparse(end)
            except Exception as e:
                HttpResponse(e)

        if start is None:
            start = (datetime.utcnow() - timedelta(days=30)).isoformat()
        else:
            try:
                end = isoparse(end)
            except Exception as e:
                HttpResponse(e)

        rangeTimeQuery = {"size": 10000, "query": {"bool": {"filter": [
            {"range": {"time": {"gte": start, "lte": end}}}]}}}
        self.es.indices.refresh(index=self.index)

        if pk is not None:  # singloe row
            rangeTimeQuery['query']['bool']['filter'].append(
                {"terms": {"id": [pk]}})

        elif request.body != b'':  # multiple row
            ids = (json.loads(request.body)['id'])
            rangeTimeQuery['query']['bool']['filter'].append(
                {"terms": {"id": ids}})

        res = self.es.search(index='earthquake', body=rangeTimeQuery)
        result = [r['_source'] for r in res['hits']['hits']]
        if pk is not None:
            if not result:
                result = []
            else:
                result = result[0]

        return HttpResponse(json.dumps(result),
                            content_type='application/json; charset=utf8')

    def post(self, request):
        data = json.loads(request.body)

        if type(data) is not list:
            try:
                data = json.loads(data)
            except:
                pass
        if type(data) is dict:
            data = [data]

        try:
            asyncio.run(post_concurrency(self.es, data))
        except ElasticsearchException as e:
            print(e)
            return HttpResponse(status=400)

        return HttpResponse("POST OK")

    def patch(self, request, pk=None):

        data = json.loads(request.body)
        if type(data) is dict:
            data = [data]

        self.es.indices.refresh(index=self.index)
        for doc in data:
            if pk is not None:
                self.es.update(index=self.index, id=pk,
                               body={"doc": doc})
            else:
                asyncio.run(patch_concurrency(self.es, data))

        return HttpResponse("UPDATE OK")

    def delete(self, request, pk=None):
        if pk is not None:
            self.es.delete(index=self.index, id=pk)
            return HttpResponse("DELETE OK")

        data = json.loads(request.body)["id"]

        try:
            asyncio.run(delete_concurrency(self.es, data))
        except NotFoundError:
            pass

        return HttpResponse("DELETE OK")
