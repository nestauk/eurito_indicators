import {capitalize} from '@svizzle/utils';

import browserstack from 'browserstack-local';
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

const browserstackURL = `https://${username}:${key}@${url}`;

const builder = new webdriver.Builder();

async function run (capabilities) {
	try {
		let driver = builder
		.usingServer(browserstackURL)
		.withCapabilities(capabilities)
		.build();

		await driver.get('http://localhost:3000/font-test');
		const info = await driver.findElement({id:'info'});
		const text = await info.getText();
		console.log(text);
		driver.quit();
	}
	catch (e) {
		console.log(e);
	}
}

try {
	console.log('starting...');
	const bs_local = new browserstack.Local();
	const bs_local_args = {
		key,
		forceLocal: 'true'
	};

	console.log('starting 2...');
	bs_local.start(bs_local_args, () => {
		console.log('Started BrowserStackLocal')
		console.log('Local tunnel running: ', bs_local.isRunning());
		try {
			s4caps.forEach(run);
		} catch (e) {
			console.log(e);
		}

		bs_local.stop(() => {
			console.log('Stopped BrowserStackLocal');
		});
	});
} catch (e) {
	console.error(e);
}
