import fs from 'fs';
import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';

import {lighthouseUrls} from '../../src/node_modules/app/config';

(async () => {
	for (let [id, url] of Object.entries(lighthouseUrls)) {
		const chrome = await chromeLauncher.launch({
			chromeFlags: [
				'--headless',
				// '--no-sandbox',  // uncomment if there are problems running the tests
			]
		});
		const options = {
			logLevel: 'info',
			output: 'html',
			onlyCategories: ['accessibility'],
			port: chrome.port
		};
		const runnerResult = await lighthouse(url, options);
		const reportHtml = runnerResult.report;	

		// eslint-disable-next-line no-sync
		fs.writeFileSync(`static/a11y/${id}.html`, reportHtml);

		// `.lhr` is the Lighthouse Result as a JS object
		console.log('Report is done for', runnerResult.lhr.finalUrl);
		console.log('Performance score was', runnerResult.lhr.categories.accessibility.score * 100);

		await chrome.kill();
	}
})();
