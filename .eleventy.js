/** @param {import("@11ty/eleventy").UserConfig} eleventyConfig */
module.exports = function (eleventyConfig) {
  eleventyConfig.addFilter("escapeJsonString", (value) => {
    if (value == null) return "";
    return String(value)
      .replace(/\\/g, "\\\\")
      .replace(/"/g, '\\"')
      .replace(/\r?\n|\r/g, " ");
  });

  eleventyConfig.addPassthroughCopy("src/styles.css");
  eleventyConfig.addPassthroughCopy("src/strange-house.css");
  eleventyConfig.addPassthroughCopy("src/CNAME");
  eleventyConfig.addPassthroughCopy("src/assets/backgrounds");
  eleventyConfig.addPassthroughCopy("src/assets/strange-house");
  eleventyConfig.addPassthroughCopy("src/assets/icons");
  eleventyConfig.addPassthroughCopy("src/assets/fonts/fusion-pixel-12px-proportional-latin.woff2");
  eleventyConfig.addPassthroughCopy("src/assets/fonts/Unutterable-Regular-subset.woff2");
  eleventyConfig.addPassthroughCopy("src/assets/fonts/FUSION-PIXEL-OFL.txt");
  eleventyConfig.addPassthroughCopy("src/assets/fonts/unutterable-subset-chars.txt");
  eleventyConfig.addPassthroughCopy("src/yandex_c0360f7b611be04f.html");
  eleventyConfig.addPassthroughCopy("src/favicon.svg");

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data",
    },
  };
};
