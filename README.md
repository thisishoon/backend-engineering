# SW Engineering Backend 개발자 사전 과제

## Table of Contents

- [About the Project](notion://www.notion.so/thisishoon/skt-68c9eb53d5994f73a4f8c61b8b6543d2#about-the-project)
- [Getting Started](notion://www.notion.so/thisishoon/skt-68c9eb53d5994f73a4f8c61b8b6543d2#getting-started)
- [Usage](notion://www.notion.so/thisishoon/skt-68c9eb53d5994f73a4f8c61b8b6543d2#usage)

## About The Project

**API 1: Data Downloader - Golang**

- 지난 1시간 동안의 지진 기록 (M1.0+ Earthquakes) CSV 파일을 1시간 간격의 주기적으로 다운로드 (Sleep과 고루틴 이용)
- 지진 기록 데이터에 맞춰 타입 및 JSON 변환
- net/http 모듈을 사용하여 유저의 post 요청받아 수동으로 다운로드 후 API2의 POST를 통해 새로운 기록 저장

**API 2: Data Manager - Python, Django**

- id 필드를 URL의 path parameter로 설정하여 단인 데이터에 대한 CRUD 제공
- time 필드를 URL의 query string으로 설정하여 시간 범위로 쿼리 지원
- Request Body의 id 값을 활용하여 여러 데이터에 대한 CRUD 제공
- 코루틴, 태스크를 활용하여 하나의 쿼리로 Bulk 작업

**DB - ElasticSearch**

- 지진 기록의 유일한 키인 id 필드를 pk로 사용하여 중복을 제거

**Docker**

- API 1, API 2, DB를 각각 Docker로 구성하여 docker-compose로 실행 가능하도록 세팅
- docker-compose의 links를 통해 컨테이너간 통신
- 명령어 실행 시 설치가 완료되는 시간을 제어하기 위해 API 1은 API 2를, API 2는 DB를 바라보아 완전히 실행되었는지 확인하고 정상적으로 모두 올라왔을 시 API 1의 주기적 다운로드 실행

## Getting Started

- Clone Repository

```
$ git clone <https://github.com/thisishoon/backend-engineering.git>
$ cd backend-engineenring

```

- build docker image & run container using docker, docker-compose
(It takes from 30s to 1m)

```
$ docker-compose up --remove-orphans --build

```

# API 1 Document

### **수동 다운로드 요청**

URL : `localhost:8001/`

Method : `POST`

- Success Response

Code : `200 OK`

Content : `"POST OK"`

# API 2 Document

### 0. Parameter Explain

1. id=[string] (path parameter)
- (generally) [two-character network identifier](https://earthquake.usgs.gov/data/comcat/data-eventterms.php#net) with a (generally) [eight-character network-assigned code](https://earthquake.usgs.gov/data/comcat/data-eventterms.php#code).
- A unique identifier for the event. This is the current preferred id for the event, and may change over time.
1. time=[string] (query string parameter)
- All times use ISO8601 Date/Time format. Unless a timezone is specified, UTC is assumed. Examples:
- *2020-11-01*, Implicit UTC timezone, and time at start of the day (00:00:00)
- *2020-11-01T16:50:05*, Implicit UTC timezone.
- *2020-11-01T16:50:05+00:00*, Explicit timezone.

## 1. CRUD API for single row

### Read

URL : `localhost:8000/{id}`

Method : `GET`

URL Path Params (Required) : `id`

- Success Response

Code : `200 OK`

- Example

```
GET/ <https://localhost:8002/ak020e2c6p8f>

```

Content :

```
    {
        "depth": "12.5",
        "depthError": "0.4",
        "dmin": "",
        "gap": "",
        "horizontalError": "",
        "id": "ak020e2c6p8f",
        "time": "2020-11-01T16:35:30.873Z",
        ...
    }

```

### Create

URL : `localhost:8002/`

Method : `POST`

URL Path Params (Required) : `id`

Request Body : 1. required: `id` 2. optional: All except id

Success Response Code : `200 OK`

- Request Example

```
{
        "depth": "17.55",
        "depthError": "0.88",
        "dmin": "0.03687",
        "gap": "108",
        "horizontalError": "0.8",
        "id": "ci39453463",
        "latitude": "33.6758347",
        "locationSource": "ci",
        "longitude": "-116.7011642",
        "mag": "1.08",
        "magError": "0.265",
        "magNst": "7",
        "magSource": "ci",
        "magType": "ml",
        "net": "ci",
        "nst": "20",
        "place": "7km SSE of Idyllwild, CA",
        "rms": "0.2",
        "status": "automatic",
        "time": "2020-11-01T18:27:28.090Z",
        "type": "earthquake",
        "updated": "2020-11-01T18:29:40.576Z"
    }

```

### Update

- URL : `localhost:8002/{id}`
- Method : `PATCH`
- URL Path Params (Required) : `id`
- Request Body : (required): `All filed`
- Success Response Code : `200 OK`
- Request Example

```
{
        "depth": "20.55",
        "depthError": "3.88",
        "dmin": "0.03687",
        "gap": "108",
        "horizontalError": "0.8",
        "id": "ci39453463"
    }

```

### Delete

URL : `localhost:8002/{id}`

Method : `DELETE`

Success Response Code : `200 O`

URL Path Params (Required) : `id`

## 2. CRUD Bulk API for multiple row

### Read

> 시간(time)범위 쿼리 지원

- ISO8601 Date/Time format [string]
- default end value = NOW, start value = NOW - 30days

> key가 id, value가 id의 배열인 JSON을 요청받아 id를 기반으로 데이터 삭제

- id 값을 명시하지 않으면 모든 id 값의 데이터를 반환

URL : `localhost:8000/`

Method : `GET`

URL Query String Params (Optional) : `start, end`

Success Response Code : `200 OK`

Request Body (Optional) : key:`id`[string], value: [`id`, `id`, ...] [list]

- Example

```
GET/ <https://localhost:8002/?start=2020-11-01T16:10:32.530Z&end=2020-11-01T16:32:05.771Z>

Body
{
    "id" = ["ak020e2c6p8f", "nc73477021", ...]
}

```

- Success Response

Content :

```
[
    {
        "depth": "12.5",
        "depthError": "0.4",
        "dmin": "",
        "gap": "",
        "horizontalError": "",
        "id": "ak020e2c6p8f",
        "time": "2020-11-01T16:35:30.873Z",
        ...
    },
    {
        "depth": "0.26",
        "depthError": "0.48",
        "dmin": "0.0109",
        "gap": "62",
        "horizontalError": "0.28",
        "id": "nc73477021",
        "time": "2020-11-01T16:15:42.050Z",
        ...
    }
		...
]

```

### Create

> JSON 배열을 요청받아 필수 id를 기반으로 데이터를 삽입.

URL : `localhost:8002/`

Method : `POST`

Request Body : JSON Array of data

1. required: `id` `time` 
2. optional: All except id, time
- Example

```
POST/ <https://localhost:8002/>

Body
[
    {
        "depth": 12.5,
        "depthError": 0.4,
        "dmin": 0,
        "gap": 0,
        "horizontalError": ,
        "id": "ak020e2c6p8f",
        "latitude": 64.3745,
        "locationSource": "ak",
        "longitude": -149.709,
        "mag": 1.3,
        "magError": 0,
        "magNst": 0,
        "magSource": "ak",
        "magType": "ml",
        "net": "ak",
        "nst": 0,
        "place": "25 km W of Anderson, Alaska",
        "rms": 0.48,
        "status": "automatic",
        "time": "2020-11-01T16:35:30.873Z",
        "type": "earthquake",
        "updated": "2020-11-01T16:42:44.137Z"
    },
    {
        "depth": 0.26,
        "depthError": 0.48,
        "dmin": 0.0109,
        "gap": 62,
        "horizontalError": 0.28,
        "id": "nc73477021",
        "latitude": 38.7971649,
        "locationSource": "nc",
        "longitude": -122.793335,
        "mag": 2.14,
        "magError": 0.26,
        "magNst": 16,
        "magSource": "nc",
        "magType": "md",
        "net": "nc",
        "nst": 21,
        "place": "4km NW of The Geysers, CA",
        "rms": 0.14,
        "status": "automatic",
        "time": "2020-11-01T16:15:42.050Z",
        "type": "earthquake",
        "updated": "2020-11-01T16:35:04.642Z"
    }
]

```

Success Response Code : `200 OK`

### Update

> JSON 배열을 요청받아 필수 id를 기반으로 데이터를 일부 수정

URL : `localhost:8002/`

Method : `PATCH`

Request Body : JSON Array of data, required: all field

1. required: `id`
2. optional: All except id

Success Response Code : `200 OK`

```
PATCH/ <https://localhost:8002/>

Body
[
    {
        "id": "ak020e2c6p8f",
        "latitude": "210000",
					...
    },
    {
        "id": "nc73477021",
        "latitude": "90.7971649",
        "locationSource": "nc",
					...
    }
]

```

### Delete

> key가 id, value가 id의 배열인 JSON을 요청받아 id를 기반으로 데이터 삭제

URL : `localhost:8002/`

Method : `DELETE`

Request Body (Optional) : { key: `id`[string], value: [`id`, `id`, ...] [list] }

Success Response Code : `200 OK`

- Example

```
DELETE/ <https://localhost:8002/>

Body
{
    "id" = ["ak020e2c6p8f", "nc73477021", ...]
}

```