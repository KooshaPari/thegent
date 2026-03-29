// Auto-generated usage examples for fast_http_client
// Source: generate-api-docs.py

import { FastHTTPClient, backend, close, get, get_http_client, http_get, http_post, http_request, post, request } from "./fast_http_client";

// Create a FastHTTPClient instance
const fasthttpclient = new FastHTTPClient(undefined as unknown as any);
fasthttpclient.backend();
fasthttpclient.close();
fasthttpclient.get("example_url");
fasthttpclient.post("example_url");
fasthttpclient.request("example_method", "example_url");

// Call backend
backend(undefined as unknown as any);
// Call close
close(undefined as unknown as any);
// Call get
get(undefined as unknown as any, "example_url");
// Call get_http_client
get_http_client(undefined as unknown as any);
// Call http_get
http_get("example_url");
// Call http_post
http_post("example_url");
// Call http_request
http_request("example_method", "example_url");
// Call post
post(undefined as unknown as any, "example_url");
// Call request
request(undefined as unknown as any, "example_method", "example_url");
