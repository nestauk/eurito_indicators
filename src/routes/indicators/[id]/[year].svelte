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
	import {lookupStore} from 'app/stores/data';
	import {availableYearsStore, selectedYearStore} from 'app/stores/selection';

	/* props */

	export let data;
	export let id;
	export let year;

	/* reactive vars */

	$: $selectedYearStore = Number(year);
	$: ({availableYears, title} = $lookupStore[id] || {});
	$: $availableYearsStore = availableYears;

	// FIXME can't, `lookupStore` is now a `derived`
	// $: data && lookupStore.update(_.setPath(`${id}.data`, data));
</script>

<svelte:head>
	<title>EURITO CSVs - {title} ({year})</title>
</svelte:head>

<IdYear
	{data}
	{id}
	{lookupStore}
	{types}
	{year}
/>
