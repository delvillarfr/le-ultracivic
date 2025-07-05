const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function compareScreenshots() {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    // Set viewport to match the original image dimensions
    await page.setViewport({ width: 800, height: 1200 });
    
    // Navigate to the local HTML file
    const htmlPath = path.join(__dirname, 'index.html');
    await page.goto(`file://${htmlPath}`);
    
    // Wait for images to load
    await page.waitForTimeout(2000);
    
    // Take screenshot
    const screenshot = await page.screenshot({ fullPage: true });
    
    // Save screenshot
    fs.writeFileSync('current-screenshot.png', screenshot);
    
    console.log('Screenshot saved as current-screenshot.png');
    
    // Compare with original mockup
    const originalPath = path.join(__dirname, 'media', 'mockup.png');
    if (fs.existsSync(originalPath)) {
        console.log('Original mockup found. Please compare manually or use image comparison tool.');
        console.log('Original: media/mockup.png');
        console.log('Current: current-screenshot.png');
        
        // You can add image comparison library here like pixelmatch
        // For now, we'll just log the comparison
        console.log('Manual comparison required to achieve < 6% difference.');
    } else {
        console.log('Original mockup not found at media/mockup.png');
    }
    
    await browser.close();
}

// Run if called directly
if (require.main === module) {
    compareScreenshots().catch(console.error);
}

module.exports = compareScreenshots;