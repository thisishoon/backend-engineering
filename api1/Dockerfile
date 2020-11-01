FROM amd64/golang:1.14

RUN mkdir /golang
ADD . /golang/
WORKDIR /golang

RUN go build -o main .

CMD ["/golang/main"]




