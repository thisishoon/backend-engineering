package main

import (
	"encoding/csv"
	"fmt"
	"net/http"
	"reflect"
)

func readCSVFromUrl(url string) ([][]string, error) {
	resp, err := http.Get(url)

	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	reader := csv.NewReader(resp.Body)
	reader.Comma = ','
	fmt.Println(reader.ReadAll()[0][0][0])
	data, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	return data, nil
}

func main() {
	fmt.Println("hello")
	url := "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_hour.csv"
	data, _ := readCSVFromUrl(url)
	fmt.Println(data[1][10])
	fmt.Println(reflect.TypeOf(data[1][2]))
}

// func main() {
// 	fmt.Println("Hello word")
// 	fileURL := "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_hour.csv"
// 	readCSVFromUrl(fileURL)
// }
