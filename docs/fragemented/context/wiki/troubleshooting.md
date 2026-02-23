# Troubleshooting Guide

## Common Issues and Solutions

### Getting Started Issues

#### "Command not found: ante"
- **Solution**: Ensure Ante is properly installed and in your PATH
- **Check**: Run `which ante` to verify installation
- **Reference**: See [Getting Started](./getting-started.md)

#### Import or dependency errors
- **Solution**: Verify all dependencies are installed
- **Check**: Review the Getting Started guide for installation steps
- **Reference**: [Getting Started](./getting-started.md)

### Interactive TUI Issues

#### TUI not displaying correctly
- **Solution**: Check terminal compatibility
- **Tips**:
  - Ensure terminal supports 256 colors
  - Try resizing your terminal window
  - Use a modern terminal emulator
- **Reference**: [Interactive TUI](./guides/interactive-tui.md)

#### Performance issues in TUI
- **Solution**: Check system resources and agent complexity
- **Reference**: [Architecture](./advanced/architecture.md) for system requirements

### Agent & Model Issues

#### Model not responding
- **Solutions**:
  1. Check provider configuration in [Preferences](./features/preferences.md)
  2. Verify API keys and credentials
  3. Check internet connection (unless using [Offline Mode](./features/offline-mode.md))
  4. Consult [Model & Provider Catalog](./features/model-catalog.md) for compatibility

#### Sub-Agent communication issues
- **Reference**: [Sub-Agents](./features/sub-agents.md)
- **Tips**:
  - Verify agent configuration
  - Check Memory settings in [Memory](./features/memory.md)
  - Review agent organization in [Agent Organization](./features/agent-organization.md)

### Skills & Tools Issues

#### Custom skill not loading
- **Reference**: [Skills](./features/skills.md)
- **Tips**:
  - Verify skill syntax and structure
  - Check file permissions
  - Review error messages for specific issues

#### Tool execution errors
- **Reference**: [Tools](./features/tools.md)
- **Tips**:
  - Verify tool configuration
  - Check required parameters
  - Review tool documentation

### Mode-Specific Issues

#### Headless Mode Issues
- **Reference**: [Headless Mode](./guides/headless-mode.md)
- **Common Solutions**:
  - Verify script syntax
  - Check environment variables
  - Review configuration files

#### Offline Mode Issues
- **Reference**: [Offline Mode](./features/offline-mode.md)
- **Note**: Offline mode is experimental
- **Tips**:
  - Verify offline mode is properly configured
  - Check local model availability
  - Review memory configuration

### Configuration Issues

#### Settings not persisting
- **Reference**: [Preferences](./features/preferences.md)
- **Solutions**:
  1. Check preferences file location
  2. Verify file permissions
  3. Review configuration syntax

#### Provider configuration errors
- **Reference**: [Model & Provider Catalog](./features/model-catalog.md)
- **Tips**:
  - Verify provider name and parameters
  - Check for typos in configuration
  - Validate credentials

### Performance & Optimization

#### Slow agent responses
- **Solutions**:
  1. Check [Architecture](./advanced/architecture.md) for optimization tips
  2. Review agent configuration in [Sub-Agents](./features/sub-agents.md)
  3. Check [Memory](./features/memory.md) settings

#### High memory usage
- **Reference**: [Architecture](./advanced/architecture.md)
- **Tips**:
  - Limit agent memory retention in [Memory](./features/memory.md)
  - Reduce number of concurrent agents
  - Check for memory leaks in custom skills

### Debugging Steps

1. **Enable verbose logging** (if available):
   - Check [Preferences](./features/preferences.md) for logging options

2. **Verify configuration**:
   - Review [Preferences](./features/preferences.md)
   - Check [Model & Provider Catalog](./features/model-catalog.md)

3. **Check system state**:
   - Review [Architecture](./advanced/architecture.md)
   - Verify [Core Concepts](./reference/core-concepts.md) understanding

4. **Review documentation**:
   - Check relevant feature documentation
   - Review the specific guide for your use case

5. **Isolate the issue**:
   - Test with minimal configuration
   - Disable custom skills/tools temporarily
   - Try with default settings

### Getting Help

1. **Check relevant documentation**:
   - Feature docs in [Features](./features/)
   - Guides in [Guides](./guides/)
   - Advanced topics in [Advanced](./advanced/)

2. **Review examples**:
   - Consult [Getting Started](./getting-started.md)
   - Check specific feature documentation

3. **Consult technical details**:
   - [Architecture](./advanced/architecture.md)
   - [Core Concepts](./reference/core-concepts.md)

4. **Official resources**:
   - Visit https://docs.antigma.ai
   - Check GitHub issues
   - Contact support channels

## Error Messages

### Common Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Provider not found" | Invalid provider name | Check [Model & Provider Catalog](./features/model-catalog.md) |
| "API key invalid" | Bad credentials | Verify in [Preferences](./features/preferences.md) |
| "Skill import error" | Malformed skill | Review [Skills](./features/skills.md) |
| "Agent initialization failed" | Bad config | Check [Sub-Agents](./features/sub-agents.md) configuration |
| "Memory access error" | Permission issue | See [Memory](./features/memory.md) |

## Performance Tuning

For optimization tips, see:
- [Architecture](./advanced/architecture.md) - System design and optimization
- [Preferences](./features/preferences.md) - Configuration options
- [Memory](./features/memory.md) - Memory management

## Experimental Features

Ante includes experimental features that may have issues:
- **Offline Mode**: See [Offline Mode](./features/offline-mode.md)
- **Agent Organization**: See [Agent Organization](./features/agent-organization.md)

## Still Having Issues?

1. Check the [FAQ](./faq.md) for common questions
2. Review all relevant documentation sections
3. Visit https://docs.antigma.ai for official support
4. Check GitHub issues and discussions

---

**Note**: This troubleshooting guide is based on official Ante documentation. For the most current information and support, visit https://docs.antigma.ai
