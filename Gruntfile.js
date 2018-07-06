module.exports = function(grunt) {
    
    // Project configuration
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        less: {
            development: {
                options: {
                    paths: 'app/less',
                    dumpLineNumbers: "all",
                },
                files : {
                    'app/static/css/styles.css': 'app/less/styles.less'
                }
            }
        }, 
        watch: {
            less: {
                tasks: ['less'],
                files: ['app/less/styles.less', 'app/less/auth/*.less',
                        'app/less/main/*.less', 'app/less/admin/*.less'],
                options: {
                    spawn: true,
                    reload: true
                }
            },
            css: {
                files: ['app/static/css/*'],
                options: {
                    livereload: 1337
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-watch')
};
