-- BytePort Deployments Migration
-- Migration: 002_add_deployments
-- Description: Add multi-cloud deployment tracking tables

-- Deployments table for tracking multi-cloud deployments
CREATE TABLE IF NOT EXISTS deployments (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    project_uuid UUID REFERENCES projects(uuid) ON DELETE CASCADE,

    -- Deployment status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- Status values: pending, detecting, provisioning, deploying, deployed, failed, terminated

    -- Provider configuration (JSONB for flexibility)
    providers JSONB NOT NULL DEFAULT '{}',
    -- Example: {"vercel": {"project_id": "...", "url": "..."}, "supabase": {...}}

    -- Services deployed (JSONB array)
    services JSONB NOT NULL DEFAULT '[]',
    -- Example: [{"name": "frontend", "type": "frontend", "provider": "vercel", "status": "running"}]

    -- Cost tracking
    cost_info JSONB,
    -- Example: {"monthly": 25, "breakdown": {"vercel": 0, "render": 7}}

    -- Deployment metadata
    metadata JSONB DEFAULT '{}',
    -- Store provider-specific IDs, configurations, etc.

    -- Environment variables (encrypted in production)
    env_vars JSONB DEFAULT '{}',

    -- Build information
    build_config JSONB DEFAULT '{}',
    -- Store build commands, framework detection results, etc.

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deployed_at TIMESTAMP,
    terminated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Deployment logs table
CREATE TABLE IF NOT EXISTS deployment_logs (
    id BIGSERIAL PRIMARY KEY,
    deployment_uuid UUID NOT NULL REFERENCES deployments(uuid) ON DELETE CASCADE,
    service_name VARCHAR(255),
    level VARCHAR(20) NOT NULL DEFAULT 'info',
    -- Levels: debug, info, warn, error
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Provider credentials table (for user-specific provider tokens)
CREATE TABLE IF NOT EXISTS provider_credentials (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    provider VARCHAR(100) NOT NULL,
    -- Providers: vercel, render, supabase, neon, upstash, fly, railway, etc.
    credentials JSONB NOT NULL,
    -- Store encrypted API keys, tokens, etc.
    is_valid BOOLEAN DEFAULT true,
    last_validated TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, provider)
);

-- Deployment events table (for audit trail)
CREATE TABLE IF NOT EXISTS deployment_events (
    id BIGSERIAL PRIMARY KEY,
    deployment_uuid UUID NOT NULL REFERENCES deployments(uuid) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    -- Event types: created, status_changed, service_added, service_removed, failed, terminated
    event_data JSONB DEFAULT '{}',
    user_id UUID REFERENCES users(uuid) ON DELETE SET NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Cost tracking table (for historical cost data)
CREATE TABLE IF NOT EXISTS cost_records (
    id BIGSERIAL PRIMARY KEY,
    deployment_uuid UUID REFERENCES deployments(uuid) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    breakdown JSONB NOT NULL,
    -- Breakdown by provider
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_deployments_owner ON deployments(owner);
CREATE INDEX idx_deployments_project_uuid ON deployments(project_uuid);
CREATE INDEX idx_deployments_status ON deployments(status);
CREATE INDEX idx_deployments_deleted_at ON deployments(deleted_at);
CREATE INDEX idx_deployments_created_at ON deployments(created_at DESC);

CREATE INDEX idx_deployment_logs_deployment_uuid ON deployment_logs(deployment_uuid);
CREATE INDEX idx_deployment_logs_level ON deployment_logs(level);
CREATE INDEX idx_deployment_logs_timestamp ON deployment_logs(timestamp DESC);
CREATE INDEX idx_deployment_logs_service_name ON deployment_logs(service_name);

CREATE INDEX idx_provider_credentials_user_id ON provider_credentials(user_id);
CREATE INDEX idx_provider_credentials_provider ON provider_credentials(provider);

CREATE INDEX idx_deployment_events_deployment_uuid ON deployment_events(deployment_uuid);
CREATE INDEX idx_deployment_events_timestamp ON deployment_events(timestamp DESC);
CREATE INDEX idx_deployment_events_event_type ON deployment_events(event_type);

CREATE INDEX idx_cost_records_deployment_uuid ON cost_records(deployment_uuid);
CREATE INDEX idx_cost_records_user_id ON cost_records(user_id);
CREATE INDEX idx_cost_records_period ON cost_records(period_start, period_end);

-- Create triggers for updated_at
CREATE TRIGGER update_deployments_updated_at BEFORE UPDATE ON deployments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_provider_credentials_updated_at BEFORE UPDATE ON provider_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE deployments IS 'Multi-cloud deployment tracking with provider-agnostic schema';
COMMENT ON TABLE deployment_logs IS 'Deployment logs from various services and providers';
COMMENT ON TABLE provider_credentials IS 'User-specific cloud provider credentials';
COMMENT ON TABLE deployment_events IS 'Audit trail for deployment lifecycle events';
COMMENT ON TABLE cost_records IS 'Historical cost tracking for deployments';

COMMENT ON COLUMN deployments.providers IS 'JSONB object containing provider-specific deployment information';
COMMENT ON COLUMN deployments.services IS 'JSONB array of deployed services';
COMMENT ON COLUMN deployments.cost_info IS 'Current cost information and estimates';
COMMENT ON COLUMN provider_credentials.credentials IS 'Encrypted provider API credentials';
