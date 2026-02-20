#!/usr/bin/env bash
# Bash completion script for thegent
# Install: source this file or add to ~/.bashrc

_thegent() {
    local cur prev words cword
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    words=("${COMP_WORDS[@]}")

    # Main commands
    local commands="run bg ps plan doctor setup config status logs stop resume retry purge sweep takeover history inspect feedback explorer modes operations drift audit-verify compliance-report cost-status data-protection deep-research discovery-parse discovery-register discovery-scan forensics-snapshot govern-configure govern-go-cycle govern-go-health govern-go-status govern-go-watch handoff-list handoff-show interruption-list interruption-snooze list-agents list-droids list-models load-status migration policy-show project-list project-register resolve-model-route rules-sync session-contract-health-gate session-contract-health-report session-contract-health-trend sitback-dashboard summary terminal-route usage workstream-dashboard workstream-query workstream-stats archive closure-pack cockpit contracts-conformance contracts-registry dag-add dag-cancel dag-checkpoint dag-checkpoints dag-list dag-probe dag-ready dag-reconcile dag-recover dag-remove dag-rollback dag-run dag-status dag-sync dag-update dag-validate escalate-add escalate-approve escalate-list escalate-resolve loop loop-send loop-stop plan-analyze plan-claim plan-complete plan-do-next plan-get-next plan-incorporate plan-progress plan-wait-next"

    # Subcommands for specific commands
    case "${prev}" in
        doctor)
            COMPREPLY=($(compgen -W "--fix --runtime --network --processes --memory --deps" -- "${cur}"))
            return 0
            ;;
        config)
            COMPREPLY=($(compgen -W "validate show migrate" -- "${cur}"))
            return 0
            ;;
        setup)
            COMPREPLY=($(compgen -W "--wizard --hooks" -- "${cur}"))
            return 0
            ;;
        plan)
            COMPREPLY=($(compgen -W "loop do-next analyze claim complete get-next incorporate progress wait-next" -- "${cur}"))
            return 0
            ;;
        govern)
            COMPREPLY=($(compgen -W "go-cycle go-health go-status go-watch configure" -- "${cur}"))
            return 0
            ;;
    esac

    # Complete main commands
    if [[ ${cword} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
        return 0
    fi

    return 0
}

complete -F _thegent thegent
