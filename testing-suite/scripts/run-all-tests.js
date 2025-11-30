#!/usr/bin/env node

/**
 * Test Suite Executor
 * 
 * This script runs all test categories and generates a comprehensive report
 */

const fs = require('fs');
const path = require('path');

// Test categories
const testCategories = [
  { name: 'Smoke Tests', script: 'smoke/scripts/smoke.test.js', required: true },
  { name: 'Unit Tests', script: 'unit/scripts/calculator.test.js', required: true },
  { name: 'Integration Tests', script: 'integration/scripts/user-auth.integration.test.js', required: true },
  { name: 'Performance Tests', script: 'performance/scripts/api-load.test.js', required: false },
  { name: 'Security Tests', script: 'security/scripts/vulnerability.scan.js', required: false },
  { name: 'E2E Tests', script: 'e2e/scripts/user-journey.e2e.test.js', required: false },
  { name: 'Regression Tests', script: 'regression/scripts/api-regression.test.js', required: true },
  { name: 'API Tests', script: 'api/scripts/rest-api.test.js', required: true },
  { name: 'Database Tests', script: 'database/scripts/data-integrity.test.js', required: false },
  { name: 'Configuration Tests', script: 'config/scripts/environment-validation.test.js', required: true },
  { name: 'Accessibility Tests', script: 'accessibility/scripts/wcag-compliance.test.js', required: false },
  { name: 'Chaos Engineering Tests', script: 'chaos/scripts/failure-simulation.test.js', required: false }
];

// Test results storage
const testResults = [];

// Real test runner
async function runTestScript(scriptPath) {
  console.log(`\n--- Running ${scriptPath} ---`);
  
  const startTime = Date.now();
  
  try {
    // Actually run the test script
    const { spawn } = require('child_process');
    const testPath = path.join(__dirname, '..', scriptPath);
    
    return new Promise((resolve) => {
      const child = spawn('node', [testPath], {
        cwd: path.join(__dirname, '..'),
        stdio: 'inherit'
      });
      
      child.on('close', (code) => {
        const executionTime = Date.now() - startTime;
        resolve({
          passed: code === 0,
          executionTime,
          timestamp: new Date()
        });
      });
      
      child.on('error', (error) => {
        const executionTime = Date.now() - startTime;
        resolve({
          passed: false,
          error: error.message,
          executionTime,
          timestamp: new Date()
        });
      });
    });
  } catch (error) {
    const executionTime = Date.now() - startTime;
    return {
      passed: false,
      error: error.message,
      executionTime,
      timestamp: new Date()
    };
  }
}

// Run all tests
async function runAllTests() {
  console.log('Enterprise Testing Suite Executor');
  console.log('=================================');
  console.log(`Starting test execution at ${new Date().toISOString()}\n`);
  
  // Run tests for each category
  for (const category of testCategories) {
    try {
      const result = await runTestScript(category.script);
      testResults.push({
        category: category.name,
        script: category.script,
        required: category.required,
        ...result
      });
      
      if (result.passed) {
        console.log(`✓ ${category.name} PASSED (${result.executionTime}ms)`);
      } else {
        console.log(`✗ ${category.name} FAILED (${result.executionTime}ms)`);
        if (result.error) {
          console.log(`  Error: ${result.error}`);
        }
      }
    } catch (error) {
      const result = {
        passed: false,
        error: error.message,
        executionTime: 0,
        timestamp: new Date()
      };
      
      testResults.push({
        category: category.name,
        script: category.script,
        required: category.required,
        ...result
      });
      
      console.log(`✗ ${category.name} FAILED`);
      console.log(`  Error: ${error.message}`);
    }
  }
  
  // Generate summary report
  generateSummaryReport();
}

