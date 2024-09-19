// Load Gulp and additional Gulp plugins
const gulp = require('gulp');
const concat = require('gulp-concat');
const sourcemaps = require('gulp-sourcemaps');

// Define file paths
const bootstrapJsPath = 'node_modules/bootstrap/dist/js/bootstrap.bundle.js';  // Source path for Bootstrap JavaScript files
const dragulaJsPath = 'node_modules/dragula/dist/dragula.js';                  // Source path for Dragula JavaScript file
const dragulaCssPath = 'node_modules/dragula/dist/dragula.css';                // Source path for Dragula CSS file
const sortableJsPath = 'node_modules/sortable-tree/dist/sortable-tree.js';     // Source path for sortable.js
const sortableCssPath = 'node_modules/sortable-tree/dist/sortable-tree.css';   // Source path for sortable.css
const jqueryJsPath = 'node_modules/jquery/dist/jquery.min.js'; // Source path for jQuery
const jqueryUiJsPath = 'node_modules/jquery-ui/dist/jquery-ui.min.js';    // Source path for jQuery UI
const jqueryUiCssPath = 'node_modules/jquery-ui/dist/themes/vader/jquery-ui.min.css';    // Source path for jQuery UI
const jqueryUiThemeCssPath = 'node_modules/jquery-ui/dist/themes/vader/theme.css';    // Source path for jQuery Theme UI

/*
Bootstrap
 */
gulp.task('build-js', function () {
   return gulp.src(bootstrapJsPath)          // Get Bootstrap JavaScript files
       .pipe(sourcemaps.init())              // Initialize sourcemap for these files
       .pipe(concat('bootstrap.bundle.js'))  // Concatenate them into a single bundle file
       .pipe(sourcemaps.write('.'))          // Write out the sourcemap
       .pipe(gulp.dest('src/static/js'));    // Save the resulting bundle in the 'src/static/js' directory
});


/*
Dragula
 */
// Define Gulp task to copy the Dragula JavaScript file
gulp.task('copy-dragula-js', function () {
   return gulp.src(dragulaJsPath)             // Get the Dragula JavaScript file
       .pipe(gulp.dest('src/static/js'));     // Save it in the 'src/static/js' directory
});
// Define Gulp task to copy the Dragula CSS file
gulp.task('copy-dragula-css', function () {
   return gulp.src(dragulaCssPath)            // Get the Dragula CSS file
       .pipe(gulp.dest('src/static/css'));    // Save it in the 'src/static/css' directory
});

// Define "build-dragula" task to run both "copy-dragula-js" and "copy-dragula-css" in parallel
gulp.task('build-dragula', gulp.parallel('copy-dragula-js', 'copy-dragula-css'));


/*
jQuery
 */
// Define Gulp task to copy the jQuery file
gulp.task('copy-jquery-js', function () {
   return gulp.src(jqueryJsPath)
       .pipe(gulp.dest('src/static/js/jquery'));
});
gulp.task('copy-jquery-ui-js', function () {
   return gulp.src(jqueryUiJsPath)
       .pipe(gulp.dest('src/static/js/jquery'));
});
// Define Gulp task to copy the jQuery UI file
gulp.task('copy-jquery-ui-css', function () {
   return gulp.src(jqueryUiCssPath)
       .pipe(gulp.dest('src/static/css/jquery'));
});
gulp.task('copy-jquery-ui-theme-css', function () {
   return gulp.src(jqueryUiThemeCssPath)
       .pipe(gulp.dest('src/static/css/jquery'));
});

/*
Sortable
https://marcantondahmen.github.io/sortable-tree/#getting-started
 */
gulp.task('copy-sortable-tree-js', function () {
   return gulp.src(sortableJsPath)
       .pipe(gulp.dest('src/static/js/bridge/categories'));
});
gulp.task('copy-sortable-tree-css', function () {
   return gulp.src(sortableCssPath)
       .pipe(gulp.dest('src/static/css'));
});
// Define "build-dragula" task to run both "copy-dragula-js" and "copy-dragula-css" in parallel
gulp.task('build-sortable-tree', gulp.parallel('copy-sortable-tree-js', 'copy-sortable-tree-css'));

// Define "build-jquery" task to run "copy-jquery" and "copy-jquery-ui" in parallel
gulp.task('build-jquery', gulp.parallel('copy-jquery-js', 'copy-jquery-ui-js', 'copy-jquery-ui-css', 'copy-jquery-ui-theme-css'));


/*
All together
 */
// Add jQuery to the default task
gulp.task('default', gulp.parallel('build-js', 'build-dragula'));