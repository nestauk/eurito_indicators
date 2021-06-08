<script>
	import {onMount} from 'svelte';
	import * as _ from 'lamb';
	import Bowser from 'bowser';

	import {getTest, groupTests, testResultsURL} from 'app/utils/tests';
	import {failingA11yAudit, lighthouseUrls, toolName} from 'app/config';

	const wcag21Url = 'https://www.w3.org/TR/WCAG21/';

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
	<meta
		name='description'
		content='All about accessibility in {toolName}, including a guide on how to enable the accessibility dialog, accessibility audit and other quality audits, plus some pointers to setup various accessibility tools on your system'
	>
</svelte:head>

<main>
	<section>
		<h1>Accessibility</h1>

		<p>
			Ensuring greater access to technologies by meeting the needs of
			people with disabilities lays the foundation for inclusive work
			cultures that empower individuals and teams to thrive.
		</p>
		<p>
			Therefore, {toolName} is committed to making its best effort towards
			continually improving the accessibility of all the information
			provided in this website. 
		</p>
		<p>
			To meet these requirements, we follow the recomendations of the
			<a href={wcag21Url}>WCAG 2.1</a> guidelines when building our
			platform and websites. With this guidance in mind, we:
		</p>
		<ul>
			<li>
				<p>
					We ensure that the choices of color provide sufficient
					contrast for comfortable reading.
				</p>
			</li>
			<li>
				<p>
					Wherever it's possible, we enhance the semantic meta 
					information of each page to improve the reach of tools such
					as screen readers, (DEV NOTE: Mybe this point should be
					added only after we're done with the ARIA PR)
				</p>
			</li>
			<li>
				<p>
					We regularly measure our site using a variety of methods,
					such as third-party automated and manual audits across a 
					range of different browsers and devices. You can review some
					of those results in the Lighthouse reports presented below.
				</p>
			</li>
		</ul>
		<p>
			Although we continually revise the website for proper support, we
			recognize that some pages may present occasional accessibility
			problems. Also, just as technology improves and standards evolve,
			our work is also never done and we continually strive to achieve the
			highest levels of compliance with the requirements and
			recommendations.
		</p>
		<p>
			If you see any errors or have other suggestions on how we
			can further improve the accessibility of our site,
			please contact us at CHANGE@nestauk.org.
		</p>
		
		<h2>Detected Browsing Environment</h2>
		<dl>
			<dt>Platform</dt>
			<dd>{environment?.platform?.type}</dd>
			<dt>Operating System</dt>
			<dd>
				{environment?.os?.name}
				{#if environment?.os?.versionName}
					- {environment.os.versionName}
				{/if}
			</dd>
			<dt>Browser</dt>
			<dd>
				{environment?.browser.name}
				{#if environment?.browser?.version}
					- {environment.browser.version}
				{/if}
			</dd>
			<dt>Engine</dt>
			<dd>
				{environment?.engine.name}
				{#if environment?.engine?.version}
					- {environment.engine.version}
				{/if}
			</dd>
		</dl>

		{#if testResults}
			<p>
				This browsing environment has been tested and is supported.
			</p>
		{:else}
			<p>
				This browsing environment is untested and user experience may
				vary.
			</p>
		{/if}

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
				Unfortunately the accessibility audit for this page fails
				because of an
				<a
					href='https://github.com/GoogleChrome/lighthouse/issues/12039'
					rel='noopener'
				>
					issue
				</a> in Google Lighthouse.
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
	h1 {
		font-weight: bold;
	}
	h2 {
		font-weight: normal;
		margin-bottom: 1.5rem;
		margin-top: 1.5rem;
	}
	p {
		margin-bottom: 1.5rem;
	}
	a {
		text-decoration: none;
		font-weight: bold;
	}
	p a {
		border-bottom: 1px solid var(--color-link);
		color: var(--color-link);
		font-weight: bold;
		padding: 0.1rem;
		text-decoration: none;
	}
	ul {
		list-style: initial;
		margin-left: 20px;
	}
	dl {
		display: grid;
		grid-template-rows: repeat(4, auto);
    	grid-template-columns: repeat(2, minmax(min-content, max-content));
	}
	dt {
		padding: 0.5em 1em;
		border-top: thin solid white;
		color: white;
		background: var(--color-main);
		text-align: right;
	}
	dt:first-child {
		border-top: none;
	}
	dd {
		border: thin solid var(--color-main);
		padding: 0.5em 1em;
	}
	dd:not(:last-child) {
		border-bottom: none;
	}
	.tabs ul {
		border-bottom: thin solid var(--color-main);
		display: flex;
		flex-direction: row;
		list-style-type: none;
		margin: 0;
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
