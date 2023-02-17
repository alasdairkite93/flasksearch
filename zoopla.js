const puppeteer = require('puppeteer-extra')
const {executablePath} = require('puppeteer')
var fs = require('fs')

// add stealth plugin and use defaults (all evasion techniques)
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
puppeteer.use(StealthPlugin())

var text = fs.readFileSync("./static/urls.txt").toString('utf-8');
let list = text.split('\n');
let url = list[0];
let prox = list[1]
let ar_var = '--proxy-server='+prox;

console.log("going to: "+url+" ar_var: "+ar_var);

puppeteer.launch({
headless: true, executablePath: executablePath(), args: [prox], ignoreHTTPSErrors: true,
}).then(async browser => {


console.log('Running tests..')
const page = await browser.newPage()
await page.goto(url, {
    waitUntil: "load", timeout: 0,
});
await page.content();



innerText = await page.evaluate(() => {
    console.log(JSON.parse(document.querySelector('#__NEXT_DATA__').innerHTML));
    return JSON.parse(document.querySelector('#__NEXT_DATA__').innerHTML);
});


fs.writeFile('zoopla.json', JSON.stringify(innerText), (err) => {
    if (err) throw err;
})


await page.waitForTimeout(5000)
await browser.close()
});
