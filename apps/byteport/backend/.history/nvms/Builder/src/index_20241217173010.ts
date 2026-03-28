import { ResponseBuilder } from "@fermyon/spin-sdk";
import {
	S3Client,
	CreateBucketCommand,
	PutObjectCommand,
	GetObjectCommand,
	CreateBucketCommandInput,
	BucketLocationConstraint,
} from "@aws-sdk/client-s3";
import { v4 as uuidv4 } from "uuid";

export async function handler(req: Request, res: ResponseBuilder) {
	console.log(req);
	try {
		// Parse the request body as JSON
		const bodyText = await req.text();
		const project: Project = JSON.parse(bodyText);
		console.log("Pushing")
		await pushToS3(project);

		return {
			status: 200,
			headers: { "content-type": "application/json" },
			body: JSON.stringify({ message: "Upload successful" }),
		};
	} catch (error) {
		console.error("Error:", error instanceof Error);
		return {
			status: 500,
			headers: { "content-type": "application/json" },
			body: JSON.stringify({ error: (error as Error).message }),
		};
	}
}

interface AwsCreds {
	accessKeyId: string;
	secretAccessKey: string;
}

interface Project {
	accessKey: string;
	secretKey: string;
	projectName: string;
	zipball: Uint8Array;
}

export async function pushToS3(project: Project): Promise<void> {
	const creds: AwsCreds = {
		accessKeyId: project.accessKey,
		secretAccessKey: project.secretKey,
	};

	const region = "us-west-2";
	const client = await createS3Client(creds, region);
	const bucketName = project.projectName;

	//await createBucket(client, bucketName, region);

	const key = `Byteport-${bucketName}-${uuidv4()}`;
	//await uploadToS3(client, bucketName, key, project.zipball);
}

export async function createS3Client(
	creds: AwsCreds,
	region: string
): Promise<S3Client> {
	return new S3Client({
		region: region,
		credentials: {
			accessKeyId: creds.accessKeyId,
			secretAccessKey: creds.secretAccessKey,
		},
	});
}

export async function createBucket(
	client: S3Client,
	bucketName: string,
	region: string
): Promise<void> {
	const input: CreateBucketCommandInput = {
		Bucket: bucketName,
		CreateBucketConfiguration: {
			LocationConstraint: region as BucketLocationConstraint,
		},
	};

	try {
		await client.send(new CreateBucketCommand(input));
	} catch (error) {
		throw new Error(`Failed to create bucket: ${error}`);
	}
}

export async function uploadToS3(
	client: S3Client,
	bucketName: string,
	key: string,
	body: Uint8Array
): Promise<void> {
	try {
		// Upload the object
		const uploadResponse = await client.send(
			new PutObjectCommand({
				Bucket: bucketName,
				Key: key,
				Body: body,
			})
		);

		console.log(
			"Upload success. Version:",
			uploadResponse.VersionId ?? "missing version ID"
		);

		// Retrieve the uploaded object
		const getResponse = await client.send(
			new GetObjectCommand({
				Bucket: bucketName,
				Key: key,
			})
		);

		console.log("etag:", getResponse.ETag ?? "(missing)");
		console.log("version:", getResponse.VersionId ?? "(missing)");
	} catch (error) {
		throw new Error(`Failed to upload to S3: ${error}`);
	}
}
