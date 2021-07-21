import * as _ from 'lamb';

const routes = [
	'/',
	'/guide',
	'/methodology',
];

export default async ({driver, target, log}) => {
	const results = [];

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

		let isFunctionReady = false;
		let isPageLoaded = false;

		isFunctionReady = await driver.executeScript(
			() => Boolean(window.nesta_isLayoutUndefined)
		);
		if (isFunctionReady) {
			isPageLoaded = await driver.executeScript(
				() => !window.nesta_isLayoutUndefined()
			);
			log(`page loaded: ${isPageLoaded}`);
		} else {
			log('function NOT ready!');
		}

		results.push([route, isPageLoaded]);
	}

	const retVal = {
		passed: _.reduce(results, (p, c) => p && c[1]),
		reasonsForFailure: _.pipe([
			_.filterWith(c => !c[1]),
			_.mapWith(c => c[0]),
		])(results)
	}
	log(retVal);
	return retVal;
}
