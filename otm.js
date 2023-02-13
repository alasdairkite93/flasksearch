const puppeteer = require('puppeteer-extra')
const {executablePath} = require('puppeteer')
var fs = require('fs')

// add stealth plugin and use defaults (all evasion techniques)
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
puppeteer.use(StealthPlugin())


// puppeteer usage as normal

function scrapeUrl(url) {
    console.log("puppeteer using: "+url);

    puppeteer.launch({
        headless: true, executablePath: executablePath(),
    }).then(async browser => {
        console.log('Running tests..')
        const page = await browser.newPage()
        await page.goto(url);

        const script = await page.evaluate(() => window.__OTM__.jsonData);

        fs.writeFile('file.json', JSON.stringify(script), (err) => {
            if (err) throw err;
        })

        //add scraping in here


        await page.waitForTimeout(5000)
        await browser.close()
    });
}

function readFile(){
    var text = fs.readFileSync("./urls.txt");
    scrapeUrl(text.toString());
}

readFile();