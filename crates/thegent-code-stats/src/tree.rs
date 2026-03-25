//! Tree generation for visualization.

use crate::stats::{CodeStats, DirectoryStats, FileStats, LanguageStats, SummaryStats};
use crate::config::TreeConfig;

/// Generates ASCII tree visualizations.
pub struct TreeGenerator {
    config: TreeConfig,
}

impl TreeGenerator {
    pub fn new(config: TreeConfig) -> Self {
        Self { config }
    }

    /// Generate a file tree in ASCII format.
    pub fn generate_file_tree(&self, stats: &CodeStats) -> String {
        let mut output = String::new();
        output.push_str("# File Tree\n\n");
        output.push_str("Files sorted by lines of code (LOC):\n\n");
        output.push_str("```\n");

        let total_loc = stats.summary.total_loc;

        for file in &stats.summary.largest_files {
            let percentage = if total_loc > 0 {
                (file.loc as f64 / total_loc as f64) * 100.0
            } else {
                0.0
            };

            let bar = self.render_bar(percentage);
            output.push_str(&format!(
                "{:6} LOC │{}{} {} ({})\n",
                file.loc,
                bar,
                " ".repeat(3),
                file.path,
                file.language
            ));
        }

        output.push_str("```\n");
        output
    }

    /// Generate a directory tree in ASCII format.
    pub fn generate_directory_tree(&self, stats: &CodeStats) -> String {
        let mut output = String::new();
        output.push_str("# Directory Tree\n\n");
        output.push_str("Directories sorted by total LOC:\n\n");
        output.push_str("```\n");

        let total_loc = stats.summary.total_loc;

        // Build directory hierarchy
        let mut dir_stats: Vec<(&String, usize)> = stats
            .by_directory
            .iter()
            .map(|(path, dir)| (path, dir.total_loc))
            .collect();
        dir_stats.sort_by(|a, b| b.1.cmp(&a.1));

        for (path, loc) in dir_stats.into_iter().take(30) {
            let percentage = if total_loc > 0 {
                (loc as f64 / total_loc as f64) * 100.0
            } else {
                0.0
            };

            let bar = self.render_bar(percentage);
            let files = stats
                .by_directory
                .get(path)
                .map(|d| d.total_files)
                .unwrap_or(0);

            output.push_str(&format!(
                "{:6} LOC │{}{} 📁 {} ({}) files\n",
                loc,
                bar,
                " ".repeat(3),
                if path.is_empty() { "./" } else { path },
                files
            ));
        }

        output.push_str("```\n");
        output
    }

    /// Generate a technology/language tree in ASCII format.
    pub fn generate_language_tree(&self, stats: &CodeStats) -> String {
        let mut output = String::new();
        output.push_str("# Technology Tree\n\n");
        output.push_str("Code distribution by programming language:\n\n");
        output.push_str("```\n");

        let total_loc = stats.summary.total_loc;

        let mut languages: Vec<(&String, &LanguageStats)> =
            stats.summary.languages.iter().collect();
        languages.sort_by(|a, b| b.1.loc.cmp(&a.1.loc));

        for (lang, stats) in languages.into_iter().take(15) {
            let percentage = stats.percentage;
            let bar = self.render_bar(percentage);

            output.push_str(&format!(
                "{:6} LOC │{}{} {} ({} files)\n",
                stats.loc,
                bar,
                " ".repeat(3),
                lang,
                stats.files
            ));
        }

        output.push_str("```\n");
        output
    }

    /// Generate Mermaid pie chart for technology distribution.
    pub fn generate_mermaid_pie(&self, stats: &CodeStats) -> String {
        let mut output = String::new();
        output.push_str("## Technology Distribution\n\n");
        output.push_str("```mermaid\n");
        output.push_str("pie showData title Code by Language\n");

        let mut languages: Vec<(&String, &LanguageStats)> =
            stats.summary.languages.iter().collect();
        languages.sort_by(|a, b| b.1.loc.cmp(&a.1.loc));

        for (lang, stats) in languages.into_iter().take(10) {
            output.push_str(&format!(
                "    \"{} ({})\" : {}\n",
                lang,
                stats.loc,
                stats.loc
            ));
        }

        output.push_str("```\n");
        output
    }

    /// Generate a feature tree (inferred from directory structure).
    pub fn generate_feature_tree(&self, stats: &CodeStats) -> String {
        let mut output = String::new();
        output.push_str("# Feature Tree\n\n");
        output.push_str("Features inferred from directory structure:\n\n");
        output.push_str("```mermaid\n");
        output.push_str("graph TD\n");

        // Extract top-level directories as features
        let mut features: std::collections::HashSet<String> = std::collections::HashSet::new();
        for file in &stats.files {
            let parts: Vec<&str> = file.path.split('/').collect();
            if let Some(feature) = parts.first() {
                if !feature.is_empty() && !feature.starts_with('.') {
                    features.insert(feature.to_string());
                }
            }
        }

        output.push_str("    subgraph \"Features\"\n");
        for feature in features.iter().take(20) {
            let safe_name = feature.replace('-', "_").replace(' ', "_");
            output.push_str(&format!(
                "        F_{}[📦 {}]\n",
                safe_name,
                feature
            ));
        }
        output.push_str("    end\n");
        output.push_str("```\n");

        // Add table
        output.push_str("\n## Feature Breakdown\n\n");
        output.push_str("| Feature | Files | LOC | Top Files |\n");
        output.push_str("|---------|-------|-----|----------|\n");

        for feature in features.iter().take(15) {
            let dir_stats = stats.by_directory.get(feature);
            let files = dir_stats.map(|d| d.total_files).unwrap_or(0);
            let loc = dir_stats.map(|d| d.total_loc).unwrap_or(0);

            let top_files: Vec<String> = dir_stats
                .map(|d| {
                    let mut files = d.files.clone();
                    files.sort_by(|a, b| b.loc.cmp(&a.loc));
                    files.into_iter()
                        .take(3)
                        .map(|f| f.path.split('/').last().unwrap_or(&f.path).to_string())
                        .collect()
                })
                .unwrap_or_default();

            output.push_str(&format!(
                "| {} | {} | {} | {} |\n",
                feature,
                files,
                loc,
                top_files.join(", ")
            ));
        }

        output
    }

    fn render_bar(&self, percentage: f64) -> String {
        if !self.config.show_bars {
            return String::new();
        }

        let filled = ((percentage / 100.0) * self.config.bar_width as f64).round() as usize;
        let filled = filled.min(self.config.bar_width);
        "█".repeat(filled)
    }
}

impl Default for TreeGenerator {
    fn default() -> Self {
        Self::new(TreeConfig::default())
    }
}
