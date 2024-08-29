# General


## Todo:
- [ ] Figure out universal Styling/structure
- [X] Frontend Auth
- [ ] Config file?  
        - config class
- [X] Fix up command_console
- [ ] Document all of the:
    - Endpoints
    - Relative logic
    - User Docs?
    - Other?

- [X] Clients list (need to do some server work for that one)
    /clients exists now, just need to set it up client side and parse that data now
- [X] Include JWT in requests

- [ ] CLenaup/robustify
    - [ ] consitent names to align w server (token needs to be access_token)
    - [X] getters for the config setup.
    - [X] Error handling for the config setup
    - [X] Try except EVERYWHERE possible with proper logging

- [ ] Nice to haves:
    - [ ] Dropdown/list of previously connected servers on login


- [ ] command_console
    - [X] Serverside get response endpoint working, /response/<client-id>
        this is fucking broken for some reason. cannot find the correct id/key for wahtever reason, despite it existing. wtf
    - [X] tech docs for how this exactly works
    - [X] CLEAN UP THE DAMN COMMAND_CONSOLE/refactor it. << PRIORITY
        - all old print commands + extra logging in there too, and in simple_http.py
        - nuke not needed dumb test
    - [X] get output to screen working
    - [ ] Accurate connection menu/if connected
        - server status/connection/ping 

- [ ] 401 error
    - [X]basically, if 401, use creds, re-login
        function done, haven't run itno the bug since tho. weird. its there if needed
    Add logout button too


- [ ] formj
    - [ ] Docs on key constructor/whole process
    - [ ] move key constructor to api as well if needed.
    - [ ] logging key constructor

## Structure

Each module can be a class or a set of fucntions, whatever works best. 

## Tailwind CSS Docs for ref:

https://tailwindcss.com/docs/flex
