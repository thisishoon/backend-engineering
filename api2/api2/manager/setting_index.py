from elasticsearch import Elasticsearch

es = Elasticsearch()
index_name = "earthquake"


def make_index():
    if es.indices.exists(index=index_name):
        print('existing earthquake index in use')
    else:
        es.indices.create(index=index_name)


if __name__ == '__main__':
    make_index()
