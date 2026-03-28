// index.ts

// Define the interfaces
export interface AwsCreds {
	accessKeyId: string;
	secretAccessKey: string;
}

export interface Project {
	accessKey: string;
	secretKey: string;
	projectName: string;
	zipball: Uint8Array; // Ensure this is a Uint8Array
}

// AWS Signature Version 4 signing functions
export async function sha256(message: Uint8Array | string): Promise<string> {
  const encoder = new TextEncoder();
  const data = typeof message === "string" ? encoder.encode(message) : message;
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
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

export async function signRequest(
  method: string,
  url: string,
  region: string,
  service: string,
  requestPayload: Uint8Array | string,
  accessKeyId: string,
  secretAccessKey: string,
  additionalHeaders: Record<string, string>
): Promise<Record<string, string>> {
  console.log("Signing request with payload:", requestPayload);
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
  console.log("Getting payload hash");
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
  console.log("Getting signing key");
  const signingKey = await getSignatureKey(
    secretAccessKey,
    dateStamp,
    region,
    service
  );
  console.log("Getting signature");
  const signatureArrayBuffer = await hmac(signingKey, stringToSign);
  const signature = Array.from(new Uint8Array(signatureArrayBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

  const authorizationHeader = `AWS4-HMAC-SHA256 Credential=${accessKeyId}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;
  console.log("Setting Header");

  const headers: Record<string, string> = {
    ...additionalHeaders,
    Authorization: authorizationHeader,
    "x-amz-date": amzDate,
    host: host,
  };

  