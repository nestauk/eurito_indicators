<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import Download from '@svizzle/ui/src/icons/feather/Download.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';
	import Methodology from 'app/components/content/Methodology.svx';

	import {toolName} from 'app/config';
	import {zipUrl} from 'app/utils/assets';
	import theme from 'app/theme';
</script>

<svelte:head>
	<title>Methodology - {toolName}</title>
	<meta
		content='{toolName}: methodology used to produce these indicators'
		name='description'
	>
</svelte:head>

<main class={$_screen?.classes}>
	<div>
		<Methodology/>

		<div class='cta'>
			<LinkButton
				download
				glyph={Download}
				href={zipUrl}
				text='Download all indicators'
				theme={{backgroundColor: theme.colorLink}}
			/>
			<LinkButton
				href='/guides'
				text='Read the guides'
				theme={{backgroundColor: theme.colorLink}}
			/>
			<LinkButton
				href='/indicators'
				text='Explore the indicators'
				theme={{backgroundColor: theme.colorLink}}
			/>
		</div>
	</div>
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

	div {
		background-color: white;
		box-shadow: var(--box-shadow-y);
		max-width: 900px;
		overflow-y: auto;
		padding: 2rem;
	}

	.cta {
		display: flex;
		justify-content: space-around;
		margin: 4rem 0 3rem 0;
		flex-direction: column;
		row-gap: 1em;
	}

	:global(.medium) .cta {
		flex-direction: row;
		row-gap: 0;
	}
</style>
