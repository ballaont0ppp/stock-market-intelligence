/**
 * Performance Tests for API Endpoints
 * 
 * These tests measure response times under various load conditions
 */

// Mock API endpoints
const apiEndpoints = {
  '/api/users': {
    method: 'GET',
    responseTime: 50, // ms
    successRate: 0.99
  },
  '/api/users/:id': {
    method: 'GET',
    responseTime: 30, // ms
    successRate: 0.995
  },
  '/api/users': {
    method: 'POST',
    responseTime: 100, // ms
    successRate: 0.98
  },
  '/api/orders': {
    method: 'GET',
    responseTime: 75, // ms
    successRate: 0.99
  },
  '/api/orders': {
    method: 'POST',
    responseTime: 150, // ms
    successRate: 0.97
  }
};

// Mock load testing function
async function simulateApiCall(endpoint, config) {
  const endpointConfig = apiEndpoints[endpoint];
  if (!endpointConfig) {
    throw new Error(`Endpoint ${endpoint} not found`);
  }
  
  // Simulate network delay
  const delay = endpointConfig.responseTime * (0.8 + Math.random() * 0.4); // ±20% variance
  await new Promise(resolve => setTimeout(resolve, delay));
  
  // Simulate success/failure based on success rate
  const isSuccess = Math.random() < endpointConfig.successRate;
  
  return {
    endpoint,
    method: endpointConfig.method,
    responseTime: delay,
    status: isSuccess ? 200 : 500,
    timestamp: new Date()
  };
}

// Load test runner
async function runLoadTest(endpoint, concurrentUsers, durationMs) {
  console.log(`Running load test on ${endpoint} with ${concurrentUsers} concurrent users for ${durationMs}ms`);
  
  const results = [];
  const startTime = Date.now();
  const endTime = startTime + durationMs;
  
  // Create concurrent user simulations
  const userPromises = [];
  for (let i = 0; i < concurrentUsers; i++) {
    userPromises.push(simulateUser(endpoint, startTime, endTime, results));
  }
  
  // Wait for all users to finish
  await Promise.all(userPromises);
  
  return analyzeResults(results);
}

async function simulateUser(endpoint, startTime, endTime, results) {
  while (Date.now() < endTime) {
    try {
      const result = await simulateApiCall(endpoint, {});
      results.push(result);
      
      // Random delay between requests (100-500ms)
      const delay = 100 + Math.random() * 400;
      await new Promise(resolve => setTimeout(resolve, delay));
    } catch (error) {
      console.error(`User simulation error: ${error.message}`);
      break;
    }
  }
}

function analyzeResults(results) {
  const totalRequests = results.length;
  const successfulRequests = results.filter(r => r.status === 200).length;
  const failedRequests = totalRequests - successfulRequests;
  
  const responseTimes = results.map(r => r.responseTime);
  const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
  const minResponseTime = Math.min(...responseTimes);
  const maxResponseTime = Math.max(...responseTimes);
  
  const successRate = (successfulRequests / totalRequests) * 100;
  
  return {
    totalRequests,
    successfulRequests,
    failedRequests,
    successRate,
    avgResponseTime,
    minResponseTime,
    maxResponseTime,
    results
  };
}

// Performance test suite
async function runPerformanceTests() {
  console.log('Running API Performance Tests...');
  console.log('===============================');
  
  const testScenarios = [
    {
      name: 'Low Load Test',
      endpoint: '/api/users',
      concurrentUsers: 10,
      duration: 10000 // 10 seconds
    },
    {
      name: 'Medium Load Test',
      endpoint: '/api/users',
      concurrentUsers: 50,
      duration: 15000 // 15 seconds
    },
    {
      name: 'High Load Test',
      endpoint: '/api/users',
      concurrentUsers: 100,
      duration: 20000 // 20 seconds
    }
  ];
  
  for (const scenario of testScenarios) {
    console.log(`\n--- ${scenario.name} ---`);
    
    try {
      const results = await runLoadTest(
        scenario.endpoint,
        scenario.concurrentUsers,
        scenario.duration
      );
      
      console.log(`Total Requests: ${results.totalRequests}`);
      console.log(`Successful Requests: ${results.successfulRequests}`);
      console.log(`Failed Requests: ${results.failedRequests}`);
      console.log(`Success Rate: ${results.successRate.toFixed(2)}%`);
      console.log(`Avg Response Time: ${results.avgResponseTime.toFixed(2)}ms`);
      console.log(`Min Response Time: ${results.minResponseTime.toFixed(2)}ms`);
      console.log(`Max Response Time: ${results.maxResponseTime.toFixed(2)}ms`);
      
      // Performance assertions
      if (results.successRate < 95) {
        console.log(`⚠️  Warning: Success rate below 95% threshold`);
      }
      
      if (results.avgResponseTime > 200) {
        console.log(`⚠️  Warning: Average response time above 200ms threshold`);
      }
    } catch (error) {
      console.log(`✗ ${scenario.name} failed: ${error.message}`);
    }
  }
  
  console.log('\nPerformance Tests Completed!');
}

// Run the tests
if (require.main === module) {
  runPerformanceTests().catch(error => {
    console.error('Performance tests failed with error:', error);
    process.exit(1);
  });
}

module.exports = { runLoadTest, simulateApiCall, runPerformanceTests };