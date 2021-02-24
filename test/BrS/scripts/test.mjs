import webdriver from 'selenium-webdriver';
import config from '../.config.mjs';

const {
	username,
	key,
	url
} = config.browserstack;

let browserstackURL = `https://${username}:${key}@${url}`;

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
