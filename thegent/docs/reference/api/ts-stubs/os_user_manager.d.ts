// Auto-generated TypeScript declarations for os_user_manager
// Source: generate-api-docs.py

export declare class OSUser {
}

export declare class OSUserManager {
  constructor(prefix: string);
  create_user(name: string, home_base: any): void;
  delete_user(username: string, delete_home: boolean): void;
}

export declare function create_user(name: string, home_base: any): void;
export declare function delete_user(username: string, delete_home: boolean): void;
