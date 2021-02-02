<script>
	import Layout from '@svizzle/time_region_value/src/routes/_layout.svelte';

	import {groupsStore} from 'app/stores/data';
	import {goTo} from 'app/utils/sapper';

	export let segment;
</script>

<Layout
	{goTo}
	{groupsStore}
	{segment}
	hrefBase='indicators'
>
	<slot></slot>
</Layout>
