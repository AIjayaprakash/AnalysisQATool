// JavaScript/Node.js example for testing /execute-from-excel endpoint
// Install: npm install axios form-data

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_URL = 'http://localhost:8000/execute-from-excel';
const EXCEL_FILE = 'test_cases.xlsx';

// Example 1: Basic usage
async function example1_basicUsage() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 1: Basic Usage (First Test Case, Chromium)');
    console.log('='.repeat(70));

    const formData = new FormData();
    formData.append('file', fs.createReadStream(EXCEL_FILE));

    try {
        const response = await axios.post(API_URL, formData, {
            headers: formData.getHeaders()
        });

        console.log('✅ Success!');
        console.log(`📄 Pages extracted: ${response.data.pages.length}`);
        console.log(`🔗 Edges extracted: ${response.data.edges.length}`);

        // Print page details
        response.data.pages.forEach(page => {
            console.log(`\n  Page: ${page.label}`);
            console.log(`  URL: ${page.metadata.url}`);
            console.log(`  Elements: ${page.metadata.key_elements.length}`);
        });
    } catch (error) {
        console.error('❌ Error:', error.response?.status || error.message);
        console.error(error.response?.data || error.message);
    }
}

// Example 2: Specific test case with Edge browser
async function example2_specificTestCase() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 2: Specific Test Case with Edge Browser');
    console.log('='.repeat(70));

    const formData = new FormData();
    formData.append('file', fs.createReadStream(EXCEL_FILE));
    formData.append('sheet_name', 'Sheet1');
    formData.append('test_id', 'TC_LOGIN_001');
    formData.append('browser_type', 'edge');
    formData.append('headless', 'false');
    formData.append('max_iterations', '10');

    try {
        const response = await axios.post(API_URL, formData, {
            headers: formData.getHeaders()
        });

        console.log('✅ Success!');
        console.log(`📄 Pages extracted: ${response.data.pages.length}`);
        console.log(`🔗 Edges extracted: ${response.data.edges.length}`);

        // Detailed page information
        response.data.pages.forEach((page, i) => {
            console.log(`\n  Page ${i + 1}: ${page.label}`);
            console.log(`  ID: ${page.id}`);
            console.log(`  URL: ${page.metadata.url}`);
            console.log(`  Title: ${page.metadata.title}`);
            console.log(`  Elements: ${page.metadata.key_elements.length}`);

            // Print first 3 elements
            page.metadata.key_elements.slice(0, 3).forEach(elem => {
                console.log(`    - ${elem.type}: ${elem.text || elem.tag}`);
            });
        });

        // Print edges
        if (response.data.edges.length > 0) {
            console.log(`\n  Navigation Flow:`);
            response.data.edges.forEach(edge => {
                console.log(`    ${edge.source} → ${edge.target}: ${edge.label}`);
            });
        }
    } catch (error) {
        console.error('❌ Error:', error.response?.status || error.message);
        console.error(error.response?.data || error.message);
    }
}

// Example 3: Firefox headless mode
async function example3_firefoxHeadless() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 3: Firefox Headless Mode');
    console.log('='.repeat(70));

    const formData = new FormData();
    formData.append('file', fs.createReadStream(EXCEL_FILE));
    formData.append('sheet_name', 'Sheet1');
    formData.append('browser_type', 'firefox');
    formData.append('headless', 'true');
    formData.append('max_iterations', '15');

    try {
        const response = await axios.post(API_URL, formData, {
            headers: formData.getHeaders()
        });

        console.log('✅ Success!');
        console.log(`📄 Pages: ${response.data.pages.length}`);
        console.log(`🔗 Edges: ${response.data.edges.length}`);

        // Save to JSON file
        const outputFile = 'automation_results.json';
        fs.writeFileSync(outputFile, JSON.stringify(response.data, null, 2));
        console.log(`💾 Results saved to: ${outputFile}`);
    } catch (error) {
        console.error('❌ Error:', error.response?.status || error.message);
        console.error(error.response?.data || error.message);
    }
}

