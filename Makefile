HTML_FILES:= $(wildcard doc/*.html)

clean:
	find -name "*.pyc" -type f -delete
	find -name "__pycache__" -type d -delete
	-rm -f "README.html"
	-rm -f "$(HTML_FILES)"

%.html : %.md
	markdown $< > $@

DOC_FILES_TO_BE_GEN:= $(patsubst %.md,%.html,$(wildcard doc/*.md))

docs: $(DOC_FILES_TO_BE_GEN) README.html
