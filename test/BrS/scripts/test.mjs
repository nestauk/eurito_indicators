import fs from 'fs';
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
	os: Object.keys(browserstack.operatingSystems),
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
		consoleLogs: 'errors',
		// local: true,
	}
}));

console.log('Configurations:', s4caps.length);

const browserstackURL = `https://${username}:${key}@${url}`;

const results = [];

function buildHeader (capabilities) {
	const logHeader = [];
	const isMobile = Boolean(capabilities.device);
	logHeader.push(capabilities.device || capabilities['bstack:options'].os);
	if (isMobile) {
		logHeader.push(capabilities.deviceOrientation);
	} else {
		logHeader.push(capabilities['bstack:options'].osVersion);
		logHeader.push(capabilities.resolution);
	}
	logHeader.push(capabilities.browserName);
	logHeader.push(capabilities.browserVersion);
	return logHeader.join('-');
}
function log (capabilities, message) {
	console.log(buildHeader(capabilities), message);
}
function err (capabilities, error) {
	console.error(buildHeader(capabilities), error)
}

function fail (driver, message) {
	// TODO notify faliure
}

async function run (capabilities) {
	let driver;
	try {
		driver = await new webdriver.Builder()
		.usingServer(browserstackURL)
		.withCapabilities(capabilities)
		.build();

		// test1
		log(capabilities, 'Navigating...');
		await driver.get(
			'https://deploy-preview-15--eurito-indicators-ui-dev.netlify.app/guide'
		);
		log(capabilities, "Sleeping #1...");
		await driver.sleep(10);
		log(capabilities, "Searching for element...");
		await driver.wait(
			until.elementLocated(By.id('info')),
			20,
			'Element not found.',
			10
		);
		const info = await driver.findElement(By.id('info'));
		log(capabilities, "Sleeping #2...");
		await driver.sleep(10);
		if (!info) {
			log(capabilities, 'Element not found.');
			fail('Element not found.');
			results.push({
				capabilities,
				error: 'Element not found',
			})
		} else {
			log(capabilities, 'Found element. Getting text content...');
			const result = JSON.parse(await info.getText());
			log(capabilities, 'Content:', result);
			results.push({
				capabilities,
				result,
			});
		}
	} catch (e) {
		results.push({
			capabilities,
			exception: e,
			trace: e.stack
		});
		err(capabilities, e);
	} finally {
		driver && driver.quit();
	}
}

function run2 (capabilities) {
	log(capabilities, 'test')
}
const queue = new Queue({
	concurrent: 5,
	interval: 20000
});
queue.on("end", () =>
	fs.writeFile('report.json', JSON.stringify(results, null, 2), () => {
		console.log('Done!');
	})
);
s4caps.forEach(caps => {
	if (caps.device) {
		queue.enqueue(() => run({
			...caps,
			deviceOrientation: 'portrait'
		}));
		queue.enqueue(() => run({
			...caps,
			deviceOrientation: 'landscape'
		}));
	} else {
		const {os} = caps['bstack:options'];
		const versions = browserstack.operatingSystems[os];
		Object.keys(versions).forEach(version => {
			const resolutions = versions[version];
			resolutions.forEach(resolution => {
				queue.enqueue(() => run({
					...caps,
					resolution,
					'bstack:options': {
						...caps['bstack:options'],
						osVersion: version
					}
				}));
			});
		});
		queue.enqueue(() => run(caps));
	}
});


