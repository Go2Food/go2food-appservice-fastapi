# How to run

## Mongodb setup
* You can run the database locally or using a cluster
* The configurations is controlled in the subfolder config/connections.py

## Attention
* Before running anything, please change the .env to suit your database setup
* After the .env file is appropriately changed, cd to the main directory of the repository, then:

### Use python 3.10+ to run
```
    # create a virtual environment specifically called fastmongo
    > python -m venv fastmongo

    # activating venv in windows
    > fastmongo\Scripts\Activate

    # install requirements
    > pip install -r requirements.txt

    # run development server
    > uvicorn main:app --reload

    # open the docs to test api calls
    > click the link presented in the console

    # append /docs to the url
    > test individual methods that you created on that webpage
```

## Pushing instructions
* Please create a new branch to avoid clutters in the main development branch
* before pushing dont forget to remove the tracking of the .env file so that if somebody has different configs it would not interfere with their work
```
    # use this command before pushing to remove the tracking on .env
    > git rm .env --cached
```