// Generate summary report
function generateSummaryReport() {
  console.log('\n' + '='.repeat(50));
  console.log('TEST EXECUTION SUMMARY REPORT');
  console.log('='.repeat(50));
  
  const totalTests = testResults.length;
  const passedTests = testResults.filter(t => t.passed).length;
  const failedTests = totalTests - passedTests;
  const requiredTests = testResults.filter(t => t.required);
  const passedRequired = requiredTests.filter(t => t.passed).length;
  const totalRequired = requiredTests.length;
  
  const passRate = ((passedTests / totalTests) * 100).toFixed(1);
  const requiredPassRate = ((passedRequired / totalRequired) * 100).toFixed(1);
  
  console.log(`Total Tests: ${totalTests}`);
  console.log(`Passed: ${passedTests}`);
  console.log(`Failed: ${failedTests}`);
  console.log(`Overall Pass Rate: ${passRate}%`);
  console.log(`Required Tests Pass Rate: ${requiredPassRate}%`);
  
  console.log('\nDetailed Results:');
  console.log('-'.repeat(30));
  testResults.forEach(result => {
    const status = result.passed ? 'PASSED' : 'FAILED';
    const required = result.required ? '(Required)' : '(Optional)';
    console.log(`${status} ${result.category} ${required} (${result.executionTime}ms)`);
  });
  
  // Check if deployment can proceed
  const canDeploy = passedRequired === totalRequired;
  console.log('\n' + '='.repeat(50));
  console.log('DEPLOYMENT STATUS:');
  if (canDeploy) {
    console.log('✓ READY FOR DEPLOYMENT');
    console.log('All required tests passed');
  } else {
    console.log('✗ DEPLOYMENT BLOCKED');
    console.log(`${totalRequired - passedRequired} required tests failed`);
  }
  console.log('='.repeat(50));
  
  // Save results to file
  saveResultsToFile();
}

// Save results to file
function saveResultsToFile() {
  const resultsDir = path.join(__dirname, '..', 'results');
  if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
  }
  
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      totalTests: testResults.length,
      passedTests: testResults.filter(t => t.passed).length,
      failedTests: testResults.filter(t => !t.passed).length,
      passRate: ((testResults.filter(t => t.passed).length / testResults.length) * 100).toFixed(1)
    },
    details: testResults
  };
  
  const reportPath = path.join(resultsDir, `test-report-${Date.now()}.json`);
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`\nDetailed report saved to: ${reportPath}`);
  
  // Also save as markdown
  const markdownReportPath = path.join(resultsDir, `test-report-${Date.now()}.md`);
  const markdownContent = generateMarkdownReport(report);
  fs.writeFileSync(markdownReportPath, markdownContent);
  console.log(`Markdown report saved to: ${markdownReportPath}`);
}

// Generate markdown report
function generateMarkdownReport(report) {
  let content = `# Test Execution Report\n\n`;
  content += `**Generated:** ${report.timestamp}\n\n`;
  content += `## Summary\n\n`;
  content += `| Metric | Value |\n`;
  content += `|--------|-------|\n`;
  content += `| Total Tests | ${report.summary.totalTests} |\n`;
  content += `| Passed | ${report.summary.passedTests} |\n`;
  content += `| Failed | ${report.summary.failedTests} |\n`;
  content += `| Pass Rate | ${report.summary.passRate}% |\n\n`;
  
  content += `## Detailed Results\n\n`;
  content += `| Test Category | Status | Execution Time | Required |\n`;
  content += `|---------------|--------|----------------|----------|\n`;
  
  report.details.forEach(detail => {
    const status = detail.passed ? '✅ PASSED' : '❌ FAILED';
    const required = detail.required ? 'Yes' : 'No';
    content += `| ${detail.category} | ${status} | ${detail.executionTime}ms | ${required} |\n`;
  });
  
  return content;
}

// Run the test suite
if (require.main === module) {
  runAllTests().catch(error => {
    console.error('Test suite execution failed:', error);
    process.exit(1);
  });
}

module.exports = { runAllTests, testCategories };