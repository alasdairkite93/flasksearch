const puppeteer = require('puppeteer-extra')
const {executablePath} = require('puppeteer')
var fs = require('fs')

// add stealth plugin and use defaults (all evasion techniques)
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
puppeteer.use(StealthPlugin())

// puppeteer usage as normal
function scrapeUrl(url, prox) {
    console.log("Scrape url: "+url)

    puppeteer.launch({
        headless: true, executablePath: executablePath(), args: [prox]
    }).then(async browser => {


        console.log('Running tests..')
        const page = await browser.newPage()
        await page.goto(url);

        let bodyHTML = await page.evaluate(() => document.documentElement.outerHTML);


        fs.writeFile('temp.txt', (bodyHTML), (err) => {
            if (err) throw err;
        })


        await page.waitForTimeout(5000)
        await browser.close()
    });
}

function readFile(){

    var text = fs.readFileSync("./proxies.txt").toString('utf-8');
    let list = text.split('\n');
    let l_length = list.length;
    let rand_ind = Math.floor(Math.random() * l_length);
    let rand_prox = list[rand_ind];
    let ar_var = '--proxy-server='+rand_prox;

    var url = fs.readFileSync("./urls.txt");
    console.log("going to: "+url+" ar_var: "+ar_var);

    scrapeUrl(url.toString(), ar_var);
}

readFile()