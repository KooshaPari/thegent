package deploy

import (
	"context"
	"fmt"

	aws "nvms/deploy/awspin"
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
		Endpoint: "https://s3.us-west-2.amazonaws.com",
		Region: "us-west-2",
		Service: "s3",
	}
	ctx := context.Background()
	s3Client, err := aws.NewS3(cfg)
	if err != nil {
		fmt.Println(err)
		return err
	}
	fmt.Println("Created S3 client")
	err = s3Client.CreateBucket(ctx, ProjectName)
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
 