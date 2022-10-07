// FIXME not great importing from a stores/ file
import {
	getYearExtent,
	makeIndicatorsLookup
} from '@svizzle/time_region_value/src/lib/stores/dataset';
import {inclusiveRange} from '@svizzle/utils';
import {derived, readable} from 'svelte/store';

import groups from '$lib/data/indicatorsGroups.json';

export const _groups = readable(groups);
export const _lookup = derived(_groups, makeIndicatorsLookup);
export const _yearExtent = derived(_groups, getYearExtent);
export const _yearRange = derived(_yearExtent, inclusiveRange);

// TODO `_lookup` should derive from fetched data too
// so that we cache results as we did before:
// $: data && lookupStore.update(_.setPath(`${id}.data`, data));
