from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
import json
from datetime import datetime, timedelta
from dateutil.parser import parse, isoparse

from elasticsearch import Elasticsearch, ElasticsearchException, helpers, NotFoundError


# Create your views here.

class ManagerView(APIView):
    es = Elasticsearch('localhost:9200')
    index = "earthquake"

    def get(self, request, *args, **kwargs):
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

        query = {
            "query": {
                "range": {
                    "time": {
                        "gte": start,
                        "lte": end
                    }
                }
            }
        }
        res = self.es.search(index='earthquake', body=query)
        result = []
        for i in res['hits']['hits']:
            result.append(i['_source'])

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

        data = json.loads(request.body)
        print(data)
        try:
            for doc in data:
                deleted_id = doc['id']
                self.es.delete(index=self.index, id=deleted_id)
        except NotFoundError:
            pass

        return HttpResponse("DELETE OK")
