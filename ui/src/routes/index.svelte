<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import Link from '@svizzle/ui/src/Link.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';

	import {toolName} from 'app/config';
	import theme from 'app/theme';

	const repoUrl = 'https://github.com/nestauk/eurito_indicators_ui';

	const linkTheme = {
		color: theme.colorLink,
		iconStroke: theme.colorLink
	};
</script>

<svelte:head>
	<title>EURITO - Home</title>
	<meta
		content='{toolName}: homepage'
		name='description'
	>
</svelte:head>

<main class={$_screen?.classes}>
	<section>
		<h1>EURITO indicators</h1>

		<h2>Intro</h2>
		<p>
			We have created an 
			<Link
				href={repoUrl}
				isBold={true}
				isExternal={true}
				theme={linkTheme}
			>
				open repository
			</Link>
			of indicators TODO: complete.
		</p>
		<p>
			We have also built a tool to
			<Link
				href='indicators'
				isBold={true}
				isUnderlined={true}
				theme={linkTheme}
			>
				visualise and explore
			</Link>
			these indicators TODO: complete.
		</p>

		<h2>The framework</h2>
		<p>Our indicators are arranged in four broad categories.</p>

		<h3>Public R&D Capability</h3>
		<p>
			Measuring the quantity and excellence of R&D activity taking place
			in higher education institutions in a region.
		</p>

		<h3>Business R&D Capability</h3>
		<p>
			Measuring the level of R&D activity and innovative outputs in the
			private sector in a region.
		</p>

		<h3>Knowledge exchange</h3>
		<p>
			Measuring the connectivity between higher education institutions in
			a region and the wider economy.
		</p>

		<h3>Place potential</h3>
		<p>
			Measuring wider infrastructures and framework conditions in a region
			that might drive - or hinder - its innovative performance.
		</p>

		<div class='cta'>
			<LinkButton
				href='/methodology'
				text='Read more about the methodology'
				theme={{backgroundColor: theme.colorLink}}
			/>
			<LinkButton
				href='/indicators'
				text='Explore the indicators'
				theme={{backgroundColor: theme.colorLink}}
			/>
		</div>
	</section>
</main>

<style>
	main {
		background-color: var(--color-background);
		display: flex;
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
	h3 {
		font-weight: normal;
		margin-top: 1.5rem;
	}

	p {
		margin-bottom: 1.5rem;
	}

	.cta {
		align-content: center;
		display: flex;
		flex-direction: column;
		justify-content: space-around;
		margin: 4rem 0 3rem 0;
		row-gap: 1em;
	}

	.large .cta {
		flex-direction: row;
		row-gap: 0;
	}
</style>
