package main

import (
	"bytes"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"
)

func readCSVFromUrl(url string) ([][]string, error) {
	resp, err := http.Get(url)

	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	reader := csv.NewReader(resp.Body)
	reader.Comma = ','

	data, err := reader.ReadAll()

	if err != nil {
		return nil, err
	}

	return data, nil
}

func convertJSON(data [][]string) (interface{}, error) {
	parseData := make([]map[string]interface{}, 0, 0)

	for i := 1; i < len(data); i++ {
		m := make(map[string]interface{})
		for j := 0; j < len(data[i]); j++ {
			key := data[0][j]
			value := data[i][j]
			m[key] = value
		}
		parseData = append(parseData, m)
	}
	result, _ := json.Marshal(parseData)
	return string(result), nil
}

func dataDownloader() (result string) {
	fmt.Println("새 기록 저장 (POST to API2)")

	url := "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_hour.csv"
	data, _ := readCSVFromUrl(url)
	beforeJSON, _ := convertJSON(data)
	JSON, _ := json.Marshal(beforeJSON)
	buff := bytes.NewBuffer(JSON)

	resp, err := http.Post("http://api2:8002/", "application/json", buff)
	if err != nil {
		panic(err)
	}

	defer resp.Body.Close()

	//check response
	respBody, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	return string(respBody)
}

func doPeriodically() {
	fmt.Println("주기적 다운로드 시작(1시간 간격)")
	dataDownloader()
}

func runPeriodically() {
	for {
		doPeriodically()
		time.Sleep(time.Minute * 60)
	}
}

func waitAPI2() {
	time.Sleep(time.Second * 15)
	for {
		_, err := http.Get("http://api2:8002/")
		if err != nil {
			time.Sleep(time.Second * 5)
			fmt.Println("api1 is waiting for api2")
		} else {
			fmt.Println("api1 start")
			break
		}
	}
}

func main() {
	waitAPI2()
	go runPeriodically()

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {
			fmt.Println("Hello World")
		} else if r.Method == "POST" {
			fmt.Println("수동 다운로드 요청")
			res := dataDownloader()
			w.WriteHeader(200)
			w.Write([]byte(res))
		}
	})

	err := http.ListenAndServe(":8001", nil)
	if err != nil {
		log.Fatalln(err)
	}
}
