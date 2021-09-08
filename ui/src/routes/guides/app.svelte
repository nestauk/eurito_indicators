<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import AppMedium from './AppMedium.svx';
	import AppSmall from './AppSmall.svx';

	import {toolName} from 'app/config';
</script>

<svelte:head>
	<title>App guide - {toolName}</title>
	<meta
		content='{toolName}: how to use the app'
		name='description'
	>
</svelte:head>

{#if $_screen?.sizes.medium}
	<AppMedium />
{:else}
	<AppSmall />
{/if}
