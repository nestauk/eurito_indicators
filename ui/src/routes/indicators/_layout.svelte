<script>
	import Layout from '@svizzle/time_region_value/src/routes/_layout.svelte';

	import {_groups} from 'app/stores/data';
	import {goTo} from 'app/utils/sapper';

	export let segment;
</script>

<Layout
	{goTo}
	{segment}
	groupsStore={_groups}
	hrefBase='indicators'
>
	<slot></slot>
</Layout>
