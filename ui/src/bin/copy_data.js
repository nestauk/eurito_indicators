#!/usr/bin/env node -r esm

import path from 'path';

import {tapMessage} from '@svizzle/dev';
import {isCsvFile, readDir} from '@svizzle/file';
import cpy from 'cpy';
import del from 'del';
import * as _ from 'lamb';
import tempy from 'tempy';
import {zip} from 'zip-a-folder';

import {basename} from 'app/utils/assets';

const DS_DATA_REL_PATH = '../../../ds/outputs/data';
const DATA_DIR = path.resolve(__dirname, DS_DATA_REL_PATH, 'processed');
const DATA_DIR_STATIC = path.resolve(__dirname, '../../static/data');

const isDir = name => !name.startsWith('.') && path.parse(name).ext === '';
const makePath = dirName => filename => path.resolve(
	DATA_DIR,
	dirName,
	filename
);

const run = async () => {

	/* delete the data dir */

	await del([DATA_DIR_STATIC]);

	/* copy the indicator files */

	// FIXME use a proper walker
	const dirNames = await readDir(DATA_DIR).then(_.filterWith(isDir));
	const csvFilepaths = await Promise.all(
		_.map(dirNames, dirName =>
			readDir(path.resolve(DATA_DIR, dirName))
			.then(_.pipe([
				_.filterWith(_.allOf([isCsvFile])),
				_.mapWith(makePath(dirName))
			]))
		)
	)
	.then(_.flatten);

	await cpy(csvFilepaths, DATA_DIR_STATIC);

	/* zip them all & copy the zip to static/ */

	const tmpZipPath = tempy.file({name: `${basename}.zip`});
	await zip(DATA_DIR_STATIC, tmpZipPath);
	await cpy(tmpZipPath, DATA_DIR_STATIC);
}

run().then(tapMessage(`Updated data in ${DATA_DIR_STATIC}`));
