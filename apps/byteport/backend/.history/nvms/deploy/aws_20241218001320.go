package deploy

import (
	"context"
	"fmt"
	"strings"

	aws "nvms/deploy/awspin"
	ec2 "nvms/deploy/awspin/ec2"
	s3 "nvms/deploy/awspin/s3"
	"nvms/models"

	"github.com/google/uuid"
)
type BuilderReq struct {
	ZipBall     []byte `json:"zipball"`
	AccessKey   string `json:"accessKey"`
	SecretKey   string `json:"secretKey"`
	ProjectName string `json:"projectName"`
}

func pushToS3(zipBall []byte, AccessKey string, SecretKey string, ProjectName string) (string,string,error) {
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
	s3Client, err := s3.NewS3(cfg)
	if err != nil {
		fmt.Println(err)
		return "","",err
	}
	fmt.Println("Created S3 client")
	bucketName := strings.ToLower(ProjectName) + "-bytebucket-" + uuid.New().String()
	err = s3Client.CreateBucket(ctx, bucketName)
	if err != nil {
			fmt.Println(err)
			return "","",err
		}
	fmt.Println("Created bucket")
	err = s3Client.PutObject(ctx, bucketName, "src.zip", zipBall)
	if err != nil {
		fmt.Println(err)
		return "","",err
	}
	fmt.Println("Uploaded to S3")
	// return uri/bucket name for later use

	return bucketName, "src.zip",nil
}

func deployEC2(AccessKey string, SecretKey string, BucketName string, service models.Service) error{
	client, err := ec2.NewEC2(aws.Config{
		AccessKeyId: AccessKey,
		SecretAccessKey: SecretKey,
		SessionToken: "",
		Endpoint: "https://ec2.us-east-1.amazonaws.com",
		Region: "us-east-1",
		Service: "ec2",
	})
	if err != nil {
		fmt.Println(err)
		return err
	}
	fmt.Println("Created EC2 client")
	params := map[string]string{
		"ImageId": "ami-0c55b159cbfafe1f0",
		
	}
	return nil;
}
 