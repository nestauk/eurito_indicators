<script>
	import Layout from '@svizzle/time_region_value/src/routes/_layout.svelte';

	import {flags, hrefBase, regionSettings} from 'app/config';
	import {_groups} from 'app/stores/data';
	import theme from 'app/theme';

	export let segment;
</script>

<Layout
	{_groups}
	{flags}
	{hrefBase}
	{regionSettings}
	{segment}
	{theme}
>
	<slot />
</Layout>
