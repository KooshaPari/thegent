#!/usr/bin/env zsh
# Zsh completion script for thegent
# Install: source this file or add to ~/.zshrc

#compdef thegent

_thegent() {
    local context state line
    local -a commands subcommands

    commands=(
        'run:Execute a task in the foreground'
        'bg:Start a background agent session'
        'ps:List active and historical agent sessions'
        'plan:Plan and manage work items'
        'doctor:Verify environment health'
        'setup:Initialize thegent configuration'
        'config:Manage configuration'
        'status:Show system status'
        'logs:View logs'
        'stop:Stop a running session'
        'resume:Resume a paused session'
        'retry:Retry a failed session'
        'purge:Clean up old data'
        'sweep:Clean up resources'
        'takeover:Take over a session'
        'history:View command history'
        'inspect:Inspect a session'
        'feedback:Provide feedback'
        'explorer:Explore resources'
        'modes:Manage modes'
        'operations:Manage operations'
        'drift:Check for drift'
        'audit-verify:Verify audit logs'
        'compliance-report:Generate compliance report'
        'cost-status:Show cost status'
        'data-protection:Manage data protection'
        'deep-research:Perform deep research'
        'discovery-parse:Parse discovery data'
        'discovery-register:Register discovery'
        'discovery-scan:Scan for resources'
        'forensics-snapshot:Create forensics snapshot'
        'govern-configure:Configure governance'
        'govern-go-cycle:Governance cycle'
        'govern-go-health:Governance health'
        'govern-go-status:Governance status'
        'govern-go-watch:Watch governance'
        'handoff-list:List handoffs'
        'handoff-show:Show handoff'
        'interruption-list:List interruptions'
        'interruption-snooze:Snooze interruption'
        'list-agents:List agents'
        'list-droids:List droids'
        'list-models:List models'
        'load-status:Show load status'
        'migration:Run migration'
        'policy-show:Show policy'
        'project-list:List projects'
        'project-register:Register project'
        'resolve-model-route:Resolve model route'
        'rules-sync:Sync rules'
        'session-contract-health-gate:Session contract health gate'
        'session-contract-health-report:Session contract health report'
        'session-contract-health-trend:Session contract health trend'
        'sitback-dashboard:Sitback dashboard'
        'summary:Show summary'
        'terminal-route:Terminal route'
        'usage:Show usage'
        'workstream-dashboard:Workstream dashboard'
        'workstream-query:Query workstream'
        'workstream-stats:Workstream statistics'
    )

    _arguments -C \
        "1: :->command" \
        "*::arg:->args"

    case $state in
        command)
            _describe 'command' commands
            ;;
        args)
            case $words[1] in
                doctor)
                    _arguments \
                        '--fix[Attempt automatic fixes]' \
                        '--runtime[Check runtime status]' \
                        '--network[Check network connectivity]' \
                        '--processes[Check process health]' \
                        '--memory[Check memory usage]' \
                        '--deps[Check dependencies]'
                    ;;
                config)
                    _arguments \
                        '1: :(validate show migrate)'
                    ;;
                setup)
                    _arguments \
                        '--wizard[Interactive setup wizard]' \
                        '--hooks[Install hooks]'
                    ;;
                plan)
                    _arguments \
                        '1: :(loop do-next analyze claim complete get-next incorporate progress wait-next)'
                    ;;
                govern)
                    _arguments \
                        '1: :(go-cycle go-health go-status go-watch configure)'
                    ;;
            esac
            ;;
    esac
}

_thegent "$@"
