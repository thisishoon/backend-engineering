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

func dataDownloader() {
	url := "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_hour.csv"
	data, _ := readCSVFromUrl(url)

	beforeJSON, _ := convertJSON(data)
	JSON, _ := json.Marshal(beforeJSON)
	buff := bytes.NewBuffer(JSON)

	resp, err := http.Post("http://localhost:8000/", "application/json", buff)
	if err != nil {
		panic(err)
	}
	fmt.Println(resp.Body)

	defer resp.Body.Close()

	//check response
	respBody, err := ioutil.ReadAll(resp.Body)
	if err == nil {
		str := string(respBody)
		println(str)
	}
}

func doPeriodically() {
	fmt.Println("주기적 다운로드")
	dataDownloader()
}

func runPeriodically() {
	for {
		doPeriodically()
		time.Sleep(time.Second * 30)
	}
}

func main() {
	// dataDownloader()
	go runPeriodically()
	http.HandleFunc("/api1", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {
			fmt.Println("Hello World")
		} else if r.Method == "POST" {
			fmt.Println("선택적 다운로드")
			dataDownloader()
		}
	})

	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatalln(err)
	}
}
