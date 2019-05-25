# Sauce Bot
![Sauce Bot](static/saucebot.png)
#### Description
This program is intended to scrape the UCLA Dining Halls menu daily and determine if selected food items are available in the dining halls. Users can add or remove food items.
#### User Commands
The bot is activated by messaging "!sauce bot \[command\]". Some example commands are given below
- **info** lists a brief description of what saucebot can do
- **list** returns a list of all food items that are being tracked
- **today** gives all of the items in their respective dining halls that are available today
- **add \[food item\]** or **track \[food item\]** adds a new item to be tracked. If the item hasn't been seen before, it cannot be added. If an item doesn't exactly match with found items, suggestions will be provided
- **remove \[food item\]** takes an item off the list to be checked

#### Instructions
Saucebot is a Flask webapp, intended for hosting on Google Cloud Platform with a PostgreSQL database.
To set this up, create an [App Engine instance on Google Cloud](https://cloud.google.com/appengine/docs/standard/python3/).
In addition, you need to set up PostgreSQL, either on [Google Cloud](https://cloud.google.com/sql/docs/postgres/) or on some other database host.
Once that is done, you need to modify `app.yaml` to set the environment variables like follows
```yaml
env_variables:
  DB_USER: "username"
  DB_PASSWORD: "password"
  DB_NAME: "database name"
  PSQL_CLOUD_INSTANCE: "project:region:database"
```

To set up the database, [connect to the database](https://cloud.google.com/sql/docs/postgres/connect-admin-proxy) and
run the file `sql/setup.sql`. This will initialize the database to allow the server to properly function.

In addition, you need to [create a GroupMe bot](https://dev.groupme.com/tutorials/bots). Insert that bot
and associated group id into the database with the command
```postgresql
INSERT INTO dining.groups (group_id, bot_id) 
VALUES ('group id here', 'bot id here');
```

Finally, you will need to set up an admin or cron user to run daily tasks. This can be done with the query
```postgresql
INSERT INTO auth.users (username, permission)
VALUES ('username', 'admin');
```
This will create a user with a UUID that can be found using the query
```postgresql
SELECT token FROM auth.users WHERE username = 'whatever username you entered';
```

Then configure your cron.yaml file for Google Cloud to be in the following format
```yaml
cron:
- description: "scrape webpages"
  url: /internal/scrape/generate_new_menu_data?token=UUID of a user with cron or admin privileges
  schedule: every day 05:00
  timezone: US/Pacific

- description: "clear cached queries"
  url: /internal/db/clear_cache?token=UUID of a user with cron or admin privileges
  schedule: every 1 hours

- description: "send daily messages to subscribing groups"
  url: /internal/notify/today?token=UUID of a user with cron or admin privileges
  schedule: every day 06:00
  timezone: US/Pacific
```

This will ensure the proper scraping and notifications take place


#### Contributing
If you want to contribute to Sauce Bot, you can check out some of the projects to do, or just submit your own code. Also, please report any issues you experience on the GitHub issues tab

**Copyright Robert Geil 2019**