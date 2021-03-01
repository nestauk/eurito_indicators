// https://www.browserstack.com/docs/automate/api-reference/selenium/browser#get-browser-list
import fetch from 'node-fetch';
import config from '../.config.mjs';
const browsers = [
	'opera',
	'chrome',
	'ie',
	'firefox',
	'edge',
	'safari',
	'iphone',
	'ipad',
	'android'
];

const devices = [
	'iPhone XS',
	'iPhone 12 Pro Max',
	'iPhone 12 Pro',
	'iPhone 12 Mini',
	'iPhone 12',
	'iPhone 11 Pro Max',
	'iPhone 11',
	'iPad Air 4',
	'iPad Pro 12.9 2020',
	'iPad 8th',
	'iPhone 11 Pro',
	'iPhone 8',
	'iPhone SE 2020',
	'iPad Pro 12.9 2018',
	'iPad Pro 11 2020',
	'iPad Mini 2019',
	'iPad Air 2019',
	'iPad 7th',
	'iPhone XS Max',
	'iPhone XR',
	'iPhone 8 Plus',
	'iPhone 7',
	'iPhone 6S',
	'iPad Pro 11 2018',
	'iPhone X',
	'iPhone 6S Plus',
	'iPhone 6',
	'iPhone SE',
	'iPad Pro 9.7 2016',
	'iPad Pro 12.9 2017',
	'iPad Mini 4',
	'iPad 6th',
	'iPad 5th',
	'iPhone 7 Plus',
	'Samsung Galaxy S20',
	'Google Pixel 5',
	'Google Pixel 4',
	'Samsung Galaxy S20 Plus',
	'Samsung Galaxy S20 Ultra',
	'Samsung Galaxy Note 20 Ultra',
	'Samsung Galaxy Note 20',
	'Samsung Galaxy A51',
	'Samsung Galaxy A11',
	'Google Pixel 4 XL',
	'Google Pixel 3',
	'OnePlus 8',
	'OnePlus 7T',
	'Vivo Y50',
	'Oppo Reno 3 Pro',
	'Samsung Galaxy Tab S7',
	'Samsung Galaxy S9 Plus',
	'Samsung Galaxy S8 Plus',
	'Samsung Galaxy S10e',
	'Samsung Galaxy S10 Plus',
	'Samsung Galaxy S10',
	'Samsung Galaxy Note 10 Plus',
	'Samsung Galaxy Note 10',
	'Samsung Galaxy A10',
	'Google Pixel 3a XL',
	'Google Pixel 3a',
	'Google Pixel 3 XL',
	'Google Pixel 2',
	'Motorola Moto G7 Play',
	'OnePlus 7',
	'OnePlus 6T',
	'Xiaomi Redmi Note 8',
	'Xiaomi Redmi Note 7',
	'Samsung Galaxy Tab S6',
	'Samsung Galaxy Tab S5e',
	'Samsung Galaxy Note 9',
	'Samsung Galaxy J7 Prime',
	'Samsung Galaxy Tab S4',
	'Samsung Galaxy S9',
	'Google Pixel',
	'Samsung Galaxy Note 8',
	'Samsung Galaxy A8',
	'Samsung Galaxy S8',
	'Samsung Galaxy Tab S3',
	'Samsung Galaxy S7',
	'Google Nexus 6',
	'Motorola Moto X 2nd Gen',
	'Samsung Galaxy S6',
	'Samsung Galaxy Note 4',
	'Google Nexus 5',
	'Samsung Galaxy Tab 4'
]

const OSs = ['Windows', 'OS X', 'ios', 'android'];

const {username, key} = config.browserstack;
const url = 'api.browserstack.com/5/browsers';
const browserstackURL = `https://${username}:${key}@${url}`;
console.log(browserstackURL);

async function run () {
	const response = await fetch(browserstackURL);
	const capabilities = await response.json();
	console.log(capabilities);

	/*
	const unique = new Set();
	capabilities.forEach(element => {
		unique.add(`${element.os}-${element.browser}-${element.device}`);
	});

	console.log(unique);
	*/
}

run();


