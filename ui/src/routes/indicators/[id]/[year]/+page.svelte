<script context='module'>
	import {parseCSV} from '@svizzle/time_region_value/src/lib/utils/domain';

	import {lookup} from '$lib/data/groups';

	export function preload ({params: {id, year}}) {
		return this.fetch(lookup[id].url)
			.then(r => r.text())
			.then(parseCSV(id))
			.then(data => ({data, id, year}))
	}
</script>

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
	export let id;
	export let year;

	/* local vars */

	let availableYears;
	let title;

	/* reactive vars */

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
	{data}
	{id}
	{types}
	{year}
/>
