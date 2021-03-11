// Retrieves capabilities listing from Browserstack using latest version of
// its REST API: https://github.com/browserstack/api

import fetch from 'node-fetch';
import config from '../.config.mjs';

const {username, key} = config.browserstack;
const url = 'api.browserstack.com/5/browsers';
const browserstackURL = `https://${username}:${key}@${url}`;
console.log(browserstackURL);

async function run () {
	const response = await fetch(browserstackURL);
	const capabilities = await response.json();
	console.log(capabilities);

	const unique = new Set();
	capabilities.forEach(element => {
		unique.add(`${element.os}-${element.browser}-${element.device}`);
	});

	console.log(unique);
}

run();


