import regionSpecs from '@svizzle/atlas/src/specs';
import allBboxes from '@svizzle/atlas/data/dist/NUTS/allBboxes.js';
import overseaIdsGroups from '@svizzle/atlas/data/dist/NUTS/overseaIdsGroups.js';
import {getFamilies} from "@svizzle/ui/src/drivers/fonts/utils";
import * as _ from 'lamb';

export const toolName = 'EURITO';
export const toolLongName = 'EURITO spatial data tool';
export const contactEmail = 'dataanalytics@nesta.org.uk';
export const changelogUrl = 'https://github.com/nestauk/eurito_indicators/blob/staging/CHANGELOG.md';
export const jsonUrl = '/data/ai_map_annotated_orgs.json';

/* banners */

export const bannersDefaultFooterText = 'Click on background to dismiss';

/* navigation */

export const hrefBase = '/indicators';

// source: https://docs.google.com/forms/d/1on1rtyk9HncAz8usBZLIMkPywh5A2Q5Yj4M8ZnHMaBM/edit
export const surveyFormUrl = 'https://docs.google.com/forms/d/e/1FAIpQLSfmQKIwocPmaI_Sdte0QLMhRODCYPnuYNJreehE61xDig3nAA/viewform?embedded=true';

/* flags */

export const flags = {
	showPOIs: false
}

/* regional selection */

const regionType = 'NUTS';
const {levels, years} = regionSpecs[regionType];
const [rootLevel] = levels;
const {unified: {mainland: maxBbox}} = allBboxes;

export const regionSettings = {
	atlasBase: '/atlas',
	canSelectLevels: true,
	filterableLevel: 0,
	key: 'NUTS_ID',
	initialLevel: rootLevel,
	levels,
	maxBbox,
	processing: {
		// clip at level 0 (e.g. France - French Guyane)
		clipIds: _.pluckFrom(overseaIdsGroups, 'rootId'), // or []

		// exclude at levels 1-3 (e.g. French Guyane)
		excludeIds: _.flatMap(overseaIdsGroups, _.getKey('descendantIds')), // or []
	},
	objectId: 'NUTS',
	resolution: '10M',
	rootIds: undefined, // all roots
	type: regionType,
	years,
}
export const LOGOS = {
	themeLight: {
		nesta: '/logos/Nesta-light.svg',
	},
	themeDark: {
		nesta: '/logos/Nesta-dark.svg',
	}
}

/* testing */

export const urlBases = {
	development: 'http://localhost:5173',
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

export const fontsInfo = [
	{
		family: 'Avenir Next Variable',
		faces: [
			{
				src: 'url(/font/AvenirNext/Variable.ttf) format("truetype")'
			}
		]
	},
	{
		family: 'Archivo',
		faces: [
			{
				src: 'url(/font/Archivo/VariableFont_wdth,wght.ttf) format("truetype")',
				descriptors: {
					style: 'normal'
				}
			},
			{
				src: 'url(/font/Archivo/Italic-VariableFont_wdth,wght.ttf) format("truetype")',
				descriptors: {
					style: 'italic'
				}
			},
		]
	},
	{
		family: 'Noboto Flex',
		faces: [
			{
				src: 'url(/font/NobotoFlex/Variable.woff2)',
				descriptors: {
					weight: 140
				}
			}
		]
	},
	{
		family: 'Courier New'
	},
	{
		family: 'Open Dyslexia',
		faces: [
			{
				src: 'url(/font/OpenDyslexic/Regular.otf) format("opentype")',
				descriptors: {
					weight: 400,
					style: 'normal'
				}
			},
			{
				src: 'url(/font/OpenDyslexic/Italic.otf) format("opentype")',
				descriptors: {
					weight: 400,
					style: 'italic'
				}
			},
			{
				src: 'url(/font/OpenDyslexic/Bold.otf) format("opentype")',
				descriptors: {
					weight: 700,
					style: 'normal'
				}
			},
			{
				src: 'url(/font/OpenDyslexic/BoldItalic.otf) format("opentype")',
				descriptors: {
					weight: 700,
					style: 'italic'
				}
			}
		]
	}
];

export const a11yFontFamilies = getFamilies(fontsInfo);
