import webdriver from 'selenium-webdriver';
import config from '../.config.mjs';

const USERNAME = config.browserstack.username;
const AUTOMATE_KEY = config.browserstack.key;
const URL = config.browserstack.url;

let browserstackURL = `https://${USERNAME}:${AUTOMATE_KEY}@${URL}`;

let capabilities = {
	os : 'Windows',
	os_version : '10',
	browserName : 'Chrome',
	browser_version : '80',
	name : "sebastianferreyr1's First Test"
}

let driver = new webdriver.Builder()
.usingServer(browserstackURL)
.withCapabilities(capabilities)
.build();

async function run () {
	await driver.get('http://www.google.com');
	await driver.findElement(webdriver.By.name('q')).sendKeys('BrowserStack');
    const title = await driver.getTitle();
	console.log(title);
	driver.quit();
}

run();
