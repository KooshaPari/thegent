package deploy

import (
	"bytes"
	"encoding/json"
	"fmt"

	spinhttp "github.com/fermyon/spin-go-sdk/http"
)
type BuilderReq struct {
	ZipBall     []byte `json:"zipball"`
	AccessKey   string `json:"accessKey"`
	SecretKey   string `json:"secretKey"`
	ProjectName string `json:"projectName"`
}

func pushToS3(zipBall []byte, AccessKey string, SecretKey string, ProjectName string) error {
	fmt.Println("Uploading to S3...")
	// TODO Take Given ZipBall, push Each SubFolder Individually To a singular bucket, keep track of names via map.
	/*ctx := context.Background()
	cfg, err := config.LoadDefaultConfig(ctx,
		config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(AccessKey, SecretKey, "")),
		config.WithRegion("us-east-1"),
	)
	if err != nil {
		return fmt.Errorf("failed to create session: %v", err)
	}
	svc := s3.NewFromConfig(cfg)
	bucketName := "NVMS-"+ProjectName
	// Create the bucket
	createBucketInput := &s3.CreateBucketInput{
		Bucket: aws.String(bucketName),
	}
	if _, err := svc.CreateBucket(ctx, createBucketInput); err != nil {
		return fmt.Errorf("failed to create bucket: %v", err)
	}
	// Parse the zip archive
	zipReader, err := zip.NewReader(bytes.NewReader(zipBall), int64(len(zipBall)))
	if err != nil {
		return fmt.Errorf("failed to read zip archive: %v", err)
	}
	// Upload each file in the zip archive to the bucket
	for i, file := range zipReader.File {
		fileReader, err := file.Open()
		if err != nil {
			return fmt.Errorf("failed to open file in zip archive: %v", err)
		}
		defer fileReader.Close()
		var buf bytes.Buffer
		if _, err := buf.ReadFrom(fileReader); err != nil {
			return fmt.Errorf("failed to read file content: %v", err)
		}
		uploadInput := &s3.PutObjectInput{
			Bucket: aws.String(bucketName),
			Key:    aws.String(file.Name),
			Body:   bytes.NewReader(buf.Bytes()),
		}
		_, err = svc.PutObject(ctx, uploadInput)
		if err != nil {
			return fmt.Errorf("failed to upload file %d to bucket: %v", i, err)
		}
	}*/
	serviceDets := BuilderReq{
		ZipBall:     zipBall,
		AccessKey:   AccessKey,
		SecretKey:   SecretKey,
		ProjectName: ProjectName,}
	jsonBytes, err := json.Marshal(serviceDets)
	if err != nil {
		return err
	}
	req := bytes.NewReader(jsonBytes)


	_, err = spinhttp.Post("/build", "application/json",req)
	if err != nil {
		return fmt.Errorf("failed to send request: %v", err)
	}
	
	fmt.Println("Response: ", resp)

	return nil
}

/*
func getServiceFolder(name string, zipBall []byte) (map[string][]byte,string, error) {
	fileMap, err := processZip(zipBall)
	if err != nil {
		return nil, "", fmt.Errorf("failed to process zip file: %v", err)
	}
	rootDir, err := getRootDir(fileMap)
	if err != nil {
		return nil, "", fmt.Errorf("failed to get root directory: %v", err)
	}

	serviceDir := rootDir + name
	if _, ok := fileMap[serviceDir]; !ok {
		return nil, "", fmt.Errorf("service directory %s not found in zip file", serviceDir)
	}
	return fileMap, serviceDir, nil
}
*/