// Auto-generated usage examples for provisioner
// Source: generate-api-docs.py

import { InfraProvisioner, ResourceSpec, decommission, provision } from "./provisioner";

// Create a InfraProvisioner instance
const infraprovisioner = new InfraProvisioner("example_provider");
infraprovisioner.decommission("example_resource_id");
infraprovisioner.provision("example_resource_id", undefined as unknown as ResourceSpec);

// Create a ResourceSpec instance
const resourcespec = new ResourceSpec();

// Call decommission
decommission(undefined as unknown as any, "example_resource_id");
// Call provision
provision(undefined as unknown as any, "example_resource_id", undefined as unknown as ResourceSpec);
