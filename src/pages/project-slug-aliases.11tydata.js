module.exports = {
  eleventyComputed: {
    lang: (data) => data.alias && data.alias.lang,
    canonicalPath: (data) => data.alias && data.alias.canonicalPath,
    ruPath: (data) => data.alias && data.alias.ruPath,
    enPath: (data) => data.alias && data.alias.enPath,
    xDefaultPath: (data) => data.alias && data.alias.xDefaultPath,
    pageTitle: (data) => {
      const lang = data.alias && data.alias.lang;
      const stub = lang && data.i18n && data.i18n[lang] && data.i18n[lang].redirectStub;
      return stub && stub.meta && stub.meta.title;
    },
    pageDescription: (data) => {
      const lang = data.alias && data.alias.lang;
      const stub = lang && data.i18n && data.i18n[lang] && data.i18n[lang].redirectStub;
      return stub && stub.meta && stub.meta.description;
    },
  },
};
