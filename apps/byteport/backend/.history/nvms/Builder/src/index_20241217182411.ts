import { ResponseBuilder } from "@fermyon/spin-sdk";
import { FetchHttpHandler } from "@aws-sdk/fetch-http-handler";

import {
	S3Client,
	CreateBucketCommand,
	PutObjectCommand,
	GetObjectCommand,
	waitUntilBucketExists,
	CreateBucketCommandInput,
} from "@aws-sdk/client-s3";
import { v4 as uuidv4 } from "uuid";
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

export async function handler(req: Request, res: ResponseBuilder) {
	console.log("Request To Build: ", req);
	try {
		// Parse the request body as JSON
		const bodyText = await req.text();
		const project: Project = JSON.parse(bodyText);
		console.log("Pushing project to S3:");
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
			body: JSON.stringify({
				error: error instanceof Error ? error.message : "Unknown error",
				stack: error instanceof Error ? error.stack : undefined,
			}),
		};
	}
}

export async function pushToS3(project: Project): Promise<void> {
	const creds: AwsCreds = {
		accessKeyId: project.accessKey,
		secretAccessKey: project.secretKey,
	};
	var client" S3Client;
	console.log("Creating client");
	const region = "us-west-2";
	try {
		let client = await createS3Client(creds, region);
	} catch (error) {
		throw new Error(`Failed to Create Client: ${error}`);
	}
	const bucketName = project.projectName;
	try {
		console.log("Creating bucket");
		await createBucket(client, bucketName, region);
	} catch (error) {
		throw new Error(`Failed to create bucket: ${error}`);
	}
	try {
		console.log("Uploading to S3");
		const key = `Byteport-${bucketName}-${uuidv4()}`;
		//await uploadToS3(client, bucketName, key, project.zipball);
	} catch (error) {
		throw new Error(`Failed to push to S3: ${error}`);
	}
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
		requestHandler: new FetchHttpHandler(),
	});
}

export async function createBucket(
	client: S3Client,
	bucketName: string,
	region: string
): Promise<void> {
	const input: CreateBucketCommandInput = {
		Bucket: bucketName,
	};

	console.log("Creating bucket with params:", input);
	try {
		const command = new CreateBucketCommand(input);
		const location = await client.send(command);
		await waitUntilBucketExists(
			{ client, maxWaitTime: 120 },
			{ Bucket: bucketName }
		);
		console.log(`Bucket created with location ${location}`);
	} catch (error) {
		console.error("Error creating bucket:", error);
		throw new Error(`Failed to create bucket: ${error}`);
	}
}
/*
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
*/
