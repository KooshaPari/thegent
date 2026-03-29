-- BytePort Self-Hosted Targets Migration
-- Migration: 003_add_hosts
-- Description: Add support for self-hosted deployment targets

-- Hosts table (self-hosted servers)
CREATE TABLE IF NOT EXISTS hosts (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,

    -- Host connection information
    host_url VARCHAR(500) NOT NULL,
    -- URL of the host agent API

    api_key VARCHAR(255) NOT NULL,
    -- API key for authenticating with host agent

    -- Host specifications
    specs JSONB DEFAULT '{}',
    -- CPU, RAM, storage, etc.

    -- Host status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- Status: pending, online, offline, error

    last_heartbeat TIMESTAMP,
    -- Last successful ping from host agent

    -- Host capabilities
    capabilities JSONB DEFAULT '[]',
    -- Supported features: docker, kubernetes, etc.

    -- Host metadata
    metadata JSONB DEFAULT '{}',
    region VARCHAR(100),
    -- Geographic region or datacenter

    -- Resource limits
    max_deployments INTEGER DEFAULT 10,
    current_deployments INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Host deployments (mapping deployments to hosts)
CREATE TABLE IF NOT EXISTS host_deployments (
    id BIGSERIAL PRIMARY KEY,
    deployment_uuid UUID NOT NULL REFERENCES deployments(uuid) ON DELETE CASCADE,
    host_uuid UUID NOT NULL REFERENCES hosts(uuid) ON DELETE CASCADE,

    -- Container/service information
    container_id VARCHAR(255),
    service_name VARCHAR(255) NOT NULL,

    -- Port mappings
    port_mappings JSONB DEFAULT '[]',
    -- Example: [{"host": 8080, "container": 3000}]

    -- Environment configuration
    env_config JSONB DEFAULT '{}',

    -- Resource allocation
    resources JSONB DEFAULT '{}',
    -- CPU, memory limits

    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- Status: pending, starting, running, stopped, error

    -- Health check
    health_check_url VARCHAR(500),
    last_health_check TIMESTAMP,
    health_status VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(deployment_uuid, service_name, host_uuid)
);

-- Host metrics (for monitoring)
CREATE TABLE IF NOT EXISTS host_metrics (
    id BIGSERIAL PRIMARY KEY,
    host_uuid UUID NOT NULL REFERENCES hosts(uuid) ON DELETE CASCADE,

    -- CPU metrics
    cpu_usage DECIMAL(5, 2),
    cpu_cores INTEGER,

    -- Memory metrics
    memory_used BIGINT,
    memory_total BIGINT,

    -- Storage metrics
    storage_used BIGINT,
    storage_total BIGINT,

    -- Network metrics
    network_rx BIGINT,
    network_tx BIGINT,

    -- Additional metrics
    metrics JSONB DEFAULT '{}',

    timestamp TIMESTAMP DEFAULT NOW()
);

-- Host logs (agent logs)
CREATE TABLE IF NOT EXISTS host_logs (
    id BIGSERIAL PRIMARY KEY,
    host_uuid UUID NOT NULL REFERENCES hosts(uuid) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL DEFAULT 'info',
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_hosts_owner ON hosts(owner);
CREATE INDEX idx_hosts_status ON hosts(status);
CREATE INDEX idx_hosts_deleted_at ON hosts(deleted_at);
CREATE INDEX idx_hosts_last_heartbeat ON hosts(last_heartbeat DESC);

CREATE INDEX idx_host_deployments_deployment_uuid ON host_deployments(deployment_uuid);
CREATE INDEX idx_host_deployments_host_uuid ON host_deployments(host_uuid);
CREATE INDEX idx_host_deployments_status ON host_deployments(status);

CREATE INDEX idx_host_metrics_host_uuid ON host_metrics(host_uuid);
CREATE INDEX idx_host_metrics_timestamp ON host_metrics(timestamp DESC);

CREATE INDEX idx_host_logs_host_uuid ON host_logs(host_uuid);
CREATE INDEX idx_host_logs_timestamp ON host_logs(timestamp DESC);
CREATE INDEX idx_host_logs_level ON host_logs(level);

-- Create triggers
CREATE TRIGGER update_hosts_updated_at BEFORE UPDATE ON hosts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_host_deployments_updated_at BEFORE UPDATE ON host_deployments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update current_deployments count
CREATE OR REPLACE FUNCTION update_host_deployment_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE hosts
        SET current_deployments = current_deployments + 1
        WHERE uuid = NEW.host_uuid;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE hosts
        SET current_deployments = GREATEST(current_deployments - 1, 0)
        WHERE uuid = OLD.host_uuid;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_host_deployment_count_trigger
AFTER INSERT OR DELETE ON host_deployments
FOR EACH ROW EXECUTE FUNCTION update_host_deployment_count();

-- Add comments
COMMENT ON TABLE hosts IS 'Self-hosted deployment targets with host agent';
COMMENT ON TABLE host_deployments IS 'Deployments running on self-hosted targets';
COMMENT ON TABLE host_metrics IS 'Time-series metrics from host agents';
COMMENT ON TABLE host_logs IS 'Logs from host agents';

COMMENT ON COLUMN hosts.specs IS 'Hardware specifications of the host';
COMMENT ON COLUMN hosts.capabilities IS 'Features supported by the host agent';
COMMENT ON COLUMN host_deployments.port_mappings IS 'Port mappings for container services';
