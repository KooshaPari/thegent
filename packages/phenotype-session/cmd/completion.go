package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

var completionCmd = &cobra.Command{
	Use:   "completion [bash|zsh|fish|powershell]",
	Short: "Generate shell completion scripts",
	Long: `Generate shell completion scripts for pheno-session.

To load completions:

Bash:

  $ source <(pheno-session completion bash)

  # To load completions for each session, execute once:
  $ pheno-session completion bash > /etc/bash_completion.d/pheno-session

Zsh:

  # If shell completion is not already enabled in your environment,
  # you will need to enable it.  You can execute the following once:

  $ echo "autoload -U compinit; compinit" >> ~/.zshrc

  # To load completions for each session, execute once:
  $ pheno-session completion zsh > "${fpath[1]}/_pheno-session"

  # You will need to start a new shell for this setup to take effect.

Fish:

  $ pheno-session completion fish | source

  # To load completions for each session, execute once:
  $ pheno-session completion fish > ~/.config/fish/completions/pheno-session.fish

PowerShell:

  $ pheno-session completion powershell | Out-String | Invoke-Expression

  # To load completions for each session, execute once:
  $ pheno-session completion powershell > pheno-session.ps1
  # and source this file from your PowerShell profile.
`,
	DisableFlagsInUseLine: true,
	ValidArgs:             []string{"bash", "zsh", "fish", "powershell"},
	Args:                  cobra.ExactValidArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		switch args[0] {
		case "bash":
			return rootCmd.GenBashCompletion(os.Stdout)
		case "zsh":
			return rootCmd.GenZshCompletion(os.Stdout)
		case "fish":
			return rootCmd.GenFishCompletion(os.Stdout, true)
		case "powershell":
			return rootCmd.GenPowerShellCompletionWithDesc(os.Stdout)
		}
		return nil
	},
}
