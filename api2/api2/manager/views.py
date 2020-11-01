import json
import asyncio
from datetime import datetime, timedelta
from dateutil.parser import parse, isoparse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from elasticsearch import Elasticsearch, ElasticsearchException, helpers, NotFoundError


class ManagerView(APIView):
    es = Elasticsearch('localhost:9200')
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
            start = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        else:
            try:
                end = isoparse(end)
            except Exception as e:
                HttpResponse(e)

        rangeTimeQuery = {"query": {"bool": {"filter": [
            {"range": {"time": {"gte": start, "lte": end}}}]}}}

        if pk is not None:  # singloe row
            rangeTimeQuery['query']['bool']['filter'].append(
                {"terms": {"id": [pk]}})

        elif request.body != b'':  # multiple row
            ids = (json.loads(request.body)['id'])
            rangeTimeQuery['query']['bool']['filter'].append(
                {"terms": {"id": ids}})

        self.es.indices.refresh(index=self.index)
        res = self.es.search(index='earthquake', body=rangeTimeQuery)
        result = [r['_source'] for r in res['hits']['hits']]

        return HttpResponse(json.dumps(result),
                            content_type='application/json; charset=utf8')

    def post(self, request):
        data = json.loads(request.body)
        result = []
        if type(data) is not list:
            try:
                data = json.loads(data)
            except:
                pass

        try:
            if type(data) is dict:
                data = [data]
            else:
                for doc in data:
                    res = self.es.index(index='earthquake', body=doc, id=doc['id'])
                    result.append(res['result'])

        except ElasticsearchException as e:
            print(e)
            return HttpResponse(status=400)

        print(result)

        return HttpResponse("POST OK")

    def put(self, request, pk=None):
        data = json.loads(request.body)
        if type(data) is dict:
            data = [data]

        for doc in data:
            if pk is not None:
                updated_id = pk
            else:
                updated_id = doc['id']

            self.es.update(index=self.index, id=updated_id,
                           body={"doc": doc})

        return HttpResponse("UPDATE OK")

    def delete(self, request, pk=None):
        if pk is not None:
            self.es.delete(index=self.index, id=pk)
            return HttpResponse("DELETE OK")

        data = json.loads(request.body)["id"]
        try:
            for deleted_id in data:
                self.es.delete(index=self.index, id=deleted_id)
        except NotFoundError:
            pass

        return HttpResponse("DELETE OK")


