export const INSTITUTION = Object.freeze({
	name: "Northern New Mexico College",
	shortName: "NNMC",
	publicName: "Northern",
	city: "Espa\u00f1ola",
	state: "New Mexico",
	stateCode: "NM",
	website: "https://www.nnmc.edu/",
	logoUrl: "https://nnmc.edu/_resources/images/assets/logo.svg",
	academicsUrl: "https://www.nnmc.edu/academics/index.html",
	applyUrl: "https://apply.nnmc.edu/apply/",
	scorecardUnitId: "188058",
});

export const isNorthernNewMexicoCollege = (value = "") =>
	String(value).trim().toLowerCase() === INSTITUTION.name.toLowerCase();
