#!/usr/bin/env node

const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
}

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

function runCommand(command, description) {
  log(`\n${colors.bright}${description}${colors.reset}`)
  log(`${colors.cyan}Running: ${command}${colors.reset}`)
  
  try {
    const output = execSync(command, { 
      stdio: 'inherit',
      cwd: process.cwd()
    })
    log(`${colors.green}✅ ${description} completed successfully${colors.reset}`)
    return true
  } catch (error) {
    log(`${colors.red}❌ ${description} failed${colors.reset}`)
    log(`${colors.red}Error: ${error.message}${colors.reset}`)
    return false
  }
}

function generateReport(results) {
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: Object.keys(results).length,
      passed: Object.values(results).filter(r => r).length,
      failed: Object.values(results).filter(r => !r).length
    },
    results
  }
  
  const reportPath = path.join(process.cwd(), 'test-results', 'comprehensive-test-report.json')
  fs.mkdirSync(path.dirname(reportPath), { recursive: true })
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2))
  
  log(`\n${colors.bright}📊 Test Report Generated:${colors.reset}`)
  log(`${colors.cyan}Report saved to: ${reportPath}${colors.reset}`)
  
  // Generate HTML report
  const htmlReport = generateHTMLReport(report)
  const htmlPath = path.join(process.cwd(), 'test-results', 'comprehensive-test-report.html')
  fs.writeFileSync(htmlPath, htmlReport)
  
  log(`${colors.cyan}HTML report saved to: ${htmlPath}${colors.reset}`)
}

function generateHTMLReport(report) {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Test Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 2.5em; font-weight: 300; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; background: #f8f9fa; }
        .summary-card { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .summary-card h3 { margin: 0 0 10px 0; color: #666; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
        .summary-card .number { font-size: 2.5em; font-weight: bold; margin: 0; }
        .summary-card.passed .number { color: #28a745; }
        .summary-card.failed .number { color: #dc3545; }
        .summary-card.total .number { color: #007bff; }
        .results { padding: 30px; }
        .result-item { display: flex; align-items: center; padding: 15px; margin: 10px 0; border-radius: 8px; background: #f8f9fa; }
        .result-item.passed { background: #d4edda; border-left: 4px solid #28a745; }
        .result-item.failed { background: #f8d7da; border-left: 4px solid #dc3545; }
        .result-icon { font-size: 1.5em; margin-right: 15px; }
        .result-icon.passed { color: #28a745; }
        .result-icon.failed { color: #dc3545; }
        .result-details h4 { margin: 0 0 5px 0; font-size: 1.1em; }
        .result-details p { margin: 0; color: #666; font-size: 0.9em; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; border-top: 1px solid #dee2e6; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Comprehensive Test Report</h1>
            <p>Generated on ${new Date(report.timestamp).toLocaleString()}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card total">
                <h3>Total Tests</h3>
                <div class="number">${report.summary.total}</div>
            </div>
            <div class="summary-card passed">
                <h3>Passed</h3>
                <div class="number">${report.summary.passed}</div>
            </div>
            <div class="summary-card failed">
                <h3>Failed</h3>
                <div class="number">${report.summary.failed}</div>
            </div>
        </div>
        
        <div class="results">
            <h2>Test Results</h2>
            ${Object.entries(report.results).map(([test, passed]) => `
                <div class="result-item ${passed ? 'passed' : 'failed'}">
                    <div class="result-icon ${passed ? 'passed' : 'failed'}">
                        ${passed ? '✅' : '❌'}
                    </div>
                    <div class="result-details">
                        <h4>${test}</h4>
                        <p>${passed ? 'Test completed successfully' : 'Test failed'}</p>
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div class="footer">
            <p>BytePort Frontend Testing Suite</p>
        </div>
    </div>
</body>
</html>
  `
}

async function runComprehensiveTests() {
  log(`${colors.bright}🚀 Starting Comprehensive Frontend Testing Suite${colors.reset}`)
  log(`${colors.cyan}This will run all tests: Unit, E2E, Performance, Accessibility, and Visual Regression${colors.reset}`)
  
  const results = {}
  
  // Unit Tests (currently disabled due to React 19 compatibility issues)
  log(`\n${colors.yellow}⚠️  Unit tests are currently disabled due to React 19 compatibility issues${colors.reset}`)
  log(`${colors.yellow}   This will be addressed in a future update${colors.reset}`)
  results['Unit Tests'] = false
  
  // E2E Tests
  results['E2E Tests'] = runCommand(
    'pnpm test:e2e',
    'Running E2E Tests with Playwright'
  )
  
  // Performance Tests
  results['Performance Tests'] = runCommand(
    'node performance/lighthouse-ci.js',
    'Running Performance Tests with Lighthouse CI'
  )
  
  // Accessibility Tests
  results['Accessibility Tests'] = runCommand(
    'pnpm test:e2e --grep "Accessibility"',
    'Running Accessibility Tests with axe-core'
  )
  
  // Visual Regression Tests
  results['Visual Regression Tests'] = runCommand(
    'pnpm test:e2e --grep "Visual Regression"',
    'Running Visual Regression Tests'
  )
  
  // Generate comprehensive report
  generateReport(results)
  
  // Summary
  const passed = Object.values(results).filter(r => r).length
  const total = Object.keys(results).length
  
  log(`\n${colors.bright}📊 Test Summary:${colors.reset}`)
  log(`${colors.green}✅ Passed: ${passed}/${total}${colors.reset}`)
  log(`${colors.red}❌ Failed: ${total - passed}/${total}${colors.reset}`)
  
  if (passed === total) {
    log(`\n${colors.green}🎉 All tests passed! Your frontend is ready for production.${colors.reset}`)
    process.exit(0)
  } else {
    log(`\n${colors.red}⚠️  Some tests failed. Please review the results and fix the issues.${colors.reset}`)
    process.exit(1)
  }
}

// Handle command line arguments
const args = process.argv.slice(2)
if (args.includes('--help') || args.includes('-h')) {
  log(`${colors.bright}Comprehensive Frontend Test Runner${colors.reset}`)
  log(`${colors.cyan}Usage: node scripts/test-runner.js [options]${colors.reset}`)
  log(`\n${colors.bright}Options:${colors.reset}`)
  log(`  --help, -h     Show this help message`)
  log(`  --unit         Run only unit tests`)
  log(`  --e2e          Run only E2E tests`)
  log(`  --performance  Run only performance tests`)
  log(`  --accessibility Run only accessibility tests`)
  log(`  --visual       Run only visual regression tests`)
  log(`\n${colors.bright}Examples:${colors.reset}`)
  log(`  node scripts/test-runner.js                    # Run all tests`)
  log(`  node scripts/test-runner.js --e2e             # Run only E2E tests`)
  log(`  node scripts/test-runner.js --performance     # Run only performance tests`)
} else {
  runComprehensiveTests().catch(error => {
    log(`${colors.red}❌ Test runner failed: ${error.message}${colors.reset}`)
    process.exit(1)
  })
}