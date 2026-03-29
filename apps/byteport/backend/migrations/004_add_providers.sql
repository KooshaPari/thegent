-- BytePort Cloud Provider Integrations Migration
-- Migration: 004_add_providers
-- Description: Add provider-specific tables and configurations

-- Provider configurations (system-level)
CREATE TABLE IF NOT EXISTS provider_configs (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,

    -- Provider capabilities
    supported_types JSONB NOT NULL,
    -- Example: ["frontend", "backend", "database"]

    -- Pricing information
    pricing_tiers JSONB NOT NULL,
    -- Tier information for cost estimation

    -- Provider status
    is_enabled BOOLEAN DEFAULT true,
    is_beta BOOLEAN DEFAULT false,

    -- Provider metadata
    metadata JSONB DEFAULT '{}',
    -- API endpoints, documentation links, etc.

    -- Rate limits
    rate_limits JSONB DEFAULT '{}',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default provider configurations
INSERT INTO provider_configs (provider, display_name, supported_types, pricing_tiers, metadata) VALUES
('vercel', 'Vercel', '["frontend"]',
 '{"hobby": {"monthly": 0, "limits": {"bandwidth": "100GB", "builds": 100}}, "pro": {"monthly": 20}}',
 '{"api_url": "https://api.vercel.com", "docs": "https://vercel.com/docs"}'),

('render', 'Render', '["frontend", "backend", "database"]',
 '{"free": {"monthly": 0, "limits": {"hours": 750}}, "starter": {"monthly": 7}, "standard": {"monthly": 25}}',
 '{"api_url": "https://api.render.com", "docs": "https://render.com/docs"}'),

('supabase', 'Supabase', '["database", "storage", "backend"]',
 '{"free": {"monthly": 0, "limits": {"storage": "500MB", "bandwidth": "2GB"}}, "pro": {"monthly": 25}}',
 '{"api_url": "https://api.supabase.com", "docs": "https://supabase.com/docs"}'),

('neon', 'Neon', '["database"]',
 '{"free": {"monthly": 0, "limits": {"storage": "3GB", "compute": "100h"}}, "pro": {"monthly": 19}}',
 '{"api_url": "https://console.neon.tech/api/v2", "docs": "https://neon.tech/docs"}'),

('upstash', 'Upstash', '["cache", "queue", "database"]',
 '{"free": {"monthly": 0, "limits": {"requests": "10000"}}, "payg": {"monthly": 0, "per_request": 0.0002}}',
 '{"api_url": "https://api.upstash.com", "docs": "https://upstash.com/docs"}'),

('fly', 'Fly.io', '["frontend", "backend"]',
 '{"free": {"monthly": 0, "limits": {"machines": 3}}, "payg": {"monthly": 0}}',
 '{"api_url": "https://api.fly.io", "docs": "https://fly.io/docs"}'),

('railway', 'Railway', '["frontend", "backend", "database"]',
 '{"trial": {"monthly": 0, "limits": {"hours": 500}}, "developer": {"monthly": 5}, "team": {"monthly": 20}}',
 '{"api_url": "https://backboard.railway.app/graphql/v2", "docs": "https://docs.railway.app"}'),

('byteport-host', 'BytePort Host', '["frontend", "backend", "database", "cache", "storage", "queue"]',
 '{"free": {"monthly": 0}}',
 '{"type": "self-hosted"}')
ON CONFLICT (provider) DO NOTHING;

-- Framework detection patterns
CREATE TABLE IF NOT EXISTS framework_patterns (
    id SERIAL PRIMARY KEY,
    framework VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    -- Type: frontend, backend, fullstack

    -- Detection patterns
    file_patterns JSONB NOT NULL,
    -- Example: {"package.json": {"dependencies": {"next": "*"}}}

    dependency_patterns JSONB DEFAULT '{}',
    -- Dependency name patterns to check

    confidence_weight DECIMAL(3, 2) DEFAULT 1.0,
    -- Weight for confidence calculation

    -- Build configuration
    default_build_command VARCHAR(500),
    default_start_command VARCHAR(500),
    default_install_command VARCHAR(500),

    -- Recommended providers
    recommended_providers JSONB DEFAULT '[]',

    -- Framework metadata
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(framework, type)
);

-- Insert common framework patterns
INSERT INTO framework_patterns (framework, type, file_patterns, default_build_command, default_start_command, recommended_providers, metadata) VALUES
('nextjs', 'frontend',
 '{"next.config.js": true, "package.json": {"dependencies": {"next": "*"}}}',
 'npm run build', 'npm start', '["vercel", "render"]',
 '{"runtime": "nodejs", "category": "react-framework"}'),

('react', 'frontend',
 '{"package.json": {"dependencies": {"react": "*"}}}',
 'npm run build', 'npm start', '["vercel", "render"]',
 '{"runtime": "nodejs", "category": "library"}'),

('express', 'backend',
 '{"package.json": {"dependencies": {"express": "*"}}}',
 'npm install', 'npm start', '["render", "fly"]',
 '{"runtime": "nodejs", "category": "framework"}'),

('nestjs', 'backend',
 '{"nest-cli.json": true, "package.json": {"dependencies": {"@nestjs/core": "*"}}}',
 'npm run build', 'npm run start:prod', '["render", "fly"]',
 '{"runtime": "nodejs", "category": "framework"}'),

('django', 'backend',
 '{"requirements.txt": {"Django": "*"}, "manage.py": true}',
 'pip install -r requirements.txt', 'python manage.py runserver', '["render", "fly"]',
 '{"runtime": "python", "category": "framework"}'),

('fastapi', 'backend',
 '{"requirements.txt": {"fastapi": "*"}}',
 'pip install -r requirements.txt', 'uvicorn main:app', '["render", "fly"]',
 '{"runtime": "python", "category": "framework"}')
ON CONFLICT (framework, type) DO NOTHING;

-- API rate limit tracking
CREATE TABLE IF NOT EXISTS api_rate_limits (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    request_count INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, endpoint, window_start)
);

-- Create indexes
CREATE INDEX idx_provider_configs_is_enabled ON provider_configs(is_enabled);

CREATE INDEX idx_framework_patterns_type ON framework_patterns(type);
CREATE INDEX idx_framework_patterns_framework ON framework_patterns(framework);

CREATE INDEX idx_api_rate_limits_user_id ON api_rate_limits(user_id);
CREATE INDEX idx_api_rate_limits_window_start ON api_rate_limits(window_start);

-- Create triggers
CREATE TRIGGER update_provider_configs_updated_at BEFORE UPDATE ON provider_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_framework_patterns_updated_at BEFORE UPDATE ON framework_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean up old rate limit records
CREATE OR REPLACE FUNCTION cleanup_old_rate_limits()
RETURNS void AS $$
BEGIN
    DELETE FROM api_rate_limits
    WHERE window_start < NOW() - INTERVAL '1 hour';
END;
$$ language 'plpgsql';

-- Add comments
COMMENT ON TABLE provider_configs IS 'System-level cloud provider configurations and capabilities';
COMMENT ON TABLE framework_patterns IS 'Patterns for detecting application frameworks';
COMMENT ON TABLE api_rate_limits IS 'Track API rate limits per user and endpoint';

COMMENT ON COLUMN provider_configs.supported_types IS 'Service types supported by this provider';
COMMENT ON COLUMN provider_configs.pricing_tiers IS 'Pricing tier information for cost estimation';
COMMENT ON COLUMN framework_patterns.file_patterns IS 'File patterns for framework detection';
COMMENT ON COLUMN framework_patterns.confidence_weight IS 'Weight for confidence score calculation';
