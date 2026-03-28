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
		Endpoint: "",
		Region: "us-west-1",
		Service: "s3",
	}
	ctx := context.Background()
	s3Client, err := aws.NewS3(cfg)
			if err != nil {
				fmt.Println(err)
				return err
			}

			err = s3Client.CreateBucket(ctx, ProjectName)
			if err != nil {
				fmt.Println(err)
				return err
			}

			err = s3Client.PutObject(ctx, ProjectName, "hello.txt", []byte("Hello, S3!"))
			if err != nil {
				fmt.Println(err)
				return err
			}


 

	return nil
}
 