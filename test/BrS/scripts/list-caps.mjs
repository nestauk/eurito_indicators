// https://www.browserstack.com/docs/automate/api-reference/selenium/browser#get-browser-list
import Caps from 'browserstack-capabilities';
import config from '../.config.mjs';
import * as browserstack from './browserstack.mjs';

const {username, key} = config.browserstack;
const bsCapabilities = Caps(username, key);

const capabilities = bsCapabilities.create([{
	os: browserstack.oSystems,
	browser: browserstack.browsers,
	browser_version: ['current']
}, {
	device: browserstack.devices,
	browser: browserstack.browsers,
	browser_version: ['current']
}]);

console.log(capabilities);

/*
const unique = new Set();
capabilities.forEach(element => {
	unique.add(`${element.os}-${element.browser}-${element.device}`);
});

console.log(unique);
*/
