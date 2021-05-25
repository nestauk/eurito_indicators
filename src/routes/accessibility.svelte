<script>
	import {onMount} from 'svelte';
	import * as _ from 'lamb';
	import Bowser from 'bowser';

	import {toolName} from 'app/config';

	import {getTest, groupTests, testResultsURL} from 'app/utils/tests';
	import {lighthouseUrls, failingA11yAudit} from 'app/config';

	let environment;
	let testResults = null;
	let lighthouseFrame;
	let currentreport = _.keys(lighthouseUrls)[0];

	async function loadResults() {
		const response = await fetch(testResultsURL);
		const allTests = await response.json();
		const indexedResults = groupTests(allTests);
		testResults = getTest(indexedResults, environment);
	}

	function resizeIFrameToFitContent( iFrame ) {
		iFrame.height = iFrame.contentWindow.document.body.scrollHeight;
	}

	onMount(() => {
		lighthouseFrame.contentWindow.addEventListener(
			'load',
			() => resizeIFrameToFitContent( lighthouseFrame )
		);

		environment = Bowser.parse(window.navigator.userAgent);
		loadResults();
	})

	$: reportUrl = `/a11y/${currentreport}.html`;
</script>

<svelte:head>
	<title>EURITO CSVs - Accessibility</title>
	<meta name="description" content={`All about accessibility in ${toolName}, including a guide on how to enable the accessibility dialog, accessibility audit and other quality audits, plus some pointers to setup various accessibility tools on your system`}>
</svelte:head>

<main>
	<section>
		<h1>Accessibility</h1>

		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed eiusmod tempor
			incidunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
			exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat. Quis aute 
			iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla 
			pariatur. Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui 
			officia deserunt mollit anim id est laborum.
		</p>

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

		<h2>Compatibility testing results</h2>
		<pre>{JSON.stringify(testResults, null, 2)}</pre>

		<h2>Quality audits</h2>
		<menu class='tabs'>
			<ul>
				{#each _.keys(lighthouseUrls) as id}
					<li>
						<input {id} type='radio' bind:group={currentreport} value={id}>
						<label for={id} class='clickable'>{id}</label>
					</li>
				{/each}
			</ul>
		</menu>
		{#if failingA11yAudit.includes(currentreport)}
			<figure>
				Unfortunately the accessibility audit for this page fails because of an
				<a href='https://github.com/GoogleChrome/lighthouse/issues/12039'>issue</a>
				in Google Lighthouse.
			</figure>
		{/if}
		<iframe
			bind:this={lighthouseFrame}
			frameborder='0'
			marginheight='0'
			marginwidth='0'
			src={reportUrl}
			title='Accessibility validation results'
		>
			Loading...
		</iframe>
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

	figure {
		background: var(--color-warning-background);
		border: thin solid var(--color-warning-border);
		color: var(--color-warning-text);
		padding: 0.5em 1em;
	}

	iframe {
		width: 100%;
	}

	h1 {
		font-weight: bold;
	}
	h2 {
		font-weight: normal;
		margin-bottom: 1.5rem;
		margin-top: 1.5rem;
	}
	.tabs ul {
		list-style-type: none;
		display: flex;
		flex-direction: row;
		border-bottom: thin solid var(--color-main);
	}
	.tabs input {
		display: none;
	}
	.tabs input[type="radio"] + label {
		display: block;
		padding: 0.5em 1em;
	}
	.tabs li:first-child {
		border-left: thin solid var(--color-main);
	}
	.tabs li {
		border-top: thin solid var(--color-main);
		border-right: thin solid var(--color-main);
	}
	.tabs input[type="radio"]:checked + label {
		background: var(--color-main);
		color: white;
	}
</style>
