import { version } from "../../package.json" with { type: "json" };
import type { APIRoute } from "astro";

export const prerender = true;

export const GET: APIRoute = () =>
  new Response(JSON.stringify({ status: "ok", version }), {
    status: 200,
    headers: {
      "content-type": "application/json",
      "cache-control": "public, max-age=0, must-revalidate",
    },
  });
