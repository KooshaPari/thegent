# Self-Hosted Runner Setup

## One-time Setup

```bash
# Create runner directory
mkdir -p actions-runner && cd actions-runner

# Download runner
curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.320.0/actions-runner-osx-x64-2.320.0.tar.gz
tar xzf actions-runner.tar.gz

# Configure (follow prompts)
./config.sh --url https://github.com/KooshaPari/thegent --token <TOKEN>

# Install as service
./svc.sh install
./svc.sh start
```

## Token Generation
Go to: https://github.com/KooshaPari/thegent/settings/actions/runners/new?arch=x64&os=osx
