const puppeteer = require('puppeteer-extra')
const {executablePath} = require('puppeteer')
var fs = require('fs')

// add stealth plugin and use defaults (all evasion techniques)
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
puppeteer.use(StealthPlugin())


var text = fs.readFileSync('/home/alasdairkite/flasksearch/urls.txt').toString('utf-8');
let list = text.split('\n');
let url = list[0];
let prox = list[1]
let ar_var = '--proxy-server=' + prox;

const proxy = prox;
const username = 'woaokexr';
const password = '6tq2q8b4e15q';

console.log(url);
// puppeteer usage as normal
puppeteer.launch({
    headless: true, ignoreHTTPSErrors: true, executablePath: executablePath(), args: [ar_var]
}).then(async browser => {

    const page = await browser.newPage()
    await page.setExtraHTTPHeaders({
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'upgrade-insecure-requests': '1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,en;q=0.8'
    });
    await page.authenticate({username, password});
    await page.goto(url);
    await page.content();

    innerText = await page.evaluate(() => {
        return document.documentElement.outerHTML;
    });

    console.log("javascript running: ");

    console.log(innerText);

    fs.writeFile('/home/alasdairkite/flasksearch/temp.txt', (innerText), (err) => {
        if (err) throw err;
    })


    await page.waitForTimeout(5000)
    await browser.close()

});
