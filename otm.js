const puppeteer = require('puppeteer-extra')
const {executablePath} = require('puppeteer')
var fs = require('fs')

// add stealth plugin and use defaults (all evasion techniques)
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
puppeteer.use(StealthPlugin())


// puppeteer usage as normal

function scrapeUrl(url, proxy) {
    console.log("puppeteer using: "+url);

    puppeteer.launch({
        headless: true, executablePath: executablePath(), args: [proxy]
    }).then(async browser => {
        console.log('Running tests..')
        const page = await browser.newPage()
        await page.goto(url);

        const script = await page.evaluate(() => window.__OTM__.jsonData);
        fs.writeFileSync('./file.json', JSON.stringify(script), (err) => {
            if (err) throw err;
        })


        await page.waitForTimeout(5000)
        await browser.close()
    });
}

function readFile(){
    console.log("read file method")
    var text = fs.readFileSync("./urls.txt");
    console.log(text.toString())
    const vals = text.toString().split(',');
    const url = vals[0].toString();
    console.log("url: "+url);
    const proxy = vals[1].toString();
    console.log("proxy: "+proxy);
    scrapeUrl(url, proxy);
}

readFile();