export default {
	browserstack: {
		username: "your username",
		key: "your key",
		url: "hub-cloud.browserstack.com/wd/hub",
		tests: 'test/browserstack/scripts/automate',
		target: 'https://deploy-preview-21--eurito-indicators-ui-dev.netlify.app',
		report: 'test/selenium-report.json'
	}
}
