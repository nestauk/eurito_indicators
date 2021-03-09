import fs from 'fs/promises';
import {capitalize} from '@svizzle/utils';

import Queue from "queue-promise";
import Caps from 'browserstack-capabilities';
import webdriver from 'selenium-webdriver';
import config from './.config.mjs';
import * as options from './options.mjs';

const {until, By} = webdriver;

const {
	username,
	key,
	url,
	target,
	tests,
	report
} = config.browserstack;

const browserstackURL = `https://${username}:${key}@${url}`;
const optionsKey = 'bstack:options';
const results = [];

// utilities
function buildHeader (capabilities) {
	const logHeader = [];
	const isMobile = Boolean(capabilities.device);
	logHeader.push(capabilities.device || capabilities[optionsKey].os);
	if (isMobile) {
		logHeader.push(capabilities.deviceOrientation);
	} else {
		logHeader.push(capabilities[optionsKey].osVersion);
		logHeader.push(capabilities.resolution);
	}
	logHeader.push(capabilities.browserName);
	logHeader.push(capabilities.browserVersion);
	return logHeader.join('-');
}
function log (capabilities, ...message) {
	console.log(buildHeader(capabilities), ...message);
}
function err (capabilities, error) {
	console.error(buildHeader(capabilities), error)
}

function fail (driver, message) {
	// TODO notify faliure
}

async function run (task, capabilities) {
	let driver;
	try {
		driver = await new webdriver.Builder()
		.usingServer(browserstackURL)
		.withCapabilities(capabilities)
		.build();

		return await task({
			capabilities,
			driver,
			By,
			until,
			target,
			fail: message => fail(driver, message),
			log: message => log(capabilities, message)
		});
	} catch (e) {
		err(capabilities, e);
		return {
			capabilities,
			exception: e,
			trace: e.stack
		};
	} finally {
		driver && driver.quit();
	}
}

// Task runner
// 1. Get filtered capabilities through Browserstack API
const bsCapabilities = Caps(username, key);
const devicesCaps = bsCapabilities.create([{
	os: Object.keys(options.operatingSystems),
	browser: options.browsers,
	browser_version: ['current']
}, {
	device: options.devices,
	browser: options.browsers,
	browser_version: ['current']
}]);

// 2. Convert to Selenium 4 format
const s4caps = devicesCaps.map(deviceCaps => ({
	device: deviceCaps.device,
	browserName: capitalize(deviceCaps.browser),
	browserVersion: deviceCaps.browser_version,
	[optionsKey]: {
		os: deviceCaps.os,
		osVersion: deviceCaps.os_version,
		consoleLogs: 'errors',
		// local: true,
	}
}));

console.log('Configurations:', s4caps.length);

// 3. initialize task runner
const queue = new Queue({
	concurrent: 5,
	interval: 20000
});

queue.on("end", async () =>{
	await fs.writeFile(report, JSON.stringify(results, null, 2));
	console.log('Done!');
});

function runTest (task) {
	s4caps.forEach(caps => {
		const doTest = async extra => results.push(await run(task, {
			...caps,
			...extra
		}));
		if (caps.device) {
			queue.enqueue(doTest({deviceOrientation: 'portrait'}));
			queue.enqueue(doTest({deviceOrientation: 'landscape'}));
		} else {
			const {os} = caps[optionsKey];
			const versions = options.operatingSystems[os];
			Object.keys(versions).forEach(version => {
				const resolutions = versions[version];
				resolutions.forEach(resolution => {
					queue.enqueue(doTest({
						resolution,
						[optionsKey]: {
							...caps[optionsKey],
							osVersion: version
						}
					}));
				});
			});
		}
	});
}

// 4. load and run tests
async function runAll() {
	const files = await fs.readdir(tests);
	// console.log(...files.map(file => `./${file.ab}`));

	// const loading = files.map(file => import(`./${file}`));
	//const modules = await Promise.all(loading);
	// modules.forEach(runTest);
}

runAll();
