use clap::{Parser, Subcommand};
use thegent_maif::{MAIFArtifact, generate_key_pair, load_private_key, load_public_key, MAIFError};
use std::path::PathBuf;
use std::collections::BTreeMap;
use serde_json::json;
use pkcs8::{EncodePrivateKey, EncodePublicKey, LineEnding};
use std::fs;

#[derive(Parser)]
#[command(name = "thegent-maif")]
#[command(about = "MAIF (Model-Aware Information Flow) Action Artifacts CLI", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Generate a new RSA key pair for signing artifacts
    Keygen {
        /// Number of bits for the RSA key [default: 2048]
        #[arg(short, long, default_value_t = 2048)]
        bits: usize,
        /// Path to save the private key
        #[arg(short, long)]
        private_key: PathBuf,
        /// Path to save the public key
        #[arg(short, long)]
        public_key: PathBuf,
    },
    /// Create and sign a new action artifact
    Create {
        /// Action type (e.g., shell_command, file_write)
        #[arg(short, long)]
        action: String,
        /// JSON payload for the action
        #[arg(short, long)]
        payload: String,
        /// Agent ID
        #[arg(short, long)]
        agent: String,
        /// Session ID
        #[arg(short, long)]
        session: String,
        /// Path to the private key for signing
        #[arg(short, long)]
        key: PathBuf,
        /// Output path for the artifact JSON
        #[arg(short, long)]
        output: PathBuf,
    },
    /// Verify an existing action artifact
    Verify {
        /// Path to the artifact JSON
        #[arg(short, long)]
        artifact: PathBuf,
        /// Path to the public key for verification
        #[arg(short, long)]
        key: PathBuf,
    },
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Keygen { bits, private_key, public_key } => {
            let (priv_key, pub_key) = generate_key_pair(bits)?;
            
            let priv_pem = priv_key.to_pkcs8_pem(LineEnding::LF)?;
            fs::write(private_key, priv_pem.as_bytes())?;
            
            let pub_pem = pub_key.to_public_key_pem(LineEnding::LF)?;
            fs::write(public_key, pub_pem.as_bytes())?;
            
            println!("Key pair generated successfully.");
        }
        Commands::Create { action, payload, agent, session, key, output } => {
            let payload_map: BTreeMap<String, serde_json::Value> = serde_json::from_str(&payload)?;
            let mut artifact = MAIFArtifact::new(action, payload_map, agent, session);
            
            let priv_key = load_private_key(&key)?;
            artifact.sign(&priv_key)?;
            
            artifact.save_to_file(&output)?;
            println!("Artifact created and signed: {}", output.display());
        }
        Commands::Verify { artifact, key } => {
            let art = MAIFArtifact::load_from_file(&artifact)?;
            let pub_key = load_public_key(&key)?;
            
            if art.verify(&pub_key)? {
                println!("Verification SUCCESSFUL");
            } else {
                println!("Verification FAILED");
                std::process::exit(1);
            }
        }
    }

    Ok(())
}
