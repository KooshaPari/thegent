import { TextEncoder } from "util";
import { createHmac } from "crypto";

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

export async function handler(req: Request): Promise<Response> {
	try {
		const { accessKey, secretKey, projectName, zipball }: Project =
			await req.json();

		const bucketName = projectName.toLowerCase();
		const region = "us-west-2";
		const creds: AwsCreds = {
			accessKeyId: accessKey,
			secretAccessKey: secretKey,
		};

		// Create bucket
		const createBucketResponse = await createBucket(bucketName, region, creds);

		// Upload zipball
		const objectKey = `${projectName}.zip`;
		const uploadResponse = await putObject(
			bucketName,
			objectKey,
			zipball,
			region,
			creds
		);

		return new Response(JSON.stringify({ status: "success" }), {
			status: 200,
			headers: { "Content-Type": "application/json" },
		});
	} catch (error) {
		console.error("Error:", error);
		return new Response(JSON.stringify({ error: error.message }), {
			status: 500,
			headers: { "Content-Type": "application/json" },
		});
	}
}

async function createBucket(
	bucket: string,
	region: string,
	creds: AwsCreds
): Promise<Response> {
	const method = "PUT";
	const service = "s3";
	const host = `${bucket}.s3.${region}.amazonaws.com`;
	const url = `https://${host}/`;
	const headers = await signRequest({
		method,
		url,
		headers: {},
		body: "",
		service,
		region,
		creds,
	});
	const response = await fetch(url, { method, headers });
	if (!response.ok && response.status !== 409) {
		// 409: BucketAlreadyExists
		throw new Error(`Failed to create bucket: ${response.statusText}`);
	}
	return response;
}

async function putObject(
	bucket: string,
	key: string,
	body: Uint8Array,
	region: string,
	creds: AwsCreds
): Promise<Response> {
	const method = "PUT";
	const service = "s3";
	const host = `${bucket}.s3.${region}.amazonaws.com`;
	const url = `https://${host}/${encodeURIComponent(key)}`;
	const headers = await signRequest({
		method,
		url,
		headers: { "Content-Type": "application/octet-stream" },
		body,
		service,
		region,
		creds,
	});
	const response = await fetch(url, { method, headers, body });
	if (!response.ok) {
		throw new Error(`Failed to upload object: ${response.statusText}`);
	}
	return response;
}

/**
 * AWS Signature Version 4 signing
 */
async function signRequest({
	method,
	url,
	headers,
	body,
	service,
	region,
	creds,
}: {
	method: string;
	url: string;
	headers: Record<string, string>;
	body: Uint8Array | string;
	service: string;
	region: string;
	creds: AwsCreds;
}): Promise<Headers> {
	const { accessKeyId, secretAccessKey } = creds;
	const now = new Date();
	const amzDate = now.toISOString().replace(/[:\-]|\.\d{3}/g, "");
	const dateStamp = amzDate.substring(0, 8);

	const uri = new URL(url);
	const host = uri.hostname;
	const canonicalUri = uri.pathname;
	const canonicalQuerystring = uri.searchParams.toString();

	let canonicalHeaders = `host:${host}\n`;
	const signedHeaders = "host";

	let payloadHash = "";
	if (body && typeof body !== "string") {
		payloadHash = await sha256Hex(body);
	} else {
		payloadHash = await sha256Hex(new TextEncoder().encode(body || ""));
	}

	const canonicalRequest = [
		method,
		canonicalUri,
		canonicalQuerystring,
		canonicalHeaders,
		signedHeaders,
		payloadHash,
	].join("\n");

	const algorithm = "AWS4-HMAC-SHA256";
	const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;

	const stringToSign = [
		algorithm,
		amzDate,
		credentialScope,
		await sha256Hex(new TextEncoder().encode(canonicalRequest)),
	].join("\n");

	const signingKey = await getSignatureKey(
		secretAccessKey,
		dateStamp,
		region,
		service
	);
	const signature = await hmacHex(signingKey, stringToSign);

	const authorizationHeader = `${algorithm} Credential=${accessKeyId}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;

	const signedHeadersMap = new Headers(headers);
	signedHeadersMap.set("Authorization", authorizationHeader);
	signedHeadersMap.set("x-amz-date", amzDate);
	return signedHeadersMap;
}

async function sha256Hex(message: Uint8Array): Promise<string> {
	const hashBuffer = await crypto.subtle.digest("SHA-256", message);
	return Array.from(new Uint8Array(hashBuffer))
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
}

async function hmac(key: Uint8Array, data: string): Promise<ArrayBuffer> {
	const cryptoKey = await crypto.subtle.importKey(
		"raw",
		key,
		{ name: "HMAC", hash: "SHA-256" },
		false,
		["sign"]
	);
	return await crypto.subtle.sign(
		"HMAC",
		cryptoKey,
		new TextEncoder().encode(data)
	);
}

async function hmacHex(key: Uint8Array, data: string): Promise<string> {
	const sig = await hmac(key, data);
	return Array.from(new Uint8Array(sig))
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
}

async function getSignatureKey(
	key: string,
	dateStamp: string,
	regionName: string,
	serviceName: string
): Promise<Uint8Array> {
	const kDate = await hmac(new TextEncoder().encode("AWS4" + key), dateStamp);
	const kRegion = await hmac(new Uint8Array(kDate), regionName);
	const kService = await hmac(new Uint8Array(kRegion), serviceName);
	const kSigning = await hmac(new Uint8Array(kService), "aws4_request");
	return new Uint8Array(kSigning);
}
