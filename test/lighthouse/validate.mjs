import fs from 'fs';
import lighthouse from 'lighthouse';
import chromeLauncher from 'chrome-launcher';

(async () => {
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
	const runnerResult = await lighthouse('http://localhost:3000', options);

	// `.report` is the HTML report as a string
	const reportHtml = runnerResult.report;

	// eslint-disable-next-line no-sync
	fs.writeFileSync('static/lhreport.html', reportHtml);

	// `.lhr` is the Lighthouse Result as a JS object
	console.log('Report is done for', runnerResult.lhr.finalUrl);
	console.log('Performance score was', runnerResult.lhr.categories.performance.score * 100);

	await chrome.kill();
})();
