FROM golang:1.19.6-buster AS golangbuild
RUN apt-get update && apt-get install -y git gcc
WORKDIR /
RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest && go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

FROM python:3.10.10-buster
COPY --from=golangbuild /go/bin /go/bin
RUN apt-get update && apt-get install -y g++
WORKDIR /app
COPY . /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt
