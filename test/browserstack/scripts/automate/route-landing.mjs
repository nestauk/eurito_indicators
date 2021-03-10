import * as _ from 'lamb';

const routes = [
	'/',
	'/guide',
	'/methodology',
	'/font-test'
];

export default async ({driver, target, log}) => {
	const results = {};
	/* eslint-disable no-await-in-loop */
	for (const route of routes) {
		log('Navigating...');
		await driver.get(target + route);
		log("Retrieving document title");
		const title = await driver.getTitle();
		log(title);

		// log("Retrieving page timings");
		// const timings = await driver.executeScript(() => window.performance.navigation.timing);
		// log(timings);

		results[route] = title;
	}

	/*
	const testPromises = routes.map(async route => {
	});
	const pairs = await Promise.all(testPromises)
	const results = _.fromPairs(pairs);
	*/
	log(results);
	return results;
}
