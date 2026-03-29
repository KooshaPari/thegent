const { startServer, stopServer } = require('@lhci/cli/src/server.js')
const { runLighthouse } = require('@lhci/cli/src/collect/lighthouse.js')

async function runPerformanceTests() {
  console.log('🚀 Starting performance tests...')
  
  const server = await startServer({
    port: 3000,
    staticDistDir: './out'
  })
  
  try {
    const urls = [
      'http://localhost:3000',
      'http://localhost:3000/dashboard',
      'http://localhost:3000/deployments',
      'http://localhost:3000/settings'
    ]
    
    const results = []
    
    for (const url of urls) {
      console.log(`📊 Testing ${url}...`)
      
      const result = await runLighthouse(url, {
        chromeFlags: ['--headless', '--no-sandbox'],
        config: {
          extends: 'lighthouse:default',
          settings: {
            onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
            throttling: {
              rttMs: 40,
              throughputKbps: 10240,
              cpuSlowdownMultiplier: 1
            }
          }
        }
      })
      
      results.push({
        url,
        performance: result.lhr.categories.performance.score * 100,
        accessibility: result.lhr.categories.accessibility.score * 100,
        bestPractices: result.lhr.categories['best-practices'].score * 100,
        seo: result.lhr.categories.seo.score * 100,
        metrics: {
          firstContentfulPaint: result.lhr.audits['first-contentful-paint'].numericValue,
          largestContentfulPaint: result.lhr.audits['largest-contentful-paint'].numericValue,
          cumulativeLayoutShift: result.lhr.audits['cumulative-layout-shift'].numericValue,
          totalBlockingTime: result.lhr.audits['total-blocking-time'].numericValue,
          speedIndex: result.lhr.audits['speed-index'].numericValue
        }
      })
    }
    
    // Generate report
    console.log('\n📈 Performance Test Results:')
    console.log('=' .repeat(80))
    
    results.forEach(result => {
      console.log(`\n🌐 ${result.url}`)
      console.log(`   Performance: ${result.performance.toFixed(1)}%`)
      console.log(`   Accessibility: ${result.accessibility.toFixed(1)}%`)
      console.log(`   Best Practices: ${result.bestPractices.toFixed(1)}%`)
      console.log(`   SEO: ${result.seo.toFixed(1)}%`)
      console.log(`   FCP: ${result.metrics.firstContentfulPaint.toFixed(0)}ms`)
      console.log(`   LCP: ${result.metrics.largestContentfulPaint.toFixed(0)}ms`)
      console.log(`   CLS: ${result.metrics.cumulativeLayoutShift.toFixed(3)}`)
      console.log(`   TBT: ${result.metrics.totalBlockingTime.toFixed(0)}ms`)
      console.log(`   SI: ${result.metrics.speedIndex.toFixed(0)}ms`)
    })
    
    // Check thresholds
    const thresholds = {
      performance: 90,
      accessibility: 95,
      bestPractices: 90,
      seo: 85,
      fcp: 2000,
      lcp: 2500,
      cls: 0.1,
      tbt: 300,
      si: 3000
    }
    
    let allPassed = true
    
    results.forEach(result => {
      if (result.performance < thresholds.performance) {
        console.log(`❌ Performance threshold failed: ${result.performance.toFixed(1)}% < ${thresholds.performance}%`)
        allPassed = false
      }
      if (result.accessibility < thresholds.accessibility) {
        console.log(`❌ Accessibility threshold failed: ${result.accessibility.toFixed(1)}% < ${thresholds.accessibility}%`)
        allPassed = false
      }
      if (result.bestPractices < thresholds.bestPractices) {
        console.log(`❌ Best Practices threshold failed: ${result.bestPractices.toFixed(1)}% < ${thresholds.bestPractices}%`)
        allPassed = false
      }
      if (result.seo < thresholds.seo) {
        console.log(`❌ SEO threshold failed: ${result.seo.toFixed(1)}% < ${thresholds.seo}%`)
        allPassed = false
      }
      if (result.metrics.firstContentfulPaint > thresholds.fcp) {
        console.log(`❌ FCP threshold failed: ${result.metrics.firstContentfulPaint.toFixed(0)}ms > ${thresholds.fcp}ms`)
        allPassed = false
      }
      if (result.metrics.largestContentfulPaint > thresholds.lcp) {
        console.log(`❌ LCP threshold failed: ${result.metrics.largestContentfulPaint.toFixed(0)}ms > ${thresholds.lcp}ms`)
        allPassed = false
      }
      if (result.metrics.cumulativeLayoutShift > thresholds.cls) {
        console.log(`❌ CLS threshold failed: ${result.metrics.cumulativeLayoutShift.toFixed(3)} > ${thresholds.cls}`)
        allPassed = false
      }
      if (result.metrics.totalBlockingTime > thresholds.tbt) {
        console.log(`❌ TBT threshold failed: ${result.metrics.totalBlockingTime.toFixed(0)}ms > ${thresholds.tbt}ms`)
        allPassed = false
      }
      if (result.metrics.speedIndex > thresholds.si) {
        console.log(`❌ SI threshold failed: ${result.metrics.speedIndex.toFixed(0)}ms > ${thresholds.si}ms`)
        allPassed = false
      }
    })
    
    if (allPassed) {
      console.log('\n✅ All performance thresholds passed!')
    } else {
      console.log('\n❌ Some performance thresholds failed!')
      process.exit(1)
    }
    
  } finally {
    await stopServer(server)
  }
}

if (require.main === module) {
  runPerformanceTests().catch(console.error)
}

module.exports = { runPerformanceTests }