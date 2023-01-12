#!/usr/bin/env node -r esm

import path from 'node:path';
import {fileURLToPath} from 'node:url';

// import unifiedNuts from '@svizzle/atlas/data/dist/NUTS/unifiedNuts.json' assert { type: "json" };
import {tapMessage} from '@svizzle/dev';
import {isCsvFile, readDir, readFile, readJson, saveObjPassthrough} from '@svizzle/file';
import {parseCSV} from '@svizzle/time_region_value';
import {getObjSize} from '@svizzle/utils';
import cpy from 'cpy';
import del from 'del';
import * as _ from 'lamb';
import mkdirp from 'mkdirp';
import rimraf from 'rimraf';
import tempy from 'tempy';
import {zip} from 'zip-a-folder';

import {basename} from '../lib/utils/assets.js';

/* paths */
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname, '../../../');

const UNIFIED_NUTS = path.resolve(
	ROOT_DIR,
	'node_modules/@svizzle/atlas/data/dist/NUTS/unifiedNuts.json'
);

// ds/
const DS_DIR = path.resolve(ROOT_DIR, 'ds');
const DS_PROCESSED_DIR = path.resolve(DS_DIR, 'outputs/data/processed');

// ui/
const UI_DIR = path.resolve(ROOT_DIR, 'ui');
const UI_STATIC_DATA_DIR = path.resolve(UI_DIR, 'static/data');
const UI_STATS_DIR = path.resolve(UI_DIR, 'stats');
const UI_STATS_UNSUPPORTED_NUTS_PATH =
	path.resolve(UI_STATS_DIR, 'unsupportedRegions.json');

/* data */
const unifiedNuts = await readJson(UNIFIED_NUTS);

/* initialise the stats dir */

rimraf.sync(UI_STATS_DIR);
mkdirp.sync(UI_STATS_DIR);

/* utils */

const isDir = name => !name.startsWith('.') && path.parse(name).ext === '';
const makePath = dirName => filename => path.resolve(
	DS_PROCESSED_DIR,
	dirName,
	filename
);

const getIdFromFilepath = filepath => path.parse(filepath).name;

/*
To test this, in 1+ indicators CSVs, edit `region_id` in 1+ rows to something
not supported (e.g. `AT` -> `XX`) and run the `copydata` npm script
*/
const checkIndicators = csvFilepaths =>
	Promise.all(
		_.map(csvFilepaths, csvFilepath => {
			const id = getIdFromFilepath(csvFilepath);
			const localCsvPath = path.relative(ROOT_DIR, csvFilepath);

			return readFile(csvFilepath, 'utf-8')
			.then(parseCSV(id))
			.then(_.mapWith(_.setKey('localCsvPath', localCsvPath)))
		})
	)
	.then(_.pipe([
		_.flatten,
		_.groupBy(({region_year_spec, region_id, region_level}) =>
			`${region_year_spec}-${region_id}-${region_level}`
		),
		_.pairs,
		_.filterWith(([key]) => {
			const isUnknownNutsRegion = _.isUndefined(
				_.find(unifiedNuts, ({NUTS_ID, level, year}) => {
					const regionKey = `${year}-${NUTS_ID}-${level}`;

						return key === regionKey;
				})
			);

			return isUnknownNutsRegion;
		}),
		_.flatMapWith(_.getAt(1)),
		_.groupBy(_.getKey('localCsvPath')),
		_.mapValuesWith(_.mapWith(_.skip(['localCsvPath'])))
	]))
	.then(saveObjPassthrough(UI_STATS_UNSUPPORTED_NUTS_PATH, 2))
	.then(stats => {
		const size = getObjSize(stats);

		if (size > 0) {
			const pluralWord = size > 1 ? 's' : '';
			const pluralVerb = size > 1 ? '' : 's';

			console.log(`🤚🤚🤚: ${size} indicator${pluralWord} use${pluralVerb} \
unsupported NUTS regions: see ${UI_STATS_UNSUPPORTED_NUTS_PATH}`
			);

		}
	});

/* run */

const run = async () => {

	/* delete the data dir */

	await del([UI_STATIC_DATA_DIR]);

	/* collect indicator paths */

	// FIXME use a proper walker
	const dirNames = await readDir(DS_PROCESSED_DIR).then(_.filterWith(isDir));
	const csvFilepaths = await Promise.all(
		_.map(dirNames, dirName =>
			readDir(path.resolve(DS_PROCESSED_DIR, dirName))
			.then(_.pipe([
				_.filterWith(_.allOf([isCsvFile])),
				_.mapWith(makePath(dirName))
			]))
		)
	)
	.then(_.flatten);

	/* check indicators */

	await checkIndicators(csvFilepaths);

	/* copy the indicator files */

	await cpy(csvFilepaths, UI_STATIC_DATA_DIR);

	/* zip them all & copy the zip to static/ */

	const tmpZipPath = tempy.file({name: `${basename}.zip`});
	await zip(UI_STATIC_DATA_DIR, tmpZipPath);
	await cpy(tmpZipPath, UI_STATIC_DATA_DIR);
}

run().then(tapMessage(`Updated data in ${UI_STATIC_DATA_DIR}`));
