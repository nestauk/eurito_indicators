<script>
	import Index from '@svizzle/time_region_value/src/routes/index.svelte';

	import {_groups, _yearRange} from 'app/stores/data';
	import {goTo} from 'app/utils/sapper';
</script>

<svelte:head>
	<title>EURITO CSVs - Timelines</title>
</svelte:head>

<Index
	{goTo}
	groupsStore={_groups}
	yearRangeStore={_yearRange}
	hrefBase='indicators'
/>
