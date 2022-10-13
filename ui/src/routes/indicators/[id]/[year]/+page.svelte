<script>
	import * as _ from 'lamb';
	import IdYear from '@svizzle/time_region_value/src/routes/[id]/[year].svelte';

	/* local deps */

	import {toolName} from '$lib/config';
	import types from '$lib/data/types';
	import {_lookup} from '$lib/stores/data';
	import {_availableYears, _selectedYear} from '$lib/stores/selection';

	/* props */

	export let data;

	/* local vars */

	let availableYears;
	let title;

	/* reactive vars */

	$: json = data.data;
	$: year = data.year;
	$: id = data.id;
	$: $_selectedYear = Number(year);
	$: ({availableYears, title} = $_lookup[id] || {});
	$: $_availableYears = availableYears;
</script>

<svelte:head>
	<title>{title} ({year}) - {toolName}</title>
	<meta
		content='{toolName}: geographic distribution (NUTS2 regions) of the indicator: {title} ({year})'
		name='description'
	>
</svelte:head>

<IdYear
	data={json}
	{id}
	{types}
	{year}
/>
