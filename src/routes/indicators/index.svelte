<script>
	import Index from '@svizzle/time_region_value/src/routes/index.svelte';

	import {groupsStore, yearRangeStore} from 'app/stores/data';
	import {goTo} from 'app/utils/sapper';
</script>

<svelte:head>
	<title>EURITO CSVs - Timelines</title>
</svelte:head>

<Index
	{goTo}
	{groupsStore}
	{yearRangeStore}
	hrefBase='indicators'
/>
