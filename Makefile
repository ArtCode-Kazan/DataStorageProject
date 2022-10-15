
get-coverage:
	coverage run -m pytest
	coverage report -m
	coverage html
	cd htmlcov && open -a "Google Chrome" index.html
