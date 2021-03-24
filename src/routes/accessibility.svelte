<script>
	import {onMount} from 'svelte';
	import Bowser from "bowser";
	import {screenGauge} from 'app/components/ScreenGauge.svelte';

	let environment;

	onMount(() => {
		environment = Bowser.parse(window.navigator.userAgent);
		console.log(environment);
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
			<dd>{environment?.os.name} {environment?.os.version}</dd>
			<dt>Browser</dt>
			<dd>{environment?.browser.name} {environment?.browser.version}</dd>
			<dt>Engine</dt>
			<dd>{environment?.engine.name} {environment?.engine.version}</dd>
		</dl>

		<h2>Compatibility Testing Results</h2>
		<p>(TODO: Passed/Failed/Unknown)</p>
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
