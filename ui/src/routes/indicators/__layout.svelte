<script>
	import Layout from '@svizzle/time_region_value/src/routes/_layout.svelte';

	import {flags, hrefBase, regionSettings} from '$lib/config';
	import POIs from '$lib/data/majorCities';
	import {_groups} from '$lib/stores/data';
	import theme from '$lib/theme';

	export let segment;
</script>

<Layout
	{_groups}
	{flags}
	{hrefBase}
	{POIs}
	{regionSettings}
	{segment}
	{theme}
>
	<slot></slot>
</Layout>
