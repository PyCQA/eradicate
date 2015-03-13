check:
	pep8 eradicate eradicate.py setup.py
	pep257 eradicate eradicate.py setup.py
	pylint \
		--reports=no \
		--disable=bad-continuation \
		--disable=invalid-name \
		--disable=too-many-return-statements \
		--rcfile=/dev/null \
		eradicate.py setup.py
	python setup.py --long-description | rstcheck -
	scspell eradicate eradicate.py setup.py test_eradicate.py README.rst

coverage:
	@rm -f .coverage
	@coverage run test_eradicate.py
	@coverage report
	@coverage html
	@rm -f .coverage
	@python -m webbrowser -n "file://${PWD}/htmlcov/index.html"

mutant:
	@mut.py --disable-operator RIL -t eradicate -u test_eradicate -mc

readme:
	@restview --long-description --strict
