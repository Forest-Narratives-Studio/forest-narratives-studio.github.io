const LANGS = ["ru", "en"];

/** @typedef {{
 *  key: string,
 *  namespace: string,
 *  slugs: { ru: string, en: string },
 *  pageLdType?: string,
 *  bodyClass?: string,
 *  pageStyles?: string[],
 *  pageScripts?: string[],
 *  pageImage?: string,
 *  twitterCard?: string,
 *  disableSky?: boolean,
 * }} ProjectDef */

/** @type {ProjectDef[]} */
const list = [
  {
    key: "strangeHouse",
    namespace: "strangeHouse",
    slugs: { ru: "chuzhoy-dom", en: "strange-house" },
    pageLdType: "videoGame",
    bodyClass: "fns-house-theme",
    pageStyles: ["/strange-house.css"],
    pageImage: "/assets/strange-house/og-strange-house.webp",
    twitterCard: "summary_large_image",
    disableSky: true,
  },
  {
    key: "voluntaryConsent",
    namespace: "voluntaryConsent",
    slugs: { ru: "dobrovolnoe-soglasie", en: "voluntary-consent" },
    pageLdType: "videoGame",
    bodyClass: "fns-vc-theme",
    pageStyles: ["/voluntary-consent.css"],
    pageScripts: ["/voluntary-consent.js"],
    pageImage: "/assets/voluntary-consent/og-voluntary-consent.webp",
    twitterCard: "summary_large_image",
    disableSky: true,
  },
  {
    key: "lastWarmDay",
    namespace: "lastWarmDay",
    slugs: { ru: "posledniy-teplyy-den", en: "last-warm-day" },
  },
  {
    key: "forestEngine",
    namespace: "forestEngine",
    slugs: { ru: "forest-engine", en: "forest-engine" },
  },
];

/**
 * @param {ProjectDef} project
 * @param {string} lang
 */
function canonPath(project, lang) {
  return `/${lang}/${project.slugs[lang]}/`;
}

/**
 * @param {ProjectDef} project
 * @param {string} lang
 */
function hubPath(project, lang) {
  return `/${project.slugs[lang]}/`;
}

const byKey = Object.fromEntries(list.map((project) => [project.key, project]));

const hubs = list.flatMap((project) => {
  /** @type {Map<string, string>} */
  const slugLangs = new Map();
  for (const lang of LANGS) {
    const slug = project.slugs[lang];
    if (!slugLangs.has(slug)) slugLangs.set(slug, lang);
  }
  return [...slugLangs.entries()].map(([slug, lang]) => ({
    permalink: `/${slug}/`,
    lang,
    key: project.key,
    namespace: project.namespace,
    canonicalPath: canonPath(project, lang),
    ruPath: canonPath(project, "ru"),
    enPath: canonPath(project, "en"),
    xDefaultPath: canonPath(project, "en"),
    redirectRu: canonPath(project, "ru"),
    redirectEn: canonPath(project, "en"),
    pageLdType: project.pageLdType,
    bodyClass: project.bodyClass,
    pageStyles: project.pageStyles,
    pageScripts: project.pageScripts,
    pageImage: project.pageImage,
    twitterCard: project.twitterCard,
    disableSky: project.disableSky,
  }));
});

const aliases = list.flatMap((project) =>
  LANGS.flatMap((lang) =>
    LANGS.filter((other) => other !== lang && project.slugs[other] !== project.slugs[lang]).map(
      (other) => ({
        permalink: `/${lang}/${project.slugs[other]}/`,
        lang,
        key: project.key,
        namespace: project.namespace,
        targetPath: canonPath(project, lang),
        canonicalPath: canonPath(project, lang),
        ruPath: canonPath(project, "ru"),
        enPath: canonPath(project, "en"),
        xDefaultPath: canonPath(project, "en"),
      })
    )
  )
);

module.exports = {
  list,
  byKey,
  hubs,
  aliases,
  canonPath,
  hubPath,
};
