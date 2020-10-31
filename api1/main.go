package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
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

	for i := 0; i < len(data); i++ {
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
	// url := "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2014-01-01&endtime=2014-01-02"
	data, _ := readCSVFromUrl(url)
	fmt.Println(len(data))

	JSON, _ := convertJSON(data)
	fmt.Println((JSON))
}

func main() {
	// dataDownloader()
	http.HandleFunc("/api1", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {
			fmt.Println("Hello World")
		} else if r.Method == "POST" {
			dataDownloader()
		}
	})

	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatalln(err)
	}

}
