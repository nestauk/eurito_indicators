<script context="module">
	import {lookup} from 'app/data/groups';
	import {parseCSV} from 'app/utils/domain';

	export function preload({ params: {id, year}, query }) {
		return this.fetch(lookup[id].url)
			.then(r => r.text())
			.then(parseCSV(id))
			.then(data => ({data, id, year}))
	}
</script>

<script>
	/* ext utils */

	import * as _ from 'lamb';

	/* ext components */

	import IdYear from '@svizzle/time_region_value/src/routes/[id]/[year].svelte';

	/* data */

	import types from 'app/data/types';
	import {_lookup} from 'app/stores/data';
	import {_availableYears, _selectedYear} from 'app/stores/selection';

	/* props */

	export let data;
	export let id;
	export let year;

	let availableYears;
	let title;

	/* reactive vars */

	$: $_selectedYear = Number(year);
	$: ({availableYears, title} = $_lookup[id] || {});
	$: $_availableYears = availableYears;

	// FIXME can't, `lookupStore` is now a `derived`
	// $: data && lookupStore.update(_.setPath(`${id}.data`, data));
</script>

<svelte:head>
	<title>EURITO CSVs - {title} ({year})</title>
	<meta name="description" content={`Geographic distribution (NUTS2 regions) of the indicator: ${title} (${year})`}>
</svelte:head>

<IdYear
	{data}
	{id}
	lookupStore={_lookup}
	{types}
	{year}
/>
