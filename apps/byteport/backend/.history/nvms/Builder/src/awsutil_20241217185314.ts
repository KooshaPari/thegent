// index.ts

// Define the interfaces
interface AwsCreds {
	accessKeyId: string;
	secretAccessKey: string;
}

interface Project {
	accessKey: string;
	secretKey: string;
	projectName: string;
	zipball: Uint8Array; // Ensure this is a Uint8Array
}

// AWS Signature Version 4 signing functions
async function sha256(message: Uint8Array | string): Promise<string> {
	const encoder = new TextEncoder();
	const data = typeof message === "string" ? encoder.encode(message) : message;
	const hashBuffer = await crypto.subtle.digest("SHA-256", data);
	const hashArray = Array.from(new Uint8Array(hashBuffer));
	const hashHex = hashArray
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
	return hashHex;
}

async function hmac(
	key: ArrayBuffer | Uint8Array,
	data: string | Uint8Array
): Promise<ArrayBuffer> {
	const encoder = new TextEncoder();
	const cryptoKey = await crypto.subtle.importKey(
		"raw",
		key instanceof Uint8Array ? key : new Uint8Array(key),
		{ name: "HMAC", hash: "SHA-256" },
		false,
		["sign"]
	);
	const dataArray = typeof data === "string" ? encoder.encode(data) : data;
	const signature = await crypto.subtle.sign("HMAC", cryptoKey, dataArray);
	return signature;
}

async function getSignatureKey(
	key: string,
	dateStamp: string,
	regionName: string,
	serviceName: string
): Promise<ArrayBuffer> {
	const kDate = await hmac(new TextEncoder().encode("AWS4" + key), dateStamp);
	const kRegion = await hmac(kDate, regionName);
	const kService = await hmac(kRegion, serviceName);
	const kSigning = await hmac(kService, "aws4_request");
	return kSigning;
}

async function signRequest(
	method: string,
	url: string,
	region: string,
	service: string,
	requestPayload: Uint8Array | string,
	accessKeyId: string,
	secretAccessKey: string,
	additionalHeaders: Record<string, string>
): Promise<Headers> {
	const now = new Date();
	const amzDate = now.toISOString().replace(/[:-]|\.\d{3}/g, "");
	const dateStamp = amzDate.substring(0, 8);

	const urlObj = new URL(url);
	const host = urlObj.host;
	const canonicalUri = urlObj.pathname;
	const canonicalQuerystring = urlObj.searchParams.toString();

	const encodedHeaders: Record<string, string> = {
		"x-amz-date": amzDate,
		host: host,
		...additionalHeaders,
	};

	const sortedHeaderKeys = Object.keys(encodedHeaders).sort();
	const canonicalHeaders = sortedHeaderKeys
		.map((key) => `${key}:${encodedHeaders[key]}`)
		.join("\n");

	const signedHeaders = sortedHeaderKeys.join(";");

	const payloadHash = await sha256(requestPayload);

	const canonicalRequest = [
		method,
		canonicalUri,
		canonicalQuerystring,
		canonicalHeaders + "\n",
		signedHeaders,
		payloadHash,
	].join("\n");

	const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;
	const stringToSign = [
		"AWS4-HMAC-SHA256",
		amzDate,
		credentialScope,
		await sha256(canonicalRequest),
	].join("\n");

	const signingKey = await getSignatureKey(
		secretAccessKey,
		dateStamp,
		region,
		service
	);

	const signatureArrayBuffer = await hmac(signingKey, stringToSign);
	const signature = Array.from(new Uint8Array(signatureArrayBuffer))
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");

	const authorizationHeader = `AWS4-HMAC-SHA256 Credential=${accessKeyId}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;

	const headers = new Headers(additionalHeaders);
	headers.set("Authorization", authorizationHeader);
	headers.set("x-amz-date", amzDate);
	headers.set("host", host);

	return headers;
}

// Function to create an S3 bucket
async function createBucket(
	bucketName: string,
	region: string,
	creds: AwsCreds
): Promise<void> {
	const method = "PUT";
	const service = "s3";
	const url = `https://${bucketName}.s3.${region}.amazonaws.com/`;

	const headers = await signRequest(
		method,
		url,
		region,
		service,
		"",
		creds.accessKeyId,
		creds.secretAccessKey,
		{
			"x-amz-content-sha256": await sha256(""),
		}
	);

	const response = await fetch(url, {
		method,
		headers,
	});

	if (response.status !== 200 && response.status !== 409) {
		// 200 OK or 409 Conflict (bucket already exists)
		const errorText = await response.text();
		throw new Error(`Failed to create bucket: ${response.status} ${errorText}`);
	}
}

// Function to upload an object to S3
async function putObject(
	bucketName: string,
	objectKey: string,
	region: string,
	creds: AwsCreds,
	body: Uint8Array
): Promise<void> {
	const method = "PUT";
	const service = "s3";
	const url = `https://${bucketName}.s3.${region}.amazonaws.com/${encodeURIComponent(
		objectKey
	)}`;

	const headers = await signRequest(
		method,
		url,
		region,
		service,
		body,
		creds.accessKeyId,
		creds.secretAccessKey,
		{
			"Content-Type": "application/octet-stream",
			"x-amz-content-sha256": await sha256(body),
		}
	);

	const response = await fetch(url, {
		method,
		headers,
		body,
	});

	if (response.status !== 200) {
		const errorText = await response.text();
		throw new Error(`Failed to upload object: ${response.status} ${errorText}`);
	}
}

// Main handler function
export async function handler(req: Request): Promise<Response> {
	try {
		console.log("Received request:", req);

		const project: Project = await req.json();

		const { accessKey, secretKey, projectName, zipball } = project;

		const creds = {
			accessKeyId: accessKey,
			secretAccessKey: secretKey,
		};

		const region = "us-west-2";
		const bucketName = projectName.toLowerCase();
		const objectKey = `${projectName}.zip`;

		// Create bucket
		await createBucket(bucketName, region, creds);
		console.log(`Bucket ${bucketName} created or already exists.`);

		// Upload zipball
		await putObject(bucketName, objectKey, region, creds, zipball);
		console.log(`Object ${objectKey} uploaded to bucket ${bucketName}.`);

		return new Response(JSON.stringify({ status: "success" }), {
			status: 200,
			headers: { "Content-Type": "application/json" },
		});
	} catch (error) {
		console.error("Error:", error);
		return new Response(
			JSON.stringify({
				error: error instanceof Error ? error.message : String(error),
			}),
			{
				status: 500,
				headers: { "Content-Type": "application/json" },
			}
		);
	}
}
