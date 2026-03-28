package deploy

import (
	"context"
	"fmt"

	aws "nvms/deploy/awspin"

	"github.com/google/uuid"
)
type BuilderReq struct {
	ZipBall     []byte `json:"zipball"`
	AccessKey   string `json:"accessKey"`
	SecretKey   string `json:"secretKey"`
	ProjectName string `json:"projectName"`
}

func pushToS3(zipBall []byte, AccessKey string, SecretKey string, ProjectName string) error {
	fmt.Println("Uploading to S3...")
 	cfg := aws.Config{
		AccessKeyId: AccessKey,
		SecretAccessKey: SecretKey,
		SessionToken: "",
		Endpoint: "https://s3.us-east-1.amazonaws.com",
		Region: "us-east-1",
		Service: "s3",
	}
	ctx := context.Background()
	s3Client, err := aws.NewS3(cfg)
	if err != nil {
		fmt.Println(err)
		return err
	}
	fmt.Println("Created S3 client")
	bucketName := ProjectName. + "-bytebucket-" + uuid.New().String()
	err = s3Client.CreateBucket(ctx, bucketName)
	if err != nil {
			fmt.Println(err)
			return err
		}
	fmt.Println("Created bucket")
	err = s3Client.PutObject(ctx, ProjectName, "hello.txt", []byte("Hello, S3!"))
	if err != nil {
		fmt.Println(err)
		return err
	}
	fmt.Println("Uploaded to S3")
	return nil
}
 