import {capitalize} from '@svizzle/utils';

import Queue from "queue-promise";
import Caps from 'browserstack-capabilities';
import webdriver from 'selenium-webdriver';
import config from '../.config.mjs';
import * as browserstack from './browserstack.mjs';

const {until, By} = webdriver;

const {
	username,
	key,
	url
} = config.browserstack;

const bsCapabilities = Caps(username, key);
const devicesCaps = bsCapabilities.create([{
	os: browserstack.oSystems,
	browser: browserstack.browsers,
	browser_version: ['current']
}, {
	device: browserstack.devices,
	browser: browserstack.browsers,
	browser_version: ['current']
}]);

// convert to Selenium 4 format
const s4caps = devicesCaps.map(deviceCaps => ({
	device: deviceCaps.device,
	browserName: capitalize(deviceCaps.browser),
	browserVersion: deviceCaps.browser_version,
	'bstack:options': {
		os: deviceCaps.os,
		osVersion: deviceCaps.os_version,
		// local: true,
	}
}));

// console.log(s4caps.length)

const browserstackURL = `https://${username}:${key}@${url}`;

const results = [];

function log (capabilities, message) {
	console.log(
		capabilities.device || capabilities['bstack:options'].os,
		capabilities.browserName,
		message
	);
}
function fail (driver, message) {
	// TODO notify faliure
}

async function run (capabilities) {
	const driver = new webdriver.Builder()
	.usingServer(browserstackURL)
	.withCapabilities(capabilities)
	.build();

	// test1
	log(capabilities, 'Navigating...');
	await driver.get(
		'https://deploy-preview-15--eurito-indicators-ui-dev.netlify.app/guide'
	);
	log(capabilities, "Sleeping...");
	await driver.sleep(10);
	log(capabilities, "Searching for element...");
	await driver.wait(
		until.elementLocated(By.id('info')),
		20,
		'Element not found.',
		10
	);
	const info = await driver.findElement(By.id('info'));
	if (!info) {
		log(capabilities, 'Element not found.');
		fail('Element not found.');
	} else {
		log(capabilities, 'Found element. Getting text content...');
		const result = JSON.parse(await info.getText());
		log(capabilities, 'Content:', result);
		results.push({
			capabilities,
			result,
		})
	}
	driver.quit();
}

const queue = new Queue({
	concurrent: 5,
	interval: 20000
});
s4caps.forEach(caps => {
	queue.enqueue(() => run({
			...caps,
			deviceOrientation: 'portrait'
		})
	);
	queue.enqueue(() => run({
			...caps,
			deviceOrientation: 'landscape'
		})
	);
});
