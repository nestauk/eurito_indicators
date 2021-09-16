<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import IndicatorsMedium from '../_content/guides/IndicatorsMedium.svx';
	import IndicatorsSmall from '../_content/guides/IndicatorsSmall.svx';

	import {toolName} from '$lib/config';
</script>

<svelte:head>
	<title>Indicators guide - {toolName}</title>
	<meta
		content='{toolName}: how to explore the indicators'
		name='description'
	/>
</svelte:head>

<div>
	{#if $_screen?.sizes.medium}
		<IndicatorsMedium />
	{:else}
		<IndicatorsSmall />
	{/if}
</div>

<style>
	div {
		background-color: white;
		max-width: 900px;
		overflow-y: auto;
	}
</style>
