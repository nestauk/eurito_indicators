import fs from 'fs';
import lighthouse from 'lighthouse';
import chromeLauncher from 'chrome-launcher';

const urls = {
	home: 'http://localhost:3000',
	guide: 'http://localhost:3000/guide',
	methodology: 'http://localhost:3000/methodology',
	// indicators1: 'http://localhost:3000/indicators/',
	// indicators2: '',
	// indicators3: '',
}

const publicReports = [
	'guide',
	'indicators1',
];

(async () => {
	for (let [id, url] of Object.entries(urls)) {
		const chrome = await chromeLauncher.launch({
			chromeFlags: [
				// '--headless',
				'--no-sandbox',
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
		fs.writeFileSync(`static/lighthouse/${id}.html`, reportHtml);

		// `.lhr` is the Lighthouse Result as a JS object
		console.log('Report is done for', runnerResult.lhr.finalUrl);
		console.log('Performance score was', runnerResult.lhr.categories.accessibility.score * 100);

		await chrome.kill();
	}
})();
