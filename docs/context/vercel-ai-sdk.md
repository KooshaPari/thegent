# Vercel AI SDK Context

> Definitive reference for the Vercel AI SDK — TypeScript toolkit for building AI-powered applications across providers.
> Sources: ai-sdk.dev/docs, vercel.com/blog/ai-sdk-6, github.com/vercel/ai (fetched 2026-02-20).
> **Version covered: AI SDK 6.x (latest: 6.0.94 as of 2026-02-20)**

---

## What is Vercel AI SDK

The **AI SDK** (formerly "Vercel AI SDK") is an open-source TypeScript/JavaScript toolkit that provides a unified API for integrating AI models across providers (OpenAI, Anthropic, Google, xAI, etc.). It abstracts provider-specific differences so application code targets one stable interface.

Key capabilities:
- **Provider-agnostic**: Swap models by changing one `model` argument
- **Streaming**: First-class SSE streaming with backpressure and React Suspense integration
- **Structured output**: Generate typed JSON objects, arrays, and choices from any provider
- **Tool calling**: Declare tools with Zod schemas; SDK handles round-trips automatically
- **Agent patterns**: Multi-step tool loops with `maxSteps`; `ToolLoopAgent` for production agents
- **React/Next.js hooks**: `useChat`, `useCompletion`, `useObject` for UI state management
- **MCP support**: Native Model Context Protocol client with HTTP transport + OAuth

**Note on thegent/trace**: trace's web frontend uses `@trpc/client` for API calls, not AI SDK directly. thegent uses AI SDK patterns in proxy/routing layers for provider-agnostic model access.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Provider** | A model source adapter (e.g., `@ai-sdk/openai`, `@ai-sdk/anthropic`) |
| **LanguageModel** | Provider-created model instance passed to core functions |
| **`generateText`** | Non-streaming text generation for automation tasks |
| **`streamText`** | Streaming text generation for real-time UI |
| **`generateObject`** | Structured JSON output with schema validation |
| **Tool** | Defined with `tool()` — schema + execute function |
| **Step** | One round of model → tool calls → tool results in a multi-step loop |
| **`maxSteps`** | Max number of steps in a tool call loop |
| **ToolLoopAgent** | New in v6: production agent with automatic tool loops |
| **`useChat`** | React hook for chat UI state management |

---

## Installation

```bash
# Core SDK
npm install ai
bun add ai

# Provider packages (install per provider used)
npm install @ai-sdk/openai         # OpenAI + compatible APIs
npm install @ai-sdk/anthropic      # Anthropic Claude
npm install @ai-sdk/google         # Google Gemini
npm install @ai-sdk/xai            # xAI Grok
npm install @ai-sdk/cohere         # Cohere
npm install @ai-sdk/azure          # Azure OpenAI
npm install @ai-sdk/amazon-bedrock # Amazon Bedrock
npm install @ai-sdk/vercel         # Vercel AI Gateway (all providers)
npm install @ai-sdk/openai-compatible  # OpenRouter, LiteLLM, etc.

# Migration codemod (v5 to v6)
npx @ai-sdk/codemod upgrade v6

# DevTools viewer
npx @ai-sdk/devtools               # Opens viewer at localhost:4983
```

**Current versions (2026-02-20):**

| Package | Version |
|---------|---------|
| `ai` | `6.0.94` |
| `@ai-sdk/vercel` | `2.0.32` |
| `@ai-sdk/openai` | `~1.x` |
| `@ai-sdk/anthropic` | `~1.x` |

---

## Core: `generateText`

Generates text for non-interactive, automation use cases.

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

const result = await generateText({
    model: openai('gpt-4o'),
    prompt: 'Summarize the following: ...',
    system: 'You are a helpful assistant.',
    maxOutputTokens: 1000,
    temperature: 0.7,
    maxRetries: 2,
    tools: { myTool },
    toolChoice: 'auto',    // 'auto' | 'none' | 'required' | {type, toolName}
    maxSteps: 5,           // Max tool call rounds
});