// Example 4: Test all browsers
async function example4_allBrowsers() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 4: Test with All Browsers');
    console.log('='.repeat(70));

    const browsers = ['chromium', 'firefox', 'webkit', 'edge'];
    const resultsSummary = {};

    for (const browser of browsers) {
        console.log(`\n🔍 Testing with ${browser.toUpperCase()} browser...`);

        const formData = new FormData();
        formData.append('file', fs.createReadStream(EXCEL_FILE));
        formData.append('sheet_name', 'Sheet1');
        formData.append('browser_type', browser);
        formData.append('headless', 'true');
        formData.append('max_iterations', '10');

        try {
            const response = await axios.post(API_URL, formData, {
                headers: formData.getHeaders()
            });

            resultsSummary[browser] = {
                status: '✅ Success',
                pages: response.data.pages.length,
                edges: response.data.edges.length
            };
            console.log(`  ✅ ${browser}: ${response.data.pages.length} pages, ${response.data.edges.length} edges`);
        } catch (error) {
            resultsSummary[browser] = {
                status: `❌ Failed (${error.response?.status || 'Error'})`,
                error: error.message
            };
            console.log(`  ❌ ${browser}: Failed - ${error.response?.status || error.message}`);
        }
    }

    // Print summary
    console.log('\n' + '='.repeat(70));
    console.log('Browser Test Summary:');
    console.log('='.repeat(70));
    Object.entries(resultsSummary).forEach(([browser, result]) => {
        console.log(`${browser.toUpperCase().padEnd(10)} - ${result.status}`);
        if (result.pages !== undefined) {
            console.log(`           Pages: ${result.pages}, Edges: ${result.edges}`);
        }
    });
}

// Example 5: Detailed extraction and analysis
async function example5_detailedExtraction() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 5: Detailed Metadata Extraction');
    console.log('='.repeat(70));

    const formData = new FormData();
    formData.append('file', fs.createReadStream(EXCEL_FILE));
    formData.append('sheet_name', 'Sheet1');
    formData.append('test_id', 'TC_001');
    formData.append('browser_type', 'edge');
    formData.append('headless', 'false');
    formData.append('max_iterations', '10');

    try {
        const response = await axios.post(API_URL, formData, {
            headers: formData.getHeaders()
        });

        console.log('✅ Success!\n');
        console.log(`📄 Total Pages Visited: ${response.data.pages.length}\n`);

        // Analyze pages
        response.data.pages.forEach(page => {
            console.log('━'.repeat(50));
            console.log(`Page ID: ${page.id}`);
            console.log(`Label: ${page.label}`);
            console.log(`URL: ${page.metadata.url}`);
            console.log(`Title: ${page.metadata.title}`);
            console.log(`Position: (x=${page.x}, y=${page.y})`);
            console.log(`\n🎯 Key Elements (${page.metadata.key_elements.length}):`);

            // Group elements by type
            const elementTypes = {};
            page.metadata.key_elements.forEach(elem => {
                if (!elementTypes[elem.type]) {
                    elementTypes[elem.type] = [];
                }
                elementTypes[elem.type].push(elem);
            });

            // Print element summary
            Object.entries(elementTypes).forEach(([type, elements]) => {
                console.log(`  ${type}: ${elements.length} element(s)`);
            });

            // Print detailed element info
            console.log(`\n  Detailed Elements:`);
            page.metadata.key_elements.forEach(elem => {
                console.log(`    • ${elem.id} (${elem.type})`);
                console.log(`      Tag: <${elem.tag}>`);
                if (elem.text) console.log(`      Text: ${elem.text}`);
                if (elem.href) console.log(`      Href: ${elem.href}`);
                if (elem.element_id) console.log(`      ID: ${elem.element_id}`);
                if (elem.class_name) console.log(`      Class: ${elem.class_name}`);
                console.log();
            });
        });

        // Analyze edges
        if (response.data.edges.length > 0) {
            console.log(`\n🔗 Navigation Flow (${response.data.edges.length} transition(s)):\n`);
            response.data.edges.forEach((edge, i) => {
                console.log(`  ${i + 1}. ${edge.source} → ${edge.target}`);
                console.log(`     Action: ${edge.label}\n`);
            });
        }

        // Statistics
        const totalElements = response.data.pages.reduce((sum, page) => 
            sum + page.metadata.key_elements.length, 0);
        
        console.log(`\n📊 Statistics:`);
        console.log(`  Total Pages: ${response.data.pages.length}`);
        console.log(`  Total Elements: ${totalElements}`);
        console.log(`  Total Edges: ${response.data.edges.length}`);
        console.log(`  Avg Elements per Page: ${(totalElements / response.data.pages.length).toFixed(1)}`);
    } catch (error) {
        console.error('❌ Error:', error.response?.status || error.message);
        console.error(error.response?.data || error.message);
    }
}

