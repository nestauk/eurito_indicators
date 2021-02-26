import {capitalize} from '@svizzle/utils';

import Queue from "queue-promise";
import Caps from 'browserstack-capabilities';
import webdriver from 'selenium-webdriver';
import config from '../.config.mjs';

const {
	username,
	key,
	url
} = config.browserstack;

const bsCapabilities = Caps(username, key);
const devicesCaps = bsCapabilities.create();

// convert to Selenium 4 format
const s4caps = devicesCaps.map(deviceCaps => ({
	device: deviceCaps.device,
	browserName: capitalize(deviceCaps.browser),
	browserVersion: deviceCaps.browser_version,
	'bstack:options': {
		os: deviceCaps.os,
		osVersion: deviceCaps.os_version,
		local: true,
	}
}));

console.log(s4caps.length)
/*
const browserstackURL = `https://${username}:${key}@${url}`;

async function run (capabilities) {
	const driver = new webdriver.Builder()
	.usingServer(browserstackURL)
	.withCapabilities(capabilities)
	.build();

	await driver.get('http://localhost:3000/font-test');
	const info = await driver.findElement({id:'info'});
	const text = await info.getText();
	console.log(text);
	driver.quit();
}

const queue = new Queue({
	concurrent: 5,
	interval: 30000
  });
s4caps.forEach(caps => queue.enqueue(() => run(caps)));
*/