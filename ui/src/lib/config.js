import regionSpecs from '@svizzle/atlas/src/specs';

export const toolName = 'EURITO';
export const toolLongName = 'EURITO spatial data tool';
export const contactEmail = 'dataanalytics@nesta.org.uk';

/* navigation */

export const hrefBase = '/indicators';
export const userTestingUrl = 'https://docs.google.com/forms/d/e/1FAIpQLSfmQKIwocPmaI_Sdte0QLMhRODCYPnuYNJreehE61xDig3nAA/viewform?embedded=true';

/* flags */

export const flags = {
	showPOIs: false
}

/* regional selection */

const regionType = 'NUTS';

export const regionSettings = {
	canSelectLevels: true,
	filterableLevel: 0,
	ignoredRegions: [
		'ES7',
		'FR9',
		'FRY',
		'PT2',
		'PT3',
	],
	key: 'NUTS_ID',
	level: 0,
	level0: undefined,
	levels: regionSpecs[regionType].levels,
	objectId: 'NUTS',
	resolution: '03M',
	type: regionType,
}

/* testing */

export const urlBases = {
    development: 'http://localhost:3000',
    preview: 'https://eurito-indicators-ui-dev.netlify.app',
    // production: '',
};

export const lighthouseUrls = {
	Home: '/',
	Methodology: '/methodology',
	Guide: '/guide',
	Indicators: '/indicators',
	Trends: '/indicators/area_university_site',
	Geo: '/indicators/area_university_site/2015',
};

/*
There's a bug in Lighthouse 7.4.0 which causes the audit on the following
pages to fail when running in mobile display emulation. Commenting them
for now as tests are being run in desktop mode only pending the fix.
Ref.: https://github.com/GoogleChrome/lighthouse/issues/12039
*/
export const failingA11yAudit = [
//    'Trends',
//    'Geo'
];

export const isDev = process.env.NODE_ENV === 'development';
