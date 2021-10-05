The goal of this respoitory is to have a skeleton app for a pingid impkementation of plotly dash

Setup for local runs
__________________________
1. Go into /environment/templates, and copy those files into the /environment directory, one folder up

password.secret      - desired plotly dash basic auth password
backend.token.secret - 

2. Fill out each template with the secret, then save.
3. Remove the extension ".template" from each secrets name

It is possible to use 0auth online for free to emulate a ping federate
This emulated federate will be active on your local run. 
For this route, there are three more steps. 
4. Read oauth0 docs on this and make an account set up for pkce simulation
5. Toggle environment boolean for using local oauth0 seen in app.py
6. Fill in the according secrets for it in /oauth0 similar to above procedure.
7. add the oauth0 domain to line 25 in env.py

You are ready to run locally and import the needed secrets now. 

Production
_________________________

The production setup first checks authentication requests against users in an azure MSSQL table, then continues to pingid auth. 

If you dont need the extra database part, you will have to 'useSQL' env variable to False. 

The codebase also logs and records app runs, outputs, and accesses in the same database. 

Assumptions/prequisites-
1. that you have a "staging" and "prod" environment in an azure sunscription.
2. that you have an azure mssql database that meets the following criteria 
-contains a table that has name "app_user"
-that this table has "schema id", "email", "role" as it columns
-with id starting at 1 and descending, email being a valid shell email, and role being "admin" or "user".
3. that you have an azure keyvault storing all of the secrets with matching names seen in env.py, instead of using local template files, and place this keyvaults name on line 38 in env.py
4. that you fill out the proper staging and prod url names obtained by IT in lines 51 and 54 for the needed production environments, ie staging and/or prod. 