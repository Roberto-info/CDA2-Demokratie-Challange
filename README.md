# CDA2 Democracy Challange

This Repo contains the notebooks to visualize and document our
learnings and findings about the data we'd like to analyze

To work with this repo properly install poetry
https://python-poetry.org/docs/

or with brew: 
brew install poetry 

or with pip
pip install poetry

To set the directory of the venv
- poetry config virtualenvs.in-project true     

Then you are able to initialize:
- poetry init 
- poetry install

To use poetry with the notebooks use:
-  poetry add ipykernel 

To set poetry to be the kernel use:
- poetry run python -m ipykernel install --user --name=poetry-env --display-name "Python (Poetry)"