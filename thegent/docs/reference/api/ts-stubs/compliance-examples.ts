// Auto-generated usage examples for compliance
// Source: generate-api-docs.py

import { ComplianceAuditTrail, ComplianceControl, ComplianceEnforcer, ComplianceExporter, ComplianceProfile, ComplianceProfileType, check_control, enforce_mandatory, export_bundle, get_mandatory_controls, record_action } from "./compliance";

// Create a ComplianceAuditTrail instance
const complianceaudittrail = new ComplianceAuditTrail("example_storage_path");
complianceaudittrail.record_action("example_action", undefined as unknown as Record<(str, Any)>, undefined as unknown as ComplianceProfile);

// Create a ComplianceControl instance
const compliancecontrol = new ComplianceControl();

// Create a ComplianceEnforcer instance
const complianceenforcer = new ComplianceEnforcer(undefined as unknown as ComplianceProfile);
complianceenforcer.check_control("example_control_id", undefined as unknown as Record<(str, Any)>);
complianceenforcer.enforce_mandatory("example_action", undefined as unknown as Record<(str, Any)>);

// Create a ComplianceExporter instance
const complianceexporter = new ComplianceExporter("example_session_dir");
complianceexporter.export_bundle("example_framework", "example_target_path");

// Create a ComplianceProfile instance
const complianceprofile = new ComplianceProfile();
complianceprofile.get_mandatory_controls();

// Create a ComplianceProfileType instance
const complianceprofiletype = new ComplianceProfileType();

// Call check_control
check_control(undefined as unknown as any, "example_control_id", undefined as unknown as Record<(str, Any)>);
// Call enforce_mandatory
enforce_mandatory(undefined as unknown as any, "example_action", undefined as unknown as Record<(str, Any)>);
// Call export_bundle
export_bundle(undefined as unknown as any, "example_framework", "example_target_path");
// Call get_mandatory_controls
get_mandatory_controls(undefined as unknown as any);
// Call record_action
record_action(undefined as unknown as any, "example_action", undefined as unknown as Record<(str, Any)>, undefined as unknown as ComplianceProfile);
