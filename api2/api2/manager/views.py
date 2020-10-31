from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
import json
from datetime import datetime, timedelta
from dateutil.parser import parse, isoparse


from elasticsearch import Elasticsearch, ElasticsearchException, helpers


# Create your views here.

class ManagerView(APIView):
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

        es = Elasticsearch('localhost:9200')
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

        res = es.search(index='earthquake', body=query)
        result = []
        for i in res['hits']['hits']:
            result.append(i['_source'])

        return HttpResponse(json.dumps(result),
                            content_type='application/json; charset=utf8')


    def post(self, request):
        es = Elasticsearch('localhost:9200')
        data = json.loads(request.body)
        result = []

        try:
            if len(data) <= 1:
                res = es.index(index='earthquake', body=data)
                result.append(res['result'])
            else:
                res = helpers.bulk(es, data, index='earthquake')
                result = result

        except ElasticsearchException:
            print('ElasticSearch is not running')
            return HttpResponse(status=400)

        return HttpResponse("POST OK")


