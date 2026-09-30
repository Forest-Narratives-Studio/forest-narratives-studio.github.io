module.exports = {
  eleventyComputed: {
    lang: (data) => data.hub && data.hub.lang,
    pageI18nNamespace: (data) => data.hub && data.hub.namespace,
    canonicalPath: (data) => data.hub && data.hub.canonicalPath,
    ruPath: (data) => data.hub && data.hub.ruPath,
    enPath: (data) => data.hub && data.hub.enPath,
    xDefaultPath: (data) => data.hub && data.hub.xDefaultPath,
    pageLdType: (data) => data.hub && data.hub.pageLdType,
    bodyClass: (data) => data.hub && data.hub.bodyClass,
    pageStyles: (data) => data.hub && data.hub.pageStyles,
    pageImage: (data) => data.hub && data.hub.pageImage,
    twitterCard: (data) => data.hub && data.hub.twitterCard,
    disableSky: (data) => data.hub && data.hub.disableSky,
  },
};
