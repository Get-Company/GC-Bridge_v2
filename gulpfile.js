// Run gulp by gulp build-js

const gulp = require('gulp');
const concat = require('gulp-concat');
const sourcemaps = require('gulp-sourcemaps');
// const browserify = require('gulp-browserify');

// Definieren der Quellpfade für Bootstrap-JavaScript-Dateien
const bootstrapJsPath = 'node_modules/bootstrap/dist/js/bootstrap.bundle.js';

gulp.task('build-js', function(){
   return gulp.src(bootstrapJsPath)  // Pfad zu Bootstrap-JavaScript-Dateien
       .pipe(sourcemaps.init())  // Initialisiert die Erstellung der Source-Map
       .pipe(concat('bootstrap.bundle.js'))  // Kombinieren in eine Datei namens bootstrap.js
       // .pipe(browserify())  // Optional: Verwenden Sie Browserify für Modulbündelung, wenn benötigt
       .pipe(sourcemaps.write('.'))  // Schreibt die Source-Map in dieselbe Quelle wie das Zielverzeichnis
       .pipe(gulp.dest('src/static/js'));  // Zielverzeichnis
});

// Optional: Erstellen Sie eine Watch-Aufgabe, um Änderungen automatisch zu kompilieren
gulp.task('watch', function(){
   gulp.watch(bootstrapJsPath, gulp.series('build-js'));
});

// Optional: Definieren Sie eine Standardaufgabe, die beim Aufruf von "gulp" ausgeführt wird
gulp.task('default', gulp.series('build-js', 'watch'));

