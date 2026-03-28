package deploy

import (
	"bytes"
	"encoding/json"
	"fmt"
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
		SecretKey: SecretKey,
		SessionToken: "",
		
	}
	

 

	return nil
}
 