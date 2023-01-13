import {version} from './version.js';

export const extraDownloadIds = [];
export const basename = `eurito_${version.replace(/\./ug, '_')}`;
export const allNUTS2IndicatorsCsvName = `${basename}.NUTS2.csv`;
export const zipUrl = `/data/${basename}.zip`;
