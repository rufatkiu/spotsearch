module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      dist: {
        files: {
          'js/etheme.min.js': ['js/etheme.js']
        }
      }
    },
    jshint: {
      files: ['gruntfile.js', 'js/etheme.js'],
      options: {
        reporterOutput: "",
        // options here to override JSHint defaults
        globals: {
          jQuery: true,
          console: true,
          module: true,
          document: true
        }
      }
    },
    less: {
        development: {
            options: {
                paths: ["less/etheme"]
                //banner: '/*! less/etheme/oscar.css | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n'
            },
            files: {
              "css/etheme.css": "less/etheme/etheme.less",
              "css/etheme-dark.css": "less/etheme/etheme-dark.less"
            }
        },
        production: {
            options: {
                paths: ["less/etheme"],
                //banner: '/*! less/etheme/oscar.css | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n',
                cleancss: true
            },
            files: {
              "css/etheme.min.css": "less/etheme/etheme.less",
              "css/etheme-dark.min.css": "less/etheme/etheme-dark.less"
            }
        },
        /*
        // built with ./manage.sh styles
        bootstrap: {
            options: {
                paths: ["less/bootstrap"],
                cleancss: true
            },
            files: {"css/bootstrap.min.css": "less/bootstrap/bootstrap.less"}
        },
        */
    },
    watch: {
        scripts: {
            files: ['<%= jshint.files %>'],
            tasks: ['jshint', 'uglify']
        },
        etheme_styles: {
            files: ['less/etheme/**/*.less'],
            tasks: ['less:development', 'less:production']
        },
        bootstrap_styles: {
            files: ['less/bootstrap/**/*.less'],
            tasks: ['less:bootstrap']
        }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-less');

  grunt.registerTask('test', ['jshint']);

  grunt.registerTask('default', ['jshint', 'uglify', 'less']);

  grunt.registerTask('styles', ['less']);

};
