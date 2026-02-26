"""Register a sample feature flag for framework validation."""
# This would use phenotype_config when the wheel is built
# For now, demonstrates the registration pattern
print("phenoctl flags create --stage A --class F --channel dev,alpha,beta,canary,stable streaming_api_v1")
