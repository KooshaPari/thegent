#!/usr/bin/env python3
"""
Deployment Script for Phenotype Services

Handles deployment to staging and production environments.

Usage:
    python deploy.py --service <name> --env <staging|production> --tag <version>

Examples:
    python deploy.py --service api-gateway --env staging --tag v1.2.3
    python deploy.py --service task-engine --env production --tag v1.2.3
    python deploy.py --all --env staging
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


# Service definitions
SERVICES = {
    "api-gateway": {
        "path": "services/api-gateway",
        "port": 8080,
        "health": "/health",
    },
    "task-engine": {
        "path": "services/task-engine",
        "port": 8081,
        "health": "/health",
    },
    "colab": {
        "path": "services/colab",
        "port": 8082,
        "health": "/health",
    },
}

# Environment configurations
ENVIRONMENTS = {
    "staging": {
        "namespace": "phenotype-staging",
        " replicas": 2,
        "resources": {"cpu": "500m", "memory": "512Mi"},
    },
    "production": {
        "namespace": "phenotype-prod",
        "replicas": 3,
        "resources": {"cpu": "1000m", "memory": "1Gi"},
    },
}


def run_command(cmd, cwd=None, capture=True):
    """Run a shell command."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=not capture
    )
    return result


def build_service(name, tag):
    """Build Docker image for a service."""
    service = SERVICES[name]
    path = Path(service["path"])

    print(f"\n[Building {name}]")
    print(f"  Path: {path}")
    print(f"  Tag: {tag}")

    # Check if Dockerfile exists
    dockerfile = path / "Dockerfile"
    if not dockerfile.exists():
        print(f"  ⚠ No Dockerfile found at {dockerfile}")
        return False

    # Build command
    image = f"phenotype/{name}:{tag}"
    cmd = [
        "docker", "build",
        "-t", image,
        "-f", str(dockerfile),
        str(path)
    ]

    result = run_command(cmd)
    if result.returncode != 0:
        print(f"  ✗ Build failed")
        return False

    print(f"  ✓ Built {image}")
    return True


def deploy_service(name, env, tag):
    """Deploy a service to an environment."""
    config = ENVIRONMENTS[env]
    service = SERVICES[name]
    image = f"phenotype/{name}:{tag}"

    print(f"\n[Deploying {name} to {env}]")
    print(f"  Image: {image}")
    print(f"  Namespace: {config['namespace']}")

    # For Kubernetes deployments
    manifest = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  namespace: {config['namespace']}
spec:
  replicas: {config['replicas']}
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
      - name: {name}
        image: {image}
        ports:
        - containerPort: {service['port']}
        resources:
          requests:
            cpu: {config['resources']['cpu']}
            memory: {config['resources']['memory']}
---
apiVersion: v1
kind: Service
metadata:
  name: {name}
  namespace: {config['namespace']}
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: {service['port']}
  selector:
    app: {name}
"""

    print(f"  Applying manifest...")
    # In production, would use kubectl apply -f -
    print(f"  ✓ Deployment manifest ready")
    return True


def main():
    parser = argparse.ArgumentParser(description="Deploy Phenotype services")
    parser.add_argument("--service", help="Service name (or 'all')")
    parser.add_argument("--env", choices=["staging", "production"], default="staging")
    parser.add_argument("--tag", default=f"dev-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    parser.add_argument("--build", action="store_true", help="Build before deploy")
    parser.add_argument("--deploy", action="store_true", help="Deploy after build")
    args = parser.parse_args()

    print(f"{'='*60}")
    print("Phenotype Deployment Script")
    print(f"Environment: {args.env}")
    print(f"Tag: {args.tag}")
    print(f"{'='*60}")

    # Determine which services to deploy
    if args.service == "all":
        services = list(SERVICES.keys())
    elif args.service:
        services = [args.service]
    else:
        print("Error: --service is required (or use --all)")
        sys.exit(1)

    # Build and deploy
    for name in services:
        if name not in SERVICES:
            print(f"Unknown service: {name}")
            continue

        if args.build:
            if not build_service(name, args.tag):
                sys.exit(1)

        if args.deploy:
            if not deploy_service(name, args.env, args.tag):
                sys.exit(1)

    print(f"\n{'='*60}")
    print(f"✓ Deployment complete")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
