<script>
	import {onMount} from 'svelte';
	import * as _ from 'lamb';
	import Bowser from "bowser";
	import {screenGauge} from 'app/components/ScreenGauge.svelte';

	const testResultsURL = 'https://gist.githubusercontent.com/NestaTestUser/8fb890ee1ebf84435539faa7996b140e/raw/Browserstack%20test%20results%20for%20Eurito%20Indicators%20webapp';
	let environment;
	let testResults;
	let indexedResults;
	let thisPlatform = null

	const getOS = _.getPath('capabilities.bstack:options.os');
	const getVersion = _.getPath('capabilities.bstack:options.osVersion');
	const getBrowser = _.getPath('capabilities.browserName');
	const getBrowserV = _.getPath('capabilities.browserVersion');
	const groupTests = _.pipe([
		_.groupBy(getOS),
		_.mapValuesWith(_.pipe([
			_.groupBy(getVersion),
			_.mapValuesWith(_.pipe([
				_.groupBy(getBrowser),
				_.mapValuesWith(_.pipe([
					_.groupBy(getBrowserV),
				])),
			])),
		])),
	]);

	const osMap = {
		'Windows': 'Windows',
		'macOS': 'OS X'
	};
	const browserMap = {
		'Microsoft Edge': 'Edge',
		'Chrome': 'Chrome',
		'Safari': 'Safari',
		'Firefox': 'Firefox'
	};

	const getTest = env => {
		const os = osMap[env.os.name];
		const osVersion = env.os.versionName;
		const browser = browserMap[env.browser.name];
		const browserVersion = env.browser.version.split('.').slice(0,2).join('.');
		thisPlatform = indexedResults[os][osVersion][browser][browserVersion];
	};

	async function loadResults() {
		const response = await fetch(testResultsURL);
		testResults = await response.json();
		indexedResults = groupTests(testResults);
		getTest(environment);
		console.log(testResults);
	}

	onMount(() => {
		environment = Bowser.parse(window.navigator.userAgent);
		console.log(environment);
		loadResults();
	})
</script>

<svelte:head>
	<title>EURITO CSVs - Accessibility Statement</title>
</svelte:head>

<main class={$screenGauge?.classes}>
	<section>
		<h1>Accessibility</h1>

		<p>(TODO Foreword and other text...)</p>

		<h2>Environment</h2>
		<dl>
			<dt>Platform</dt>
			<dd>{environment?.platform.type}</dd>
			<dt>Operating System</dt>
			<dd>{environment?.os.name} - {environment?.os.versionName}</dd>
			<dt>Browser</dt>
			<dd>{environment?.browser.name} - {environment?.browser.version}</dd>
			<dt>Engine</dt>
			<dd>{environment?.engine.name} - {environment?.engine.version || ''}</dd>
		</dl>

		<h2>Compatibility Testing Results</h2>
		<pre>{JSON.stringify(thisPlatform, null, 2)}</pre>
	</section>
</main>

<style>
	main {
		height: 100%;
		width: 100%;
		display: flex;
		justify-content: space-around;

		font-size: 1.05rem;
		font-weight: 200;
		background-color: var(--color-background);
	}

	section {
		max-width: 900px;
		padding: 2rem;
		overflow-y: auto;
		background-color: white;
		box-shadow: var(--box-shadow-y);
	}

	h1 {
		font-family: 'Open Sans Semibold', sans-serif;
	}
	h2 {
		margin-bottom: 1.5rem;
		margin-top: 1.5rem;
		font-family: 'Open Sans Regular', sans-serif;
	}
	h3 {
		margin-top: 1.5rem;
		font-family: 'Open Sans Regular', sans-serif;
	}

	p, ul {
		line-height: 2rem;
	}

	a {
		text-decoration: none;
		font-weight: bold;
	}

	p a {
		padding: 0.1rem;
		border-bottom: 1px solid var(--color-link);
		color: var(--color-link);
		text-decoration: none;
		font-weight: bold;
	}
</style>
