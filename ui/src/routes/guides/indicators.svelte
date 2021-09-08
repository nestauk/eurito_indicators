<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import CTA from 'app/components/CTA.svelte';
	import IndicatorsMedium
		from 'app/components/content/guides/IndicatorsMedium.svx';
	import IndicatorsSmall
		from 'app/components/content/guides/IndicatorsSmall.svx';
		import LinkButton from '@svizzle/ui/src/LinkButton.svelte';

	import {toolName} from 'app/config';
	import theme from 'app/theme';

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

	<CTA>
		<LinkButton
			href='/accessibility'
			text='Read the accessibility statement'
			theme={{backgroundColor: theme.colorLink}}
		/>
		<LinkButton
			href='/indicators'
			text='Explore the indicators'
			theme={{backgroundColor: theme.colorLink}}
		/>
	</CTA>
</div>

<style>
	div {
		background-color: white;
		max-width: 900px;
		overflow-y: auto;
		padding: 2rem;
	}
</style>
