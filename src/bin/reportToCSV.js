#!/usr/bin/env node -r esm

import path from 'path';

import * as _ from 'lamb';
import {csvFormat} from 'd3-dsv';
import {tapWith} from '@svizzle/dev';
import {readJson, saveString} from '@svizzle/file';
import {
	capitalize,
	isObjEmpty,
	isObjNotEmpty,
	makePrefixed,
	mergeObjects,
	renameKeysWith,
	transformValues
} from '@svizzle/utils';

const DATA_REL_PATH = '../../data/tests';
const REPORT_PATH = path.resolve(__dirname, DATA_REL_PATH, 'report.json');
const CSV_PATH = path.resolve(__dirname, DATA_REL_PATH, 'report.csv');

const countEmpties = _.countBy(_.pipe([_.getKey('result'), isObjEmpty]));
const processKey = key => renameKeysWith(_.pipe([
	capitalize,
	makePrefixed(key)
]))
const makeCSV = _.pipe([
	_.filterWith(isObjNotEmpty),
	_.mapWith(_.pipe([
		_.values,
		mergeObjects,
		transformValues({
			display: _.pipe([
				_.skip(['orientation']),
				processKey('display'),
			]),
			'bstack:options': processKey('options'),
			glyph: processKey('glyph'),
			text: processKey('text'),
			size: processKey('size'),
			orientation: processKey('orientation'),
		}),
		_.collect([
			_.skip(['display', 'glyph', 'text', 'size', 'orientation', 'bstack:options']),
			_.pipe([
				_.pick(['display', 'glyph', 'text', 'size', 'orientation', 'bstack:options']),
				_.values,
			])
		]),
		([skipped, objs]) => _.reduce(
			objs,
			(acc, obj) => ({...acc, ...obj}),
			skipped
		)
	])),
	csvFormat
]);

readJson(REPORT_PATH)
.then(tapWith([countEmpties, 'empty?']))
.then(tapWith([makeCSV, 'flattened']))
.then(makeCSV)
.then(saveString(CSV_PATH))
.catch(err => console.error(err))
