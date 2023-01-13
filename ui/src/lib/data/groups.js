// FIXME not great importing from a stores/ file
import {
	getYearExtent,
	makeIndicatorsLookup
} from '@svizzle/time_region_value';
import {inclusiveRange} from '@svizzle/utils';

import groups from './indicatorsGroups.json';

export const lookup = makeIndicatorsLookup(groups);
export const yearExtent = getYearExtent(groups);
export const yearRange = inclusiveRange(yearExtent);
