<script>
	import {onMount} from 'svelte';
	import * as _ from 'lamb';
	import {isNotNil} from '@svizzle/utils';
	import Bowser from 'bowser';
	import {_screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
		
	import ChevronLeft from '@svizzle/ui/src/icons/feather/ChevronLeft.svelte';
	import ChevronRight from '@svizzle/ui/src/icons/feather/ChevronRight.svelte';
	import Icon from '@svizzle/ui/src/icons/Icon.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';
	import LoadingView from '@svizzle/ui/src/LoadingView.svelte';

	import {getTest, groupTests, testResultsURL} from 'app/utils/tests';
	import {failingA11yAudit, lighthouseUrls, toolName} from 'app/config';
	import theme from 'app/theme';

	const wcag21Url = 'https://www.w3.org/TR/WCAG21/';
	const openDyslexicUrl = 'https://opendyslexic.org/';
	const windowsMouseURL = 'https://support.microsoft.com/en-us/windows/change-mouse-settings-e81356a4-0e74-fe38-7d01-9d79fbf8712b';
	const osxMouseURL = 'https://support.apple.com/guide/mac-help/change-cursor-preferences-for-accessibility-mchl5bb12e1e/mac';
	const screenReadersUrl = 'https://en.wikipedia.org/wiki/List_of_screen_readers';
	const lighthouseIssueUrl = 'https://github.com/GoogleChrome/lighthouse/issues/12039';

	const reportNames = _.keys(lighthouseUrls)

	let environment;
	let testResults = null;
	let lighthouseFrame;
	let currentreport = reportNames[0];
	let loadingResults = false;

	async function loadResults() {
		loadingResults = true
		const response = await fetch(testResultsURL);
		const allTests = await response.json();
		const indexedResults = groupTests(allTests);
		testResults = getTest(indexedResults, environment);
	}

	function resizeIFrameToFitContent( iFrame ) {
		loadingResults = false
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

	const updateCurrentReport = id => currentreport = id;
	$: currentValueIndex = _.findIndex(
		reportNames,
		_.is(currentreport)
	);
	$: prevValue = reportNames[currentValueIndex - 1];
	$: nextValue = reportNames[currentValueIndex + 1];
	$: hasPrevValue = isNotNil(prevValue);
	$: hasNextValue = isNotNil(nextValue);
	$: clickedPrev =
		() => hasPrevValue && updateCurrentReport(prevValue);
	$: clickedNext =
		() => hasNextValue && updateCurrentReport(nextValue);
	$: reportUrl = `/a11y/${currentreport}.html`;

</script>

<svelte:head>
	<title>EURITO - Accessibility</title>
	<meta
		name='description'
		content='All about accessibility in {toolName}, including a guide on how to enable the accessibility dialog, accessibility audit and other quality audits, plus some pointers to setup various accessibility tools on your system'
	>
</svelte:head>

<main class={$_screen?.classes}>
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
		<h2>Support</h2>
		<p>
			To meet these requirements, we follow the recomendations of the
			<a href={wcag21Url} rel='noopener'>WCAG 2.1</a> guidelines when
			building our platform and websites. With this guidance in mind, we:
		</p>
		<ul>
			<li>
				<p>
					Ensure that the choices of color provide sufficient
					contrast for comfortable reading.
				</p>
			</li>
			<li>
				<p>
					Offer a selection of typefaces for improved legibility,
					including one widely believed to improve comprehension among
					people with 
					<a href={openDyslexicUrl} rel='noopener'>Dyslexia</a>.
				</p>
			</li>
			<li>
				<p>
					Wherever it's possible, enhance the semantic meta 
					information of each page to improve the reach of tools such
					as screen readers.
				</p>
			</li>
			<li>
				<p>
					We regularly measure our site using a variety of methods,
					such as third-party automated and manual audits across a 
					range of different browsers and devices. You can review some
					of those results in the reports presented below.
				</p>
			</li>
		</ul>
		<h2>Limitations</h2>
		<p>
			Although we continually revise the website for proper support, we
			recognize that some pages may present occasional accessibility
			problems. Also, just as technology improves and standards evolve,
			our work is also never done and we continually strive to achieve the
			highest levels of compliance with the requirements and
			recommendations.
		</p>
		<p>
			While we aim to make the information provided as accessible as
			possible, this website consists mostly of data presented as
			interactive graphic charts and are not organized in a way that's
			easy for a screen reader to present. However, the data is available
			for <a href='/download'>download in CSV format</a>.
		</p>
		<h2>Feedback</h2>
		<p>
			If you see any errors or have other suggestions on how we
			can further improve the accessibility of our site,
			please contact us at 
			<a href="mailto:dataanalytics@nesta.org.uk">
				dataanalytics@nesta.org.uk
			</a>.
		</p>

		<h2>Resources</h2>
		<h3>Using a screen reader</h3>
		<p>
			If you need a screen reader and have not installed one already, you
			may choose one from this <a href={screenReadersUrl} rel='noopener'>
			comprehensive list of screen readers</a>.
		</p>
		<h3>How to customize the mouse pointer</h3>
		<p>
			You can customize a computer mouse pointer in several ways. For
			example, you can slow down the speed of the mouse pointer for easier
			handling. You can also change its appearance so that it contrasts
			more with the screen content.
		</p>

		<div class='cta'>
			<LinkButton
				href={windowsMouseURL}
				text='Windows'
				theme={{backgroundColor: theme.colorMain}}
			/>
			<LinkButton
				href={osxMouseURL}
				text='OS X'
				theme={{backgroundColor: theme.colorMain}}
			/>
		</div>

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
			{#if $_screen?.sizeFlags?.medium}
				<ul>
					{#each reportNames as id}
						<li>
							<input
								{id}
								type='radio'
								bind:group={currentreport}
								value={id}
							>
							<label for={id} class='clickable'>{id}</label>
						</li>
					{/each}
				</ul>
			{:else}
				<div>
					<label for=''>{currentreport}</label>
					<button
						class:clickable={hasPrevValue}
						disabled={!hasPrevValue}
						on:click={clickedPrev}
					>
						<Icon glyph={ChevronLeft} />
					</button>
					<button
						class:clickable={hasNextValue}
						disabled={!hasNextValue}
						on:click={clickedNext}
					>
						<Icon glyph={ChevronRight} />
					</button>
				</div>
			{/if}
		</menu>
		{#if failingA11yAudit.includes(currentreport)}
			<figure>
				Unfortunately the accessibility audit for this page fails
				because of an
				<a
					href={lighthouseIssueUrl}
					rel='noopener'
				>
					issue
				</a> in Google Lighthouse.
			</figure>
		{/if}
		{#if loadingResults}
			<LoadingView stroke={theme.colorMain}/>
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
	.tabs input[type="radio"] + label, .tabs div label {
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

	.tabs div {
		border: thin solid var(--color-main);
		display: grid;
		grid-template-columns: 1fr min-content min-content;
	}
	.tabs button {
		background: white;
		border: none;
		border-left: thin solid var(--color-main);
		height: 2.5rem;
		width: 2.5rem;
	}
	.cta {
		display: flex;
		justify-content: space-around;
		margin: 4rem 0 3rem 0;
		flex-direction: column;
		row-gap: 1em;
	}
	.medium .cta {
		flex-direction: row;
		row-gap: 0;
	}
</style>
