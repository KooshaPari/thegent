-- BytePort Initial Schema Migration
-- PostgreSQL version 15+
-- Migration: 001_initial_schema
-- Description: Create initial database schema with users, projects, instances, and git_secrets

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,

    -- AWS Credentials (embedded)
    aws_access_key_id VARCHAR(255),
    aws_secret_access_key VARCHAR(255),

    -- LLM Configuration (embedded)
    llm_provider VARCHAR(100),
    llm_providers JSONB DEFAULT '{}',

    -- Portfolio (embedded)
    portfolio_root_endpoint VARCHAR(500),
    portfolio_api_key VARCHAR(255),

    -- Git Configuration (embedded)
    git_access_token TEXT,
    git_refresh_token TEXT,
    git_token_expiry TIMESTAMP,
    git_refresh_token_expiry TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id TEXT NOT NULL,
    owner UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    name TEXT NOT NULL,

    -- Repository information
    repository_id TEXT,

    -- Project metadata
    readme TEXT,
    description TEXT,
    last_updated TIMESTAMP DEFAULT NOW(),
    platform TEXT,
    access_url TEXT,
    type TEXT,

    -- Deployments stored as JSONB
    deployments JSONB DEFAULT '{}',

    -- Timestamps (GORM fields)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    full_name TEXT,
    url TEXT,
    private BOOLEAN DEFAULT false,
    default_branch TEXT,
    owner_id UUID REFERENCES users(uuid) ON DELETE CASCADE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Instances table
CREATE TABLE IF NOT EXISTS instances (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    project_uuid UUID REFERENCES projects(uuid) ON DELETE SET NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    res_uuid TEXT NOT NULL,

    -- Resources stored as JSONB
    resources JSONB DEFAULT '[]',

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- AWS Resources table (for detailed resource tracking)
CREATE TABLE IF NOT EXISTS aws_resources (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID REFERENCES instances(uuid) ON DELETE CASCADE,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    arn TEXT,
    region TEXT,
    status TEXT,
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Git Secrets table
CREATE TABLE IF NOT EXISTS git_secrets (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(uuid) ON DELETE CASCADE,
    client_id TEXT NOT NULL,
    client_secret TEXT NOT NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_deleted_at ON users(deleted_at);

CREATE INDEX idx_projects_owner ON projects(owner);
CREATE INDEX idx_projects_repository_id ON projects(repository_id);
CREATE INDEX idx_projects_deleted_at ON projects(deleted_at);
CREATE INDEX idx_projects_type ON projects(type);
CREATE INDEX idx_projects_platform ON projects(platform);

CREATE INDEX idx_repositories_owner_id ON repositories(owner_id);
CREATE INDEX idx_repositories_full_name ON repositories(full_name);

CREATE INDEX idx_instances_owner ON instances(owner);
CREATE INDEX idx_instances_project_uuid ON instances(project_uuid);
CREATE INDEX idx_instances_status ON instances(status);

CREATE INDEX idx_aws_resources_instance_id ON aws_resources(instance_id);
CREATE INDEX idx_aws_resources_resource_type ON aws_resources(resource_type);

CREATE INDEX idx_git_secrets_user_id ON git_secrets(user_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic updated_at updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_repositories_updated_at BEFORE UPDATE ON repositories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_instances_updated_at BEFORE UPDATE ON instances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_aws_resources_updated_at BEFORE UPDATE ON aws_resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_git_secrets_updated_at BEFORE UPDATE ON git_secrets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts with embedded credentials for various services';
COMMENT ON TABLE projects IS 'Projects represent deployed applications';
COMMENT ON TABLE repositories IS 'Git repositories linked to user accounts';
COMMENT ON TABLE instances IS 'Running instances of deployed projects';
COMMENT ON TABLE aws_resources IS 'AWS resources created for instances';
COMMENT ON TABLE git_secrets IS 'GitHub OAuth application credentials';

COMMENT ON COLUMN users.llm_providers IS 'JSONB object containing API keys for various LLM providers';
COMMENT ON COLUMN projects.deployments IS 'JSONB object containing deployment information';
COMMENT ON COLUMN instances.resources IS 'JSONB array containing resource information';
