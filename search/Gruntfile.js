// custom search following the guide https://gist.github.com/sebz/efddfc8fdcb6b480f567
// grunt lunr-index

var toml = require("toml");
var S = require("string");

var CONTENT_PATH_PREFIX = "../generated/content";
let INDEX_DEST_FILE = "../generated/static/js/lunr/PagesIndex.json";

module.exports = function(grunt) {

    grunt.registerTask("lunr-index", function() {

        grunt.log.writeln("Build pages index");

        var indexPages = function() {
            var pagesIndex = [];
            grunt.file.recurse(CONTENT_PATH_PREFIX, function(abspath, rootdir, subdir, filename) {
                grunt.verbose.writeln("Parse file:",abspath);
                pagesIndex.push(processFile(abspath, filename));
            });

            return pagesIndex;
        };

        var processFile = function(abspath, filename) {
            var pageIndex;

            if (S(filename).endsWith(".html")) {
                pageIndex = processHTMLFile(abspath, filename);
            } else {
                pageIndex = processMDFile(abspath, filename);
            }

            return pageIndex;
        };

        var processHTMLFile = function(abspath, filename) {
            var content = grunt.file.read(abspath);
            var pageName = S(filename).chompRight(".html").s;
            var href = S(abspath)
                .chompLeft(CONTENT_PATH_PREFIX).s;
            return {
                title: pageName,
                href: href,
                content: S(content).trim().stripTags().stripPunctuation().s
            };
        };

        var processMDFile = function(abspath, filename) {
            grunt.log.writeln("see md file " + filename);
            var content = grunt.file.read(abspath);
            
            // First separate the Front Matter from the content and parse it
            let parts = content.split("---");
            let body = "";
            let title = "unprocessed";
            if (parts.length == 3) {
                let frontMatters = parts[1].trim().split("\n");
                for (let f in frontMatters) {
                    if (frontMatters[f].startsWith("title: ")) {
                        title = frontMatters[f].split(":")[1].trim();
                    }
                    break;
                }
                body = parts[2];
            } else {
                body = content;
            }

            var href = S(abspath).chompLeft(CONTENT_PATH_PREFIX).chompRight(".md").s;
            // href for index.md files stops at the folder name
            if (filename === "index.md") {
                href = S(abspath).chompLeft(CONTENT_PATH_PREFIX).chompRight(filename).s;
            }

            // Build Lunr index for this page
            return {
                title: title,
                // tags: tags,
                href: href,
                content: S(body).trim().stripTags().stripPunctuation().s
            };
        };

        grunt.file.write(INDEX_DEST_FILE, JSON.stringify(indexPages()));
        grunt.log.ok("Index built");
    });
};
