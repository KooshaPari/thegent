// Auto-generated TypeScript declarations for playwright_recorder
// Source: generate-api-docs.py

export declare class PlaywrightRecorder {
  constructor(config: any);
}

export declare class RecordingConfig extends BaseModel {
  model_post_init(__context: any): void;
  validate_browser(v: string): void;
}

export declare class RecordingResult {
  to_dict(): void;
  to_json(path: any): void;
}

export declare class ScreenshotOptions extends BaseModel {
}

export declare class VideoRecordingOptions extends BaseModel {
}

export declare function model_post_init(__context: any): void;
export declare function to_dict(): void;
export declare function to_json(path: any): void;
export declare function validate_browser(v: string): void;
