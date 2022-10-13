<script>
	import Layout from '@svizzle/time_region_value/src/routes/_layout.svelte';

	import {page as _page} from '$app/stores';
	import {flags, hrefBase, regionSettings} from '$lib/config';
	import {_groups} from '$lib/stores/data';
	import theme from '$lib/theme';

	$: [,,segment] = $_page.url.pathname.split('/');
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
