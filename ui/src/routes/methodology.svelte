<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import Download from '@svizzle/ui/src/icons/feather/Download.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';
	import Methodology from './_content/Methodology.svx';
	import ResponsiveFlex from 'app/components/ResponsiveFlex.svelte';

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

		<ResponsiveFlex>
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
		</ResponsiveFlex>
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
</style>
