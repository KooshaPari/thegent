// Auto-generated usage examples for sensory_context
// Source: generate-api-docs.py

import { AudioFeatures, SensoryContextBridge, VideoFeatures, process_audio, process_video, register_audio_processor, register_video_processor } from "./sensory_context";

// Create a AudioFeatures instance
const audiofeatures = new AudioFeatures();

// Create a SensoryContextBridge instance
const sensorycontextbridge = new SensoryContextBridge();
sensorycontextbridge.process_audio(undefined as unknown as Uint8Array, "example_format", undefined as unknown as any);
sensorycontextbridge.process_video(undefined as unknown as Uint8Array, "example_format", false, 0);
sensorycontextbridge.register_audio_processor("example_name", undefined as unknown as any);
sensorycontextbridge.register_video_processor("example_name", undefined as unknown as any);

// Create a VideoFeatures instance
const videofeatures = new VideoFeatures();

// Call process_audio
process_audio(undefined as unknown as any, undefined as unknown as Uint8Array, "example_format", undefined as unknown as any);
// Call process_video
process_video(undefined as unknown as any, undefined as unknown as Uint8Array, "example_format", false, 0);
// Call register_audio_processor
register_audio_processor(undefined as unknown as any, "example_name", undefined as unknown as any);
// Call register_video_processor
register_video_processor(undefined as unknown as any, "example_name", undefined as unknown as any);
