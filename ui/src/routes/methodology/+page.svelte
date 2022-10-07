<script>
	import Download from '@svizzle/ui/src/icons/feather/Download.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';
	import ResponsiveFlex from '@svizzle/ui/src/ResponsiveFlex.svelte';
	import {_screen} from '@svizzle/ui/src/sensors/screen/ScreenSensor.svelte';

	import {toolName} from '$lib/config';
	import {zipUrl} from '$lib/utils/assets';
	import theme from '$lib/theme';

	import Methodology from '$lib/_content/Methodology.svx';
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