// Example 6: Error handling
async function example6_errorHandling() {
    console.log('\n' + '='.repeat(70));
    console.log('Example 6: Error Handling');
    console.log('='.repeat(70));

    // Check if file exists
    if (!fs.existsSync(EXCEL_FILE)) {
        console.log(`❌ File not found: ${EXCEL_FILE}`);
        return;
    }

    const formData = new FormData();
    formData.append('file', fs.createReadStream(EXCEL_FILE));
    formData.append('sheet_name', 'Sheet1');
    formData.append('test_id', 'TC_INVALID_999'); // Invalid test ID
    formData.append('browser_type', 'edge');
    formData.append('headless', 'false');
    formData.append('max_iterations', '10');

    try {
        const response = await axios.post(API_URL, formData, {
            headers: formData.getHeaders(),
            timeout: 300000 // 5 minutes
        });

        console.log('✅ Success!');
        console.log(`📄 Pages: ${response.data.pages.length}`);
        console.log(`🔗 Edges: ${response.data.edges.length}`);
    } catch (error) {
        if (error.response) {
            // Server responded with error
            const status = error.response.status;
            if (status === 404) {
                console.log(`❌ Test case not found`);
                console.log(`   Response:`, error.response.data);
            } else if (status === 400) {
                console.log(`❌ Bad request`);
                console.log(`   Response:`, error.response.data);
            } else if (status === 500) {
                console.log(`❌ Server error`);
                console.log(`   Response:`, error.response.data);
            } else {
                console.log(`❌ Unexpected error: ${status}`);
                console.log(error.response.data);
            }
        } else if (error.code === 'ETIMEDOUT') {
            console.log('❌ Request timeout - automation took too long');
        } else if (error.code === 'ECONNREFUSED') {
            console.log('❌ Connection error - is the server running?');
            console.log('   Start server with: python backend/app/llmops_api.py');
        } else {
            console.log(`❌ Unexpected error: ${error.message}`);
        }
    }
}

// Main execution
async function main() {
    console.log('\n' + '🎯'.repeat(35));
    console.log('Execute From Excel - Comprehensive JavaScript Examples');
    console.log('🎯'.repeat(35));
    console.log('\nMake sure:');
    console.log('1. API server is running: python backend/app/llmops_api.py');
    console.log('2. Excel file exists: test_cases.xlsx');
    console.log('3. Browsers are installed: python -m playwright install');
    console.log('4. Dependencies installed: npm install axios form-data');
    console.log('\n');

    try {
        // Run examples (uncomment the ones you want to run)
        await example1_basicUsage();
        // await example2_specificTestCase();
        // await example3_firefoxHeadless();
        // await example4_allBrowsers();
        // await example5_detailedExtraction();
        // await example6_errorHandling();
    } catch (error) {
        console.error(`\n❌ Fatal error: ${error.message}`);
        console.log('\nTroubleshooting:');
        console.log('1. Check if API server is running on http://localhost:8000');
        console.log('2. Verify Excel file path is correct');
        console.log('3. Ensure Playwright browsers are installed');
    }
}

// Run the main function
if (require.main === module) {
    main().catch(console.error);
}

module.exports = {
    example1_basicUsage,
    example2_specificTestCase,
    example3_firefoxHeadless,
    example4_allBrowsers,
    example5_detailedExtraction,
    example6_errorHandling
};