// Return fields
result.text             // string: generated text
result.toolCalls        // Array of tool invocations
result.toolResults      // Array of tool results
result.finishReason     // 'stop' | 'length' | 'tool-calls' | 'content-filter' | 'error'
result.usage            // {inputTokens, outputTokens, totalTokens}
result.totalUsage       // Aggregate across all steps
result.steps            // Array of GenerateTextStep — each step in multi-step loop
result.reasoning        // Array of reasoning outputs (models that support it)
result.response         // {id, modelId, timestamp, headers}
```

**Full parameter list:**

```typescript
await generateText({
    model,
    prompt,              // string | MessagePart[]
    messages,            // ModelMessage[]  (use prompt OR messages, not both)
    system,              // string | SystemMessage[]
    tools,               // Record<string, Tool>
    toolChoice,          // 'auto' | 'none' | 'required' | {type, toolName}
    activeTools,         // string[] — limit which tools are active
    output,              // Output.object({schema}), Output.array(), Output.choice(), Output.json()
    maxSteps,
    prepareStep,         // (step) => Promise<StepSettings>
    stopWhen,            // Condition to stop multi-step generation
    temperature,
    topP, topK,
    presencePenalty, frequencyPenalty,
    maxOutputTokens,
    stopSequences,       // string[]
    seed,
    maxRetries,          // Default: 2
    timeout,             // number | {totalMs, stepMs}
    abortSignal,         // AbortSignal
    providerOptions,     // Provider-specific settings
    headers,             // Custom HTTP headers
    experimental_context, // Custom context passed through execution
});
```

---

## Core: `streamText`

Streaming text generation. Returns a `StreamTextResult` with async iterators.

```typescript
import { streamText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';

const result = streamText({
    model: anthropic('claude-sonnet-4.5'),
    prompt: 'Tell me a story',
});

// Consume text stream
for await (const chunk of result.textStream) {
    process.stdout.write(chunk);
}

// In Next.js App Router API route
export async function POST(req: Request) {
    const { messages } = await req.json();
    const result = streamText({
        model: openai('gpt-4o'),
        messages,
    });
    return result.toDataStreamResponse();   // Response with SSE format
}
```

**Key `streamText` result properties:**

```typescript
result.textStream               // AsyncIterable<string>
result.fullStream               // AsyncIterable<TextStreamPart> (includes tool calls)
result.text                     // Promise<string> — complete text when done
result.finishReason             // Promise<FinishReason>
result.usage                    // Promise<Usage>
result.toDataStreamResponse()   // Next.js Response object (SSE)
result.pipeDataStreamToResponse(res)   // Node.js stream
result.toTextStreamResponse()   // Plain text response
```

---

## Core: `generateObject`

Generate structured JSON output with schema validation.

```typescript
import { generateObject } from 'ai';
import { z } from 'zod';

const { object } = await generateObject({
    model: openai('gpt-4o'),
    schema: z.object({
        title: z.string(),
        priority: z.enum(['low', 'medium', 'high']),
        tags: z.array(z.string()),
    }),
    prompt: 'Create a task for fixing the login bug',
});
// object: { title: string; priority: 'low'|'medium'|'high'; tags: string[] }
```

**Output modes (v6):**

```typescript
import { Output } from 'ai';

await generateText({ ..., output: Output.object({ schema: z.object({...}) }) });
await generateText({ ..., output: Output.array({ schema: z.object({...}) }) });
await generateText({ ..., output: Output.choice(['accept', 'reject', 'defer']) });
await generateText({ ..., output: Output.json() });
```

**`streamObject` for streaming structured output:**

```typescript
import { streamObject } from 'ai';

const result = streamObject({
    model: openai('gpt-4o'),
    schema: z.object({ summary: z.string(), points: z.array(z.string()) }),
    prompt: 'Summarize this document: ...',
});

for await (const partial of result.partialObjectStream) {
    console.log(partial);  // Partial updates as stream arrives
}
const finalObject = await result.object;
```

---

## Tools

```typescript
import { tool, generateText } from 'ai';
import { z } from 'zod';

const getWeather = tool({
    description: 'Get the weather for a location',
    parameters: z.object({
        location: z.string().describe('City name'),
        units: z.enum(['celsius', 'fahrenheit']).default('celsius'),
    }),
    execute: async ({ location, units }) => {
        const weather = await fetchWeatherAPI(location, units);
        return { temperature: weather.temp, condition: weather.cond };
    },
    // v6 features:
    needsApproval: false,        // boolean | async fn — human-in-the-loop
    strict: true,                // Strict JSON Schema validation
    inputExamples: [             // Clarifying examples for the model
        { location: 'San Francisco', units: 'fahrenheit' }
    ],
});

const result = await generateText({
    model: openai('gpt-4o'),
    tools: { getWeather },
    maxSteps: 3,
    prompt: 'What is the weather in SF?',
});
```

**Tool execution approval (human-in-the-loop, v6):**

```typescript
const dangerousTool = tool({
    parameters: z.object({ target: z.string() }),
    needsApproval: true,   // Pause execution; human must call addToolOutput()
    execute: async ({ target }) => {
        return performOperation(target);
    },
});
```

**`toModelOutput` — control what the model sees from tool result:**

```typescript
const richTool = tool({
    parameters: z.object({ query: z.string() }),
    execute: async ({ query }) => {
        const result = await expensiveQuery(query);
        return result;    // Full result stored in toolResults
    },
    toModelOutput: (result) => ({
        text: `Found ${result.count} items`,  // Only summary passed to model context
    }),
});
```

---

## Agents: `ToolLoopAgent` (v6)

Production-ready agent with automatic tool execution loops.

```typescript
import { ToolLoopAgent } from 'ai';
import { openai } from '@ai-sdk/openai';

const agent = new ToolLoopAgent({
    model: openai('gpt-4o'),
    instructions: 'You are a helpful assistant. Use tools to answer questions.',
    tools: { getWeather, searchDocs },
    maxSteps: 10,
});

const result = await agent.generate({
    prompt: 'What is the weather in Tokyo today?',
});
console.log(result.text);

// Streaming
const stream = agent.stream({ prompt: 'Explain...' });
for await (const chunk of stream.textStream) {
    process.stdout.write(chunk);
}
```

**Dynamic call options (v6):**

```typescript
const agent = new ToolLoopAgent({
    model: openai('gpt-4o'),
    callOptionsSchema: z.object({ userId: z.string() }),
    prepareCall: async ({ userId }) => ({
        system: `User ID: ${userId}. Provide personalized help.`,
    }),
    tools: { getProfile },
});

const result = await agent.generate({
    prompt: 'What are my preferences?',
    callOptions: { userId: 'user_123' },
});
```

**`maxSteps` without ToolLoopAgent:**

```typescript
const result = await generateText({
    model: openai('gpt-4o'),
    tools: { searchWeb, readFile, writeCode },
    maxSteps: 10,
    prompt: 'Research and implement a sorting algorithm',
});
// SDK loops: model → tool calls → tool results → model → ... until maxSteps or done
```

---

## Providers

### OpenAI

```typescript
import { openai } from '@ai-sdk/openai';

openai('gpt-4o')
openai('gpt-4o-mini')
openai('o1')
openai('o3-mini')
openai.image('dall-e-3')
openai.embedding('text-embedding-3-small')
```

### Anthropic

```typescript
import { anthropic } from '@ai-sdk/anthropic';

anthropic('claude-opus-4-6')
anthropic('claude-sonnet-4.5')
anthropic('claude-haiku-4.5')

// Provider-specific tools (v6)
import { anthropicTools } from '@ai-sdk/anthropic';
const tools = {
    computer: anthropicTools.computer_20250124(),
    bash: anthropicTools.bash_20250124(),
    textEditor: anthropicTools.textEditor_20250124(),
};
```

### Google

```typescript
import { google } from '@ai-sdk/google';

google('gemini-2.0-flash')
google('gemini-2.0-pro')
google('gemini-2.0-flash-thinking-exp')   // Reasoning model
```

### xAI

```typescript
import { xai } from '@ai-sdk/xai';

xai('grok-3')
xai('grok-3-mini')
```

### OpenAI-Compatible (OpenRouter, LiteLLM)

```typescript
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

// OpenRouter
const openrouter = createOpenAICompatible({
    name: 'openrouter',
    baseURL: 'https://openrouter.ai/api/v1',
    headers: {
        'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'HTTP-Referer': 'https://example.com',
    },
});
const model = openrouter('anthropic/claude-sonnet-4.5');

// LiteLLM proxy
const litellm = createOpenAICompatible({
    name: 'litellm',
    baseURL: 'http://localhost:4000/v1',
    headers: { 'Authorization': `Bearer ${process.env.LITELLM_API_KEY}` },
});
```

### Vercel AI Gateway

```typescript
import { createVercel } from '@ai-sdk/vercel';

const vercel = createVercel({ apiKey: process.env.AI_GATEWAY_API_KEY });
const model = vercel('anthropic/claude-sonnet-4.5');
```

---

## React Hooks (AI SDK UI)

### `useChat`

```typescript
'use client';
import { useChat } from 'ai/react';

export function ChatComponent() {
    const {
        messages,       // Message[]
        id,             // Chat ID
        status,         // 'submitted' | 'streaming' | 'ready' | 'error'
        error,
        sendMessage,    // Submit new message
        regenerate,     // Recreate last response
        stop,           // Abort streaming
        setMessages,    // Direct state setter
        addToolOutput,  // For tool approval flows
    } = useChat({
        transport: '/api/chat',
        messages: initialMessages,
        onFinish: (message) => console.log('Done:', message),
        onError: (error) => console.error(error),
        onToolCall: async ({ toolCall }) => {
            // Client-side tool handling
            if (toolCall.toolName === 'getLocation') {
                return { lat: 37.7749, lng: -122.4194 };
            }
        },
    });

    return (
        <div>
            {messages.map(m => (
                <div key={m.id}>{m.role}: {m.content}</div>
            ))}
            <button onClick={() => sendMessage('Hello!')}>Send</button>
            <button onClick={stop}>Stop</button>
        </div>
    );
}
```

### `useCompletion`

```typescript
import { useCompletion } from 'ai/react';

const { completion, complete, isLoading } = useCompletion({
    api: '/api/complete',
    onFinish: (text) => console.log('Final:', text),
});

await complete('Summarize this: ...');
// completion updates in real-time as stream arrives
```

### `useObject`

```typescript
import { useObject } from 'ai/react';
import { z } from 'zod';

const TaskSchema = z.object({
    title: z.string(),
    priority: z.enum(['low', 'medium', 'high']),
    steps: z.array(z.string()),
});

const { object, submit, isLoading } = useObject({
    api: '/api/generate-task',
    schema: TaskSchema,
});

await submit('Create a task for fixing the login bug');
// object updates in real-time as stream arrives
```

---

## Embeddings

```typescript
import { embed, embedMany } from 'ai';
import { openai } from '@ai-sdk/openai';

const { embedding } = await embed({
    model: openai.embedding('text-embedding-3-small'),
    value: 'Text to embed',
});
// embedding: number[]  (1536 dimensions)

const { embeddings } = await embedMany({
    model: openai.embedding('text-embedding-3-small'),
    values: ['Text 1', 'Text 2', 'Text 3'],
});
// embeddings: number[][]
```

---

## Image Generation

```typescript
import { generateImage } from 'ai';
import { openai } from '@ai-sdk/openai';

const { image } = await generateImage({
    model: openai.image('dall-e-3'),
    prompt: 'A futuristic city skyline',
    size: '1024x1024',
    // v6: reference images for editing
    images: [existingImageAsBase64OrURL],
});

// image.base64     → base64 string
// image.uint8Array → Uint8Array
```

---

## Middleware: `wrapLanguageModel`

Inject logging, caching, or other behavior around model calls.

```typescript
import { wrapLanguageModel } from 'ai';

const instrumentedModel = wrapLanguageModel({
    model: openai('gpt-4o'),
    middleware: {
        wrapGenerate: async ({ doGenerate, params }) => {
            console.log('Calling model...');
            const result = await doGenerate();
            console.log('Output:', result.text);
            return result;
        },
    },
});
```

**DevTools middleware (v6):**

```typescript
import { devToolsMiddleware } from '@ai-sdk/devtools';

const model = wrapLanguageModel({
    model: openai('gpt-4o'),
    middleware: devToolsMiddleware(),  // Viewer at localhost:4983
});
```

---

## Reranking (v6)

```typescript
import { rerank } from 'ai';
import { cohere } from '@ai-sdk/cohere';

const { rerankedDocuments } = await rerank({
    model: cohere.rerank('rerank-v3.5'),
    query: 'What is the weather like in London?',
    documents: [
        'London has mild weather year-round.',
        'Paris is the capital of France.',
        'The UK experiences frequent rainfall.',
    ],
    topK: 2,
});
```

---

## MCP Support (Native Client)

```typescript
import { experimental_createMcpClient } from 'ai';

const mcpClient = await experimental_createMcpClient({
    transport: {
        type: 'sse',
        url: 'http://localhost:3847/sse',
    },
});

const mcpTools = await mcpClient.tools();

const result = await generateText({
    model: openai('gpt-4o'),
    tools: { ...mcpTools },
    prompt: 'Run thegent ps',
});

// HTTP transport with OAuth
const securedClient = await experimental_createMcpClient({
    transport: {
        type: 'http',
        url: 'https://mcp.example.com',
        headers: { 'Authorization': `Bearer ${token}` },
    },
});
```

---

## Error Handling

```typescript
import { generateText, APICallError, RetryError } from 'ai';

try {
    const result = await generateText({ model: openai('gpt-4o'), prompt: 'Hello' });
} catch (error) {
    if (APICallError.isInstance(error)) {
        console.error('API error:', error.statusCode, error.message);
        console.error('Response body:', error.responseBody);
    } else if (RetryError.isInstance(error)) {
        console.error('Max retries exceeded:', error.errors);
    } else {
        throw error;
    }
}
```

---

## Telemetry

```typescript
const result = await generateText({
    model: openai('gpt-4o'),
    prompt: 'Hello',
    experimental_telemetry: {
        isEnabled: true,
        functionId: 'my-generation',
        metadata: { userId: 'user_123', requestId: 'req_456' },
    },
});
// Outputs OpenTelemetry spans to configured exporters
```

---

## 2026 Features (AI SDK 6.x as of 2026-02-20)

| Feature | Status | Notes |
|---------|--------|-------|
| `ToolLoopAgent` | Stable (v6) | Production agent with tool loops |
| Tool execution approval (`needsApproval`) | Stable (v6) | Human-in-the-loop |
| `Output.*` structured output | Stable (v6) | `Output.object/array/choice/json` |
| Computer use (Anthropic) | Stable | via `anthropicTools.computer_20250124()` |
| Reasoning model support | Stable | `reasoning` field in result |
| MCP native client | Experimental | `experimental_createMcpClient` |
| Image editing | Stable (v6) | `images` param in `generateImage` |
| Reranking | Stable (v6) | `rerank()` function |
| DevTools | Stable (v6) | `devToolsMiddleware()` |
| LangChain adapter rewrite | Stable (v6) | `@ai-sdk/langchain` v2 |
| StandardSchema V1 | Stable (v6) | Arktype, Valibot as tool schemas |

---

## thegent / trace Integration

- **trace web frontend**: uses `@trpc/client` for API calls — AI SDK is server-side only in this stack
- **thegent proxy layer**: AI SDK patterns used for provider-agnostic model access
- **Common provider**: OpenRouter (`@ai-sdk/openai-compatible`) as unified gateway
- **MCP integration**: `experimental_createMcpClient` connects to thegent MCP server on port 3847

---

## Known Issues / Gotchas

1. **`sdk.vercel.ai` deprecated**: Redirects to `ai-sdk.dev`. Update bookmarks and configs.
2. **v5 to v6 migration**: Run `npx @ai-sdk/codemod upgrade v6` — handles most breaking changes automatically.
3. **`maxSteps` required for tools**: Without `maxSteps`, tool calls stop after first round; no automatic continuation.
4. **Streaming + structured output**: `streamObject` is separate from `streamText`; cannot mix in a single call.
5. **Provider options**: Features like prompt caching require `providerOptions` — check provider-specific docs.
6. **`useChat` transport**: Default endpoint is `/api/chat` — must create matching API route.
7. **Tool approval + `useChat`**: When `needsApproval: true`, call `addToolOutput()` in the UI to resume after human approval.

---

## Sources & References

- **Official Docs**: https://ai-sdk.dev/docs (fetched 2026-02-20)
- **AI SDK 6 Announcement**: https://vercel.com/blog/ai-sdk-6 (fetched 2026-02-20)
- **GitHub**: https://github.com/vercel/ai (fetched 2026-02-20)
- **generateText Reference**: https://ai-sdk.dev/docs/reference/ai-sdk-core/generate-text (fetched 2026-02-20)
- **useChat Reference**: https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-chat (fetched 2026-02-20)
- **npm `ai` package**: https://www.npmjs.com/package/ai (v6.0.94, fetched 2026-02-20)
- **Last Verified**: 2026-02-20

See also: `docs/context/openrouter.md`, `docs/context/vercel-ai-gateway.md`

---

## Quick Reference

| Item | Value |
|------|-------|
| Install | `npm install ai @ai-sdk/openai` |
| Latest version | `ai@6.0.94` |
| Docs URL | `https://ai-sdk.dev/docs` |
| Migration codemod | `npx @ai-sdk/codemod upgrade v6` |
| DevTools | `npx @ai-sdk/devtools` — viewer at `localhost:4983` |

### Core Function Cheat Sheet

```typescript
// Text generation (non-streaming)
const { text } = await generateText({ model, prompt, tools, maxSteps });

// Streaming text
const stream = streamText({ model, messages });
for await (const chunk of stream.textStream) { ... }
return stream.toDataStreamResponse();   // For Next.js

// Structured output
const { object } = await generateObject({ model, schema, prompt });
const stream = streamObject({ model, schema, prompt });

// Embeddings
const { embedding } = await embed({ model: openai.embedding('text-embedding-3-small'), value });

// Image generation
const { image } = await generateImage({ model: openai.image('dall-e-3'), prompt });

// Agents (v6)
const agent = new ToolLoopAgent({ model, instructions, tools });
const result = await agent.generate({ prompt });

// Reranking (v6)
const { rerankedDocuments } = await rerank({ model: cohere.rerank('rerank-v3.5'), query, documents });
```

### Provider Quick Lookup

| Provider | Import | Model string |
|----------|--------|-------------|
| OpenAI | `@ai-sdk/openai` | `'gpt-4o'`, `'gpt-4o-mini'`, `'o1'` |
| Anthropic | `@ai-sdk/anthropic` | `'claude-opus-4-6'`, `'claude-sonnet-4.5'` |
| Google | `@ai-sdk/google` | `'gemini-2.0-flash'`, `'gemini-2.0-pro'` |
| xAI | `@ai-sdk/xai` | `'grok-3'`, `'grok-3-mini'` |
| OpenRouter | `@ai-sdk/openai-compatible` | `createOpenAICompatible({baseURL: 'https://openrouter.ai/api/v1', ...})` |
| Vercel Gateway | `@ai-sdk/vercel` | `createVercel({apiKey: ...})` |
