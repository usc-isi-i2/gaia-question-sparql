#GAIA QA

#### installation:
* `git clone` the repo
* run `cd gaia-question-sparql`
* run `pip install -r requirements.txt` to install dependencies
OR run 
  ```
    conda env create -f environment.yml
    source activate gaia_qa_env
  ```
#### unittests: 
`python -W ignore -m unittest discover`

#### deactive from conda env:
`source deactivate`



