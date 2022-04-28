# Release history

### 2.1.1
* Even better backwards compatibility (Docker image still can be supplied as object).

### 2.1.0
* Improve backwards compatibility.

### 2.0.3
* Add missing Dockerfile in MANIFEST.

### 2.0.2
* Fix type hints.

### 2.0.1
* Actually, make it compatible with previous versions 
  (at least from the `layer_name` -> `name` perspective).

### 2.0.0
* Complete code refactor.
* Change cmd line based bundling to Dockerfile based bundling.
* Deprecated `requirements.txt` functionality. The library will no longer
install dependencies if a `requirements.txt` file is found within source code.

### 1.1.3
* Retain dist-utils when bundling layer.

### 1.1.1
* Small bug fix to include parent directory only for source code.

### 1.1.0
* Add ability to include parent directory when bundling.

### 1.0.0
* Improve documentation.
* This is a fully working production-ready library.

### 0.0.2
* Add documentation.

### 0.0.1
* Initial build.
