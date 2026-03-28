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


func pushToS3(zipBall []byte, AccessKey string, SecretKey string, ProjectName string) (S3DeploymentInfo,error) {
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
		return S3DeploymentInfo{},err
	}
	fmt.Println("Created S3 client")
	bucketName := strings.ToLower(ProjectName) + "-bytebucket-" + uuid.New().String()
	err = s3Client.CreateBucket(ctx, bucketName)
	if err != nil {
			fmt.Println(err)
			return S3DeploymentInfo{},err
		}
		
	fmt.Println("Created bucket")
	err = s3Client.PutObject(ctx, bucketName, "src.zip", zipBall)
	if err != nil {
		fmt.Println(err)
		return S3DeploymentInfo{},err
	}
	fmt.Println("Uploaded to S3")
	// return uri/bucket name for later use
	info := S3DeploymentInfo{
        BucketName:  bucketName,
        ObjectKey:   "src.zip",
        Region:      "us-east-1",
        BucketARN:   fmt.Sprintf("arn:aws:s3:::%s", bucketName),
        ObjectURL:   fmt.Sprintf("https://%s.s3.amazonaws.com/%s", bucketName, "src.zip"),
        ContentHash: aws.GetPayloadHash(zipBall),
    }
	return info,nil
}

func deployEC2(AccessKey string, SecretKey string, BucketName string, service models.Service) ([]EC2InstanceInfo,error){
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
		return []EC2InstanceInfo{},err
	}
	fmt.Println("Created EC2 client")
	params := map[string]string{
		"ImageId": "ami-0166fe664262f664c",
		"InstanceType": "t2.micro",
		"MinCount": "1",
		"MaxCount": "1",
	}
	fmt.Println("Creating instance")
	resp, err := client.RunInstances(context.Background(), params)
	fmt.Println(resp)
	var instances []EC2InstanceInfo
    for _, instance := range resp.Instances {
        newInstance := EC2InstanceInfo{
            InstanceID:     instance.InstanceId,
            PublicIP:       instance.PublicIP,
            PrivateIP:      instance.PrivateIP,
            PublicDNS:      instance.PublicDNS,
            PrivateDNS:     instance.PrivateDNS,
            State:          instance.State,
            KeyPairName:    instance.KeyPairName,
            SecurityGroups: instance.SecurityGroups,
            SubnetID:       instance.SubnetId,
            Region:        "us-east-1",
        }
        instances = append(instances, newInstance)
    }
	return instances,nil;
}
 // S3DeploymentInfo contains information about deployed S3 resources
type S3DeploymentInfo struct {
    BucketName   string   // Name of the created bucket
    ObjectKey    string   // Key of the uploaded object (e.g., "src.zip")
    Region       string   // AWS region where bucket was created
    BucketARN    string   // ARN of the bucket
    ObjectURL    string   // Full URL to access the object
    ContentHash  string   // SHA256 hash of uploaded content
}

// EC2InstanceInfo contains information about deployed EC2 instances
type EC2InstanceInfo struct {
    InstanceID       string   // EC2 instance ID
    PublicIP         string   // Public IP address
    PrivateIP        string   // Private IP address
    PublicDNS        string   // Public DNS name
    PrivateDNS       string   // Private DNS name
    State            string   // Current instance state
    KeyPairName      string   // Name of the SSH key pair
    SecurityGroups   []string // List of security group IDs
    SubnetID         string   // Subnet ID where instance is launched
    Region           string   // AWS region where instance is launched
}
type BuilderReq struct {
	ZipBall     []byte `json:"zipball"`
	AccessKey   string `json:"accessKey"`
	SecretKey   string `json:"secretKey"`
	ProjectName string `json:"projectName"`
}
func buildEC2Service() (string,error){
	// genScript
	buildScript, err := generateBuildScript()
	// runservice

	return "Complete",nil
}
func generateBuildScript(bucket S3DeploymentInfo, service models.Service, creds models.AwsCreds)(string,error){
	 script := `#!/bin/bash
set -e

# Update system
dnf update -y

# Install AWS CLI and required tools
dnf install -y unzip tar gzip

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Configure AWS credentials
mkdir -p /root/.aws
cat > /root/.aws/credentials << EOF
[default]
aws_access_key_id = %s
aws_secret_access_key = %s
region = us-east-1
EOF

# Create working directory
mkdir -p /app
cd /app

# Download code from S3
aws s3 cp s3://%s/%s src.zip

# Unzip the code
unzip src.zip
rm src.zip

# Find the actual directory (in case the zip contains a root folder)
EXTRACT_DIR=$(ls -d */ | head -n 1)
cd "$EXTRACT_DIR"

# Navigate to service directory
cd %s

# Install build dependencies based on service type
if [[ -f "go.mod" ]]; then
    # Install Go
    dnf install -y golang
elif [[ -f "package.json" ]]; then
    # Install Node.js and npm
    dnf install -y nodejs nodejs-npm
fi

# Run build commands
%s

echo "Build complete!"
`
	var buildCmds string
    for _, cmd := range service.Build {
        buildCmds += fmt.Sprintf("%s\n", cmd)
    }

    // Format script with actual values
    script = fmt.Sprintf(script,
        creds.accessKey,
        secretKey,
        bucket.BucketName,
        bucket.ObjectKey,
        service.Path,
        buildCmds,
    )

    return base64.StdEncoding.EncodeToString([]byte(script))
	return "",nil;
}
func runService(){
	// run service
	// return logs
}
func windDownService(){
	// terminate instance
}
