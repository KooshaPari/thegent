FROM golang:1.24-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /byteport-api .

FROM gcr.io/distroless/static-debian12
COPY --from=builder /byteport-api /byteport-api
EXPOSE 8080
ENTRYPOINT ["/byteport-api"]
