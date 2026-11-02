.PHONY: build serve check clean
build:
	python3 -I build.py
serve: build
	python3 -I -m http.server 8000 --directory public
check: build
	python3 -I scripts/check-links.py public
clean:
	rm -rf public
