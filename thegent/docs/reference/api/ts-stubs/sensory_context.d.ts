// Auto-generated TypeScript declarations for sensory_context
// Source: generate-api-docs.py

export declare class AudioFeatures {
}

export declare class SensoryContextBridge {
  constructor();
  process_audio(audio_data: Uint8Array, format: string, language: any): void;
  process_video(video_data: Uint8Array, format: string, extract_frames: boolean, frame_interval: number): void;
  register_audio_processor(name: string, processor: any): void;
  register_video_processor(name: string, processor: any): void;
}

export declare class VideoFeatures {
}

export declare function process_audio(audio_data: Uint8Array, format: string, language: any): void;
export declare function process_video(video_data: Uint8Array, format: string, extract_frames: boolean, frame_interval: number): void;
export declare function register_audio_processor(name: string, processor: any): void;
export declare function register_video_processor(name: string, processor: any): void;
