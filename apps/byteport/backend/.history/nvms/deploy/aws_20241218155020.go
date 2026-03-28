package deploy

import (
	"context"
	"encoding/base64"
	"fmt"
	"strings"

	aws "nvms/deploy/awspin"
	ec2 "nvms/deploy/awspin/ec2"
	s3 "nvms/deploy/awspin/s3"
	"nvms/models"

	"github.com/google/uuid"
)

func generateBuildScript(s3Info S3DeploymentInfo, service models.Service, accessKey, secretKey string) string {
    script := `#!/bin/bash
set -e

# Configure logging
exec 1> >(logger -s -t $(basename $0)) 2>&1
BUILD_LOG="/var/log/user-data-build.log"
touch $BUILD_LOG
chmod 644 $BUILD_LOG

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a $BUILD_LOG
}

log "Starting build process..."

# Update system
log "Updating system packages..."
yum update -y

# Install AWS CLI and required tools
log "Installing required tools..."
yum install -y unzip tar gzip

# Install AWS CLI v2
log "Installing AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -f awscliv2.zip
rm -rf aws/

# Configure AWS credentials
log "Configuring AWS credentials..."
mkdir -p /root/.aws
cat > /root/.aws/credentials << EOF
[default]
aws_access_key_id = %s
aws_secret_access_key = %s
region = us-east-1
EOF

# Verify AWS configuration
aws configure list

# Create working directory
log "Creating working directory..."
mkdir -p /app
cd /app

# Download code from S3
log "Downloading code from S3..."
aws s3 cp s3://%s/%s src.zip

# Unzip the code
log "Extracting code..."
unzip src.zip
rm src.zip

# Find the actual directory
EXTRACT_DIR=$(ls -d */ | head -n 1)
cd "$EXTRACT_DIR"

# Navigate to service directory
log "Navigating to service directory: %s"
cd %s

# Install build dependencies based on service type
if [[ -f "go.mod" ]]; then
    log "Installing Go..."
    yum install -y golang
elif [[ -f "package.json" ]]; then
    log "Installing Node.js..."
    curl -sL https://rpm.nodesource.com/setup_18.x | bash -
    yum install -y nodejs
fi

# Run build commands
log "Running build commands..."
%s

# Create status file for checking build status
cat > /var/log/build-status.json << EOF
{
    "status": "complete",
    "service": "%s",
    "buildTime": "$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)",
    "buildLog": "$BUILD_LOG"
}
EOF

# Create systemd service
log "Creating systemd service..."
cat > /etc/systemd/system/%s.service << EOF
[Unit]
Description=%s Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/app/$EXTRACT_DIR/%s
ExecStart=%s
Restart=always
Environment=PORT=%d

[Install]
WantedBy=multi-user.target
EOF

# Start service
log "Starting service..."
systemctl daemon-reload
systemctl enable %s
systemctl start %s

log "Build and deployment complete!"
`
    // For Node.js commands, format them properly
    var buildCommands string
    if len(service.Build) > 0 {
        commands := make([]string, len(service.Build))
        for i, cmd := range service.Build {
            commands[i] = fmt.Sprintf("log 'Running: %s' && %s", cmd, cmd)
        }
        buildCommands = strings.Join(commands, " && ")
    }

    // Format script with actual values
    formattedScript := fmt.Sprintf(script,
        accessKey,
        secretKey,
        s3Info.BucketName,
        s3Info.ObjectKey,
        service.Path,
        service.Path,
        buildCommands,
        service.Name,
        service.Name,
        service.Name,
        service.Path,
        strings.Join(service.Build, " && "),  // ExecStart command
        service.Port,
        service.Name,
        service.Name,
    )
	fmt.Println("Formatted script: ", formattedScript)
    return base64.StdEncoding.EncodeToString([]byte(formattedScript))
}
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

func deployEC2(AccessKey string, SecretKey string, bucket S3DeploymentInfo, service models.Service) ([]EC2InstanceInfo,error){
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
	buildScript := generateBuildScript(bucket, service,AccessKey, SecretKey)
	fmt.Println("Generated build script: ", buildScript)
	fmt.Println("Created EC2 client")
	params := map[string]string{
		"ImageId": "ami-0166fe664262f664c",
		"InstanceType": "t2.micro",
		"UserData": buildScript,
		"MinCount": "1",
		"MaxCount": "1",
	}
	fmt.Println("Creating instance")
	resp, err := client.RunInstances(context.Background(), params)
	fmt.Println(resp)
	var instances []EC2InstanceInfo
    /*for _, instance := range resp.Instances {
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
    }*/
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