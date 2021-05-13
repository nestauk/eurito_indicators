<script>
	import {onMount} from 'svelte';
	import * as _ from 'lamb';
	import Bowser from 'bowser';

	import {getTest, groupTests, testResultsURL} from 'app/utils/tests';

	let environment;
	let testResults = null

	async function loadResults() {
		const response = await fetch(testResultsURL);
		const allTests = await response.json();
		const indexedResults = groupTests(allTests);
		testResults = getTest(indexedResults, environment);
	}

	onMount(() => {
		environment = Bowser.parse(window.navigator.userAgent);
		loadResults();
	})
</script>

<svelte:head>
	<title>EURITO CSVs - Accessibility</title>
</svelte:head>

<main>
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
		<pre>{JSON.stringify(testResults, null, 2)}</pre>
	</section>
</main>

<style>
	main {
		background-color: var(--color-background);
		display: flex;
		font-size: 1.05rem;
		font-weight: 200;
		height: 100%;
		justify-content: space-around;
		width: 100%;
	}

	section {
		background-color: white;
		box-shadow: var(--box-shadow-y);
		max-width: 900px;
		overflow-y: auto;
		padding: 2rem;
	}

	h1 {
		font-weight: bold;
	}
	h2 {
		font-weight: normal;
		margin-bottom: 1.5rem;
		margin-top: 1.5rem;
	}
</style>
